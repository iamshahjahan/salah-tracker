from flask import Flask, request, jsonify, render_template
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_mail import Message
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
import pytz
from database import db
from mail_config import mail

# Load environment variables
load_dotenv()

# Set up logging
from logging_config import setup_logging, get_logger
setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration
from app.config.settings import get_config
config = get_config()

app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONFIG.url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = config.JWT_CONFIG.secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Add external API config to Flask config
app.config['EXTERNAL_API_CONFIG'] = config.EXTERNAL_API_CONFIG
app.config['PRAYER_TIME_WINDOW_MINUTES'] = config.PRAYER_TIME_WINDOW_MINUTES

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
mail.init_app(app)
CORS(app)

logger.info("Flask application initialized successfully")

# Import routes
from app.routes import auth_bp, prayer_bp, dashboard_bp, social_bp
from app.routes.family_groups import family_groups_bp
from app.routes.notifications import notifications_bp
from app.routes.inspirational import inspirational_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(prayer_bp, url_prefix='/api/prayers')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(social_bp, url_prefix='/api/social')
app.register_blueprint(family_groups_bp, url_prefix='/api/family-groups')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(inspirational_bp, url_prefix='/api/inspirational')

@app.route('/')
def home():
    return render_template('index.html')

# Prayer completion routes (without API prefix for email links)
@app.route('/complete-prayer/<completion_link_id>', methods=['GET'])
def show_complete_prayer_page(completion_link_id):
    """Show prayer completion confirmation page."""
    try:
        from app.models.prayer_notification import PrayerNotification
        from app.models.user import User
        
        # Find the notification
        notification = PrayerNotification.query.filter_by(completion_link_id=completion_link_id).first()
        
        if not notification:
            return render_template('prayer_completion_error.html', 
                                 error="Invalid or expired completion link"), 404
        
        # Check if already completed
        if notification.completed_via_link:
            return render_template('prayer_completion_success.html', 
                                 message="Prayer already completed!", 
                                 prayer_type=notification.prayer_type,
                                 completed_at=notification.completed_at)
        
        # Check if link is expired (2 hours after creation)
        from datetime import datetime, timedelta
        if notification.created_at and datetime.utcnow() > notification.created_at + timedelta(hours=2):
            return render_template('prayer_completion_error.html', 
                                 error="This completion link has expired"), 400
        
        # Get user info
        user = User.query.get(notification.user_id)
        
        return render_template('prayer_completion.html', 
                             completion_link_id=completion_link_id,
                             prayer_type=notification.prayer_type,
                             prayer_date=notification.prayer_date,
                             user_name=user.first_name or user.username)
        
    except Exception as e:
        return render_template('prayer_completion_error.html', 
                             error="An error occurred processing your request"), 500

@app.route('/complete-prayer/<completion_link_id>', methods=['POST'])
def complete_prayer_via_link(completion_link_id):
    """Mark a prayer as completed via completion link."""
    try:
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        result = notification_service.mark_prayer_completed_via_link(completion_link_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
