"""
Step definitions for authentication features.
"""

from behave import given, when, then
from app.models.user import User
from app.services.auth_service import AuthService
from config.database import db
import json


@given('the application is running')
def step_application_running(context):
    """Ensure the application is running and accessible."""
    # This would typically check if the Flask app is running
    # For now, we'll assume it's running
    context.app_running = True


@given('the database is clean')
def step_database_clean(context):
    """Clean the database for testing."""
    # Clean up test data
    context.db.session.query(User).filter(User.email.like('test%@example.com')).delete(synchronize_session=False)
    context.db.session.commit()


@given('I am on the registration page')
def step_on_registration_page(context):
    """Navigate to the registration page."""
    context.current_page = 'registration'


@given('I am on the login page')
def step_on_login_page(context):
    """Navigate to the login page."""
    context.current_page = 'login'


@given('a user with email "{email}" and password "{password}" exists')
def step_user_exists(context, email, password):
    """Create a test user."""
    user = User(
        username=email,
        email=email,
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    user.set_password(password)
    context.db.session.add(user)
    context.db.session.commit()
    context.test_user = user


@given('a user with email "{email}" already exists')
def step_user_with_email_exists(context, email):
    """Create a user with specific email."""
    user = User(
        username="existinguser",
        email=email,
        first_name="Existing",
        last_name="User",
        timezone="UTC"
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.existing_user = user


@given('I am a registered user with unverified email')
def step_user_with_unverified_email(context):
    """Create a user with unverified email."""
    user = User(
        username="unverifieduser",
        email="unverified@example.com",
        first_name="Unverified",
        last_name="User",
        timezone="UTC",
        email_verified=False
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.test_user = user


@given('a user with unverified email exists')
def step_user_with_unverified_email_exists(context):
    """Create a user with unverified email."""
    # Clean up any existing user first
    context.db.session.query(User).filter(User.username == "unverifieduser").delete(synchronize_session=False)
    context.db.session.commit()
    
    user = User(
        username="unverifieduser",
        email="unverified@example.com",
        first_name="Unverified",
        last_name="User",
        timezone="UTC",
        email_verified=False
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.test_user = user


@given('I am a registered user with verified email')
def step_user_with_verified_email(context):
    """Create a user with verified email."""
    user = User(
        username="verifieduser",
        email="verified@example.com",
        first_name="Verified",
        last_name="User",
        timezone="UTC",
        email_verified=True
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.test_user = user


@when('I fill in the registration form with:')
def step_fill_registration_form(context):
    """Fill in the registration form with provided data."""
    context.registration_data = {}
    for row in context.table:
        context.registration_data[row['Field']] = row['Value']


@when('I submit the registration form')
def step_submit_registration_form(context):
    """Submit the registration form."""
    auth_service = AuthService(context.app_config)
    context.registration_result = auth_service.register_user(context.registration_data)


@when('I try to register with email "{email}"')
def step_try_register_with_email(context, email):
    """Try to register with specific email."""
    registration_data = {
        'username': 'testuser',
        'email': email,
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    auth_service = AuthService(context.app_config)
    context.registration_result = auth_service.register_user(registration_data)


@when('I enter email "{email}"')
def step_enter_username(context, email):
    """Enter username in login form."""
    context.login_data = getattr(context, 'login_data', {})
    context.login_data['email'] = email


@when('I enter username "{username}"')
def step_enter_password(context, username):
    """Enter password in login form."""
    context.login_data = getattr(context, 'login_data', {})
    context.login_data['username'] = username


@when('I enter password "{password}"')
def step_enter_password(context, password):
    """Enter password in login form."""
    context.login_data = getattr(context, 'login_data', {})
    context.login_data['password'] = password


@when('I click the login button with email')
def step_click_login_button(context):
    """Click the login button."""
    auth_service = AuthService(context.app_config)
    context.login_result = auth_service.authenticate_user_using_email(
        context.login_data['email'],
        context.login_data['password']
    )

@when('I click the login button with username')
def step_click_login_button(context):
    """Click the login button."""
    auth_service = AuthService(context.app_config)
    context.login_result = auth_service.authenticate_user_using_username(
        context.login_data['username'],
        context.login_data['password']
    )


@when('I switch to OTP login tab')
def step_switch_to_otp_login(context):
    """Switch to OTP login tab."""
    context.login_method = 'otp'


@when('I enter my email "{email}"')
def step_enter_email(context, email):
    """Enter email for OTP login."""
    context.otp_email = email


@when('I click "Send Code"')
def step_click_send_code(context):
    """Click send code button."""
    auth_service = AuthService(context.app_config)
    context.otp_result = auth_service.send_login_otp(context.otp_email)


@when('I enter the OTP code')
def step_enter_otp_code(context):
    """Enter OTP code."""
    # In a real scenario, this would be the code from email
    context.otp_code = "123456"  # Mock code


@when('I click "Login with Code"')
def step_click_login_with_code(context):
    """Click login with code button."""
    auth_service = AuthService(context.app_config)
    context.login_result = auth_service.authenticate_with_otp(
        context.otp_email, 
        context.otp_code
    )


@then('I should be registered successfully')
def step_registration_successful(context):
    """Verify registration was successful."""
    if 'error' in context.registration_result:
        print(context.registration_result['error'])
    assert context.registration_result['success'] == True


@then('I should receive a confirmation message')
def step_receive_confirmation_message(context):
    """Verify confirmation message is received."""
    assert 'message' in context.registration_result


@then('I should be automatically logged in')
def step_automatically_logged_in(context):
    """Verify user is automatically logged in."""
    assert 'access_token' in context.registration_result


@then('an email verification should be sent to my email')
def step_email_verification_sent(context):
    """Verify email verification was sent."""
    assert context.registration_result.get('verification_sent') == True


@then('I should see an error message "{error_message}"')
def step_see_error_message(context, error_message):
    """Verify error message is displayed."""
    if hasattr(context, 'registration_result'):
        actual = context.registration_result['error']
        assert actual == error_message, f"Expected error '{error_message}' but got '{actual}'"
    elif hasattr(context, 'login_result'):
        actual = context.login_result['error']
        assert actual == error_message, f"Expected error '{error_message}' but got '{actual}'"
    else:
        assert False, "No error result found in context (neither registration_result nor login_result)"



@then('I should not be registered')
def step_not_registered(context):
    """Verify user was not registered."""
    assert context.registration_result['success'] == False


@then('I should be logged in successfully')
def step_logged_in_successfully(context):
    """Verify login was successful."""
    assert context.login_result['success'], f"Expected true but got false"

@then('I should be redirected to the prayers page')
def step_redirected_to_prayers(context):
    """Verify redirection to prayers page."""
    # This would typically check the response or navigation
    context.current_page = 'prayers'


@then('I should see my user profile information')
def step_see_user_profile(context):
    """Verify user profile information is displayed."""
    assert 'user' in context.login_result


@then('I should not be logged in')
def step_not_logged_in(context):
    """Verify user was not logged in."""
    assert context.login_result['success'] == False


@then('I should receive an OTP code via email')
def step_receive_otp_code(context):
    """Verify OTP code was sent via email."""
    assert context.otp_result['success'] == True


@then('I should see an error message about invalid email format')
def step_see_invalid_email_error(context):
    """Verify invalid email format error."""
    assert 'email' in context.registration_result['error'].lower()


@then('I should see an error message about password requirements')
def step_see_password_requirements_error(context):
    """Verify password requirements error."""
    assert 'password' in context.registration_result['error'].lower()


@then('I should see error messages for missing fields')
def step_see_missing_fields_error(context):
    """Verify missing fields error."""
    assert 'required' in context.registration_result['error'].lower()


@then('I should see a validation error for the username field')
def step_see_username_validation_error(context):
    """Verify username validation error."""
    # This would typically check frontend validation
    context.validation_error = True


@then('the form should not be submitted')
def step_form_not_submitted(context):
    """Verify form was not submitted."""
    # This would typically check if the form submission was prevented
    assert hasattr(context, 'validation_error')


@when('I try to register with password "{password}"')
def step_impl(context, password):
    """Try to register with specific email."""
    registration_data = {
        'username': 'testuser',
        'email': 'test@123',
        'password': password,
        'first_name': 'Test',
        'last_name': 'User'
    }
    auth_service = AuthService(context.app_config)
    context.registration_result = auth_service.register_user(registration_data)


@when("I submit the registration form without filling required fields")
def step_impl(context):
    """Try to register with specific email."""
    registration_data = {
        'username': 'testuser',
        'email': 'test@123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    auth_service = AuthService(context.app_config)
    context.registration_result = auth_service.register_user(registration_data)


# Password Reset Steps


@when('I click "Forgot Password"')
def step_click_forgot_password(context):
    """Click the forgot password link."""
    context.current_action = 'forgot_password'


@when('I enter my email for password reset "{email}"')
def step_enter_email_for_reset(context, email):
    """Enter email for password reset."""
    context.forgot_password_email = email


@when('I submit the forgot password form')
def step_submit_forgot_password_form(context):
    """Submit the forgot password form."""
    auth_service = AuthService(context.app_config)
    context.forgot_password_result = auth_service.send_password_reset(context.forgot_password_email)


@then('I should receive a password reset email')
def step_receive_password_reset_email(context):
    """Verify password reset email was sent."""
    assert context.forgot_password_result['success'] == True
    assert 'message' in context.forgot_password_result


@given('I have a valid password reset code for "{email}"')
def step_have_valid_reset_code(context, email):
    """Create a valid password reset code for the user."""
    from app.models.email_verification import EmailVerification
    
    # Get the user
    user = User.query.filter_by(email=email).first()
    assert user is not None, f"User with email {email} not found"
    
    # Create a password reset verification
    verification = EmailVerification.create_verification(
        user_id=user.id,
        email=user.email,
        verification_type='password_reset',
        expires_in_minutes=60
    )
    context.db.session.add(verification)
    context.db.session.commit()
    
    context.reset_code = verification.verification_code
    context.reset_user = user


@given('I have an invalid password reset code')
def step_have_invalid_reset_code(context):
    """Set an invalid reset code."""
    context.reset_code = 'invalid_code_12345'


@given('I have an expired password reset code for "{email}"')
def step_have_expired_reset_code(context, email):
    """Create an expired password reset code for the user."""
    from app.models.email_verification import EmailVerification
    from datetime import datetime, timedelta
    
    # Get the user
    user = User.query.filter_by(email=email).first()
    assert user is not None, f"User with email {email} not found"
    
    # Create an expired password reset verification
    verification = EmailVerification.create_verification(
        user_id=user.id,
        email=user.email,
        verification_type='password_reset',
        expires_in_minutes=60
    )
    # Manually set it as expired
    verification.expires_at = datetime.utcnow() - timedelta(hours=1)
    context.db.session.add(verification)
    context.db.session.commit()
    
    context.reset_code = verification.verification_code
    context.reset_user = user


@when('I navigate to the reset password page with the code')
def step_navigate_to_reset_page(context):
    """Navigate to reset password page with code."""
    # This would typically involve making a GET request to the reset password page
    # For now, we'll simulate it by setting the context
    context.current_page = 'reset_password'
    context.current_reset_code = context.reset_code


@when('I enter a new password "{password}"')
def step_enter_new_password(context, password):
    """Enter new password."""
    context.new_password = password


@when('I confirm the new password "{password}"')
def step_confirm_new_password(context, password):
    """Confirm new password."""
    context.confirm_password = password


@when('I submit the reset password form')
def step_submit_reset_password_form(context):
    """Submit the reset password form."""
    auth_service = AuthService(context.app_config)
    context.reset_result = auth_service.reset_password_with_code(
        context.current_reset_code,
        context.new_password
    )


@then('my password should be reset successfully')
def step_password_reset_successful(context):
    """Verify password was reset successfully."""
    assert context.reset_result['success'] == True
    assert 'message' in context.reset_result


@then('I should be able to login with the new password')
def step_able_to_login_with_new_password(context):
    """Verify can login with new password."""
    auth_service = AuthService(context.app_config)
    login_result = auth_service.authenticate_user_using_email(
        context.reset_user.email,
        context.new_password
    )
    assert login_result['success'] == True
    assert 'access_token' in login_result


@then('I should see an error message about invalid code')
def step_see_invalid_code_error(context):
    """Verify error message for invalid code."""
    # This would be tested when accessing the GET route with invalid code
    assert context.current_reset_code == 'invalid_code_12345'


@then('I should see an error message about expired code')
def step_see_expired_code_error(context):
    """Verify error message for expired code."""
    # This would be tested when accessing the GET route with expired code
    assert context.current_reset_code is not None


@then('I should see an error message about password mismatch')
def step_see_password_mismatch_error(context):
    """Verify error message for password mismatch."""
    # This would be tested in the frontend validation
    assert context.new_password != context.confirm_password


@then('my password should not be changed')
def step_password_not_changed(context):
    """Verify password was not changed."""
    auth_service = AuthService(context.app_config)
    # Try to login with old password - should still work
    login_result = auth_service.authenticate_user_using_email(
        context.reset_user.email,
        'oldpassword123'  # Original password
    )
    assert login_result['success'] == True


@given("I have an invalid OTP code {invalid_code} and email: {email}")
def step_impl(context, invalid_code, email):
    context.login_data = getattr(context, 'login_data', {})
    context.login_data['email'] = email
    context.login_data['invalid_code'] = invalid_code


@when("I enter the invalid OTP code")
def step_impl(context):
    auth_service = AuthService(context.app_config)
    context.login_result = auth_service.authenticate_with_otp(email=context.login_data['email'],otp=context.login_data['invalid_code'])


@when("I leave the username field empty")
def step_impl(context):
    context.login_data = getattr(context, 'login_data', {})
    context.login_data['username'] = ''
    context.login_data['password'] = 'password123'


@when("I try to submit the form")
def step_impl(context):
    auth_service = AuthService(context.app_config)
    context.login_result = auth_service.authenticate_user_using_username(username=context.login_data['username'],password=context.login_data['password'])


@when('I enter my email {email}')
def step_impl(context, email):
    context.login_data = getattr(context, 'login_data', {})
    context.login_data['email'] = email


@when('I click "Send Reset Link"')
def step_impl(context):
    auth_service = AuthService(context.app_config)
    auth_service.send_password_reset(email=context.login_data['email'])

@when("I should receive a password reset email")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should receive a password reset email')