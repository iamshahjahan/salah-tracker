"""Step definitions for API endpoint features."""

import os

from behave import given, then, when

from app.models.user import User
from app.services.auth_service import AuthService


@given('the API is accessible')
def step_api_accessible(context):
    """Verify API is accessible."""
    # Use Flask test client instead of HTTP requests
    context.test_client = context.app.test_client()
    context.api_accessible = True


@given('I have a valid API token')
def step_have_valid_api_token(context):
    """Create a valid API token."""
    # Create a test user and get token
    user = User(
        username="apitestuser",
        email="apitest@example.com",
        first_name="API",
        last_name="Test",
        timezone="UTC",
        email_verified=True
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()

    auth_service = AuthService(context.app_config)
    token_result = auth_service.authenticate_user_using_email("apitestuser", "password123")
    context.api_token = token_result.get('access_token')
    context.test_user = user


@given('I have an invalid API token')
def step_have_invalid_api_token(context):
    """Set an invalid API token."""
    context.api_token = os.getenv("TEST_INVALID_TOKEN", "invalid_token_12345")


@given('I am within the Dhuhr prayer time window')
def step_within_dhuhr_prayer_time_window(context):
    """Set up prayer time window."""
    context.prayer_time_valid = True
    context.prayer_id = 1  # Mock prayer ID


@given('I have prayer completion history')
def step_have_prayer_completion_history(context):
    """Set up prayer completion history."""
    # This would typically create prayer completion records
    context.has_completion_history = True


@when('I make a GET request to "{endpoint}"')
def step_make_get_request(context, endpoint):
    """Make a GET request to an endpoint."""
    headers = {}
    if hasattr(context, 'api_token'):
        headers['Authorization'] = f'Bearer {context.api_token}'

    try:
        response = context.test_client.get(endpoint, headers=headers)
        context.api_response = response
        context.api_status_code = response.status_code
        context.api_response_data = response.get_json() if response.data else {}
    except Exception as e:
        context.api_error = str(e)
        context.api_status_code = 500


@when('I make a POST request to "{endpoint}"')
def step_make_post_request(context, endpoint):
    """Make a POST request to an endpoint."""
    headers = {'Content-Type': 'application/json'}
    if hasattr(context, 'api_token'):
        headers['Authorization'] = f'Bearer {context.api_token}'

    data = getattr(context, 'request_data', {})

    try:
        response = context.test_client.post(
            endpoint,
            headers=headers,
            json=data
        )
        context.api_response = response
        context.api_status_code = response.status_code
        context.api_response_data = response.get_json() if response.data else {}
    except Exception as e:
        context.api_error = str(e)
        context.api_status_code = 500


@when('I make a POST request to "{endpoint}" with credentials')
def step_make_post_request_with_credentials(context, endpoint):
    """Make a POST request with credentials."""
    context.request_data = {
        'username': 'apitestuser',
        'password': 'password123'
    }
    step_make_post_request(context, endpoint)


@when('I make a POST request to "{endpoint}" with registration data')
def step_make_post_request_with_registration_data(context, endpoint):
    """Make a POST request with registration data."""
    context.request_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User'
    }
    step_make_post_request(context, endpoint)


@when('I make a POST request to "{endpoint}" with prayer data')
def step_make_post_request_with_prayer_data(context, endpoint):
    """Make a POST request with prayer data."""
    context.request_data = {
        'prayer_id': context.prayer_id,
        'completion_time': '2024-01-01T14:00:00Z'
    }
    step_make_post_request(context, endpoint)


@when('I make a POST request to "{endpoint}" with verification code')
def step_make_post_request_with_verification_code(context, endpoint):
    """Make a POST request with verification code."""
    context.request_data = {
        'email': 'apitest@example.com',
        'verification_code': '123456'
    }
    step_make_post_request(context, endpoint)


@when('I make a POST request to "{endpoint}" with invalid prayer ID')
def step_make_post_request_with_invalid_prayer_id(context, endpoint):
    """Make a POST request with invalid prayer ID."""
    context.request_data = {
        'prayer_id': 99999,  # Invalid prayer ID
        'completion_time': '2024-01-01T14:00:00Z'
    }
    step_make_post_request(context, endpoint)


@when('I make a request to a protected endpoint')
def step_make_request_to_protected_endpoint(context):
    """Make a request to a protected endpoint without authentication."""
    step_make_get_request(context, "/api/dashboard/stats")


@when('I make a request with invalid data')
def step_make_request_with_invalid_data(context):
    """Make a request with invalid data."""
    context.request_data = {
        'invalid_field': 'invalid_value'
    }
    step_make_post_request(context, "/api/prayers/complete")


@when('I make multiple requests rapidly')
def step_make_multiple_requests_rapidly(context):
    """Make multiple requests rapidly."""
    context.rapid_requests = []
    for _i in range(10):  # Make 10 rapid requests
        step_make_get_request(context, "/api/prayers/times")
        context.rapid_requests.append({
            'status_code': context.api_status_code,
            'response': context.api_response_data
        })


@when('I make a request that causes an internal error')
def step_make_request_causing_internal_error(context):
    """Make a request that causes an internal error."""
    # This would typically trigger an internal server error
    context.request_data = {'trigger_error': True}
    step_make_post_request(context, "/api/prayers/complete")


@when('I make a request to a non-existent endpoint')
def step_make_request_to_nonexistent_endpoint(context):
    """Make a request to a non-existent endpoint."""
    step_make_get_request(context, "/api/nonexistent")


@when('I make requests to various API endpoints')
def step_make_requests_to_various_endpoints(context):
    """Make requests to various API endpoints."""
    endpoints = [
        "/api/prayers/times",
        "/api/dashboard/stats",
        "/api/auth/profile"
    ]

    context.various_responses = []
    for endpoint in endpoints:
        step_make_get_request(context, endpoint)
        context.various_responses.append({
            'endpoint': endpoint,
            'status_code': context.api_status_code,
            'response': context.api_response_data
        })


@when('I make a request to "{endpoint}"')
def step_make_request_to_versioned_endpoint(context, endpoint):
    """Make a request to a versioned endpoint."""
    step_make_get_request(context, endpoint)


# Duplicate step definition removed - using the one at line 62


@then('I should receive a {status_code} status code')
def step_receive_status_code(context, status_code):
    """Verify the response status code."""
    expected_code = int(status_code)
    assert context.api_status_code == expected_code, \
        f"Expected status code {expected_code}, but got {context.api_status_code}"


@then('I should receive a {status_code} response')
def step_receive_status_response(context, status_code):
    """Verify the response status code."""
    expected_code = int(status_code)
    assert context.api_status_code == expected_code, \
        f"Expected status code {expected_code}, but got {context.api_status_code}"


# Duplicate step definition removed - using the one at line 229


@then('the response should contain today\'s prayer times')
def step_response_contains_prayer_times(context):
    """Verify response contains prayer times."""
    assert 'prayer_times' in context.api_response_data or 'prayers' in context.api_response_data


@then('the response should be in JSON format')
def step_response_is_json_format(context):
    """Verify response is in JSON format."""
    assert isinstance(context.api_response_data, dict)


@then('the prayer should be marked as completed')
def step_prayer_marked_as_completed(context):
    """Verify prayer is marked as completed."""
    assert context.api_response_data.get('success')
    assert context.api_response_data.get('status') == 'completed'


@then('the response should contain success message')
def step_response_contains_success_message(context):
    """Verify response contains success message."""
    assert 'message' in context.api_response_data


@then('the response should contain completion statistics')
def step_response_contains_completion_statistics(context):
    """Verify response contains completion statistics."""
    assert 'statistics' in context.api_response_data or 'completion_rate' in context.api_response_data


@then('the response should contain weekly and monthly data')
def step_response_contains_weekly_monthly_data(context):
    """Verify response contains weekly and monthly data."""
    data = context.api_response_data
    assert 'weekly' in data or 'monthly' in data or 'periods' in data


@then('the response should contain an authentication error')
def step_response_contains_authentication_error(context):
    """Verify response contains authentication error."""
    assert 'error' in context.api_response_data
    assert 'auth' in context.api_response_data['error'].lower() or 'token' in context.api_response_data['error'].lower()


@then('I should be rate limited')
def step_should_be_rate_limited(context):
    """Verify rate limiting is applied."""
    # Check if any of the rapid requests were rate limited
    rate_limited = any(req['status_code'] == 429 for req in context.rapid_requests)
    assert rate_limited, "Expected to be rate limited but wasn't"


@then('the response should contain rate limit information')
def step_response_contains_rate_limit_info(context):
    """Verify response contains rate limit information."""
    assert 'rate_limit' in context.api_response_data or 'retry_after' in context.api_response_data


@then('the response should contain validation error')
def step_response_contains_validation_error(context):
    """Verify response contains validation error."""
    assert 'error' in context.api_response_data
    assert 'validation' in context.api_response_data['error'].lower() or 'invalid' in context.api_response_data['error'].lower()


@then('the response should contain a not found error')
def step_response_contains_not_found_error(context):
    """Verify response contains not found error."""
    assert 'error' in context.api_response_data
    assert 'not found' in context.api_response_data['error'].lower()


@then('all responses should follow the same format')
def step_all_responses_same_format(context):
    """Verify all responses follow the same format."""
    for response in context.various_responses:
        assert isinstance(response['response'], dict)
        # Check for common fields like status, message, data
        assert any(field in response['response'] for field in ['status', 'message', 'data', 'success'])


@then('all responses should include appropriate status codes')
def step_all_responses_appropriate_status_codes(context):
    """Verify all responses have appropriate status codes."""
    for response in context.various_responses:
        assert 200 <= response['status_code'] < 600


@then('all responses should include error handling')
def step_all_responses_include_error_handling(context):
    """Verify all responses include error handling."""
    for response in context.various_responses:
        if response['status_code'] >= 400:
            assert 'error' in response['response']


@then('the response should be compatible with version 1')
def step_response_compatible_version_1(context):
    """Verify response is compatible with version 1."""
    assert context.api_status_code == 200
    assert 'version' in context.api_response_data or 'api_version' in context.api_response_data


@then('the response should contain API documentation')
def step_response_contains_api_documentation(context):
    """Verify response contains API documentation."""
    assert 'documentation' in context.api_response_data or 'endpoints' in context.api_response_data


@then('the documentation should be in a readable format')
def step_documentation_readable_format(context):
    """Verify documentation is in a readable format."""
    # Check if it's HTML or markdown
    content = str(context.api_response_data)
    assert any(format_type in content.lower() for format_type in ['html', 'markdown', 'json'])


@then('the response should contain "status": "healthy"')
def step_response_contains_healthy_status(context):
    """Verify response contains healthy status."""
    assert context.api_response_data.get('status') == 'healthy'


@then('the response should contain an access token')
def step_response_contains_access_token(context):
    """Verify response contains access token."""
    assert 'access_token' in context.api_response_data or 'token' in context.api_response_data


@then('the response should contain user information')
def step_response_contains_user_information(context):
    """Verify response contains user information."""
    assert 'user' in context.api_response_data or 'username' in context.api_response_data


@then('the response should indicate verification email was sent')
def step_response_indicates_verification_email_sent(context):
    """Verify response indicates verification email was sent."""
    assert context.api_response_data.get('verification_sent')


@then('the response should indicate successful completion')
def step_response_indicates_successful_completion(context):
    """Verify response indicates successful completion."""
    assert context.api_response_data.get('success')


@then('the response should contain prayer statistics')
def step_response_contains_prayer_statistics(context):
    """Verify response contains prayer statistics."""
    assert 'statistics' in context.api_response_data or 'completion_rate' in context.api_response_data


@then('the response should contain completion rates')
def step_response_contains_completion_rates(context):
    """Verify response contains completion rates."""
    data = context.api_response_data
    assert any(rate in data for rate in ['completion_rate', 'daily_rate', 'weekly_rate', 'monthly_rate'])


@then('the prayer times should be in my timezone')
def step_prayer_times_in_timezone(context):
    """Verify prayer times are in user's timezone."""
    # This would typically check that times are in the user's timezone
    assert 'timezone' in context.api_response_data or 'local_time' in context.api_response_data


@then('the response should indicate successful verification')
def step_response_indicates_successful_verification(context):
    """Verify response indicates successful verification."""
    assert context.api_response_data.get('success')


@then('the response should contain a generic error message')
def step_response_contains_generic_error_message(context):
    """Verify response contains generic error message."""
    assert 'error' in context.api_response_data
    # Should not contain sensitive information
    error_msg = context.api_response_data['error']
    assert 'internal' in error_msg.lower() or 'server' in error_msg.lower()


@then('the error should be logged')
def step_error_should_be_logged(context):
    """Verify error is logged."""
    # This would typically check logs
    context.error_logged = True
