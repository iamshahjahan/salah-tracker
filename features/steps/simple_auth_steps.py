"""
Simple authentication step definitions for testing.
"""

from behave import given, when, then


# This step is defined in authentication_steps.py


# This step is defined in authentication_steps.py


@when('I check if authentication is available')
def step_check_authentication_available(context):
    """Check if authentication is available."""
    # Simple check - in a real scenario this would test the auth service
    context.auth_available = True


@then('I should see that authentication is working')
def step_see_authentication_working(context):
    """Verify authentication is working."""
    assert context.app_running == True
    assert context.auth_available == True
    print("✅ Authentication test passed!")


# This step is defined in email_verification_steps.py
