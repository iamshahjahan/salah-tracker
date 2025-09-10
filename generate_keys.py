#!/usr/bin/env python3
"""
Generate configuration keys for SalahReminders
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    return secrets.token_hex(length)

def generate_jwt_secret(length=32):
    """Generate a JWT secret key"""
    return secrets.token_hex(length)

def generate_random_string(length=16):
    """Generate a random string for passwords"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

if __name__ == "__main__":
    print("🔑 SalahReminders Configuration Keys Generator")
    print("=" * 50)
    
    print("\n1. SECRET_KEY (for Flask sessions):")
    secret_key = generate_secret_key()
    print(f"SECRET_KEY={secret_key}")
    
    print("\n2. JWT_SECRET_KEY (for authentication tokens):")
    jwt_secret = generate_jwt_secret()
    print(f"JWT_SECRET_KEY={jwt_secret}")
    
    print("\n3. Database URL (already configured):")
    print("DATABASE_URL=mysql+mysqlconnector://root:khankhan@localhost/salah_reminders")
    
    print("\n4. Email Configuration (optional):")
    print("MAIL_SERVER=smtp.gmail.com")
    print("MAIL_PORT=587")
    print("MAIL_USE_TLS=True")
    print("MAIL_USERNAME=your-email@gmail.com")
    print("MAIL_PASSWORD=your-app-password")
    
    print("\n5. Prayer Times API (no key needed):")
    print("PRAYER_TIMES_API_KEY=not-required")
    
    print("\n" + "=" * 50)
    print("📝 Copy these values to your .env file")
    print("💡 The app works without email configuration")
    print("🌍 Don't forget to set your location in the app!")
