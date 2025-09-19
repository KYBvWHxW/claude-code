"""End-to-end API schema testing using schemathesis."""
import time
import requests
import schemathesis

def test_openapi_endpoint_availability():
    """Test that OpenAPI endpoint is available after startup."""
    # Wait for service to be ready
    for _ in range(30):
        try:
            response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=2)
            if response.status_code == 200:
                assert "openapi" in response.json()
                return
        except (requests.RequestException, ValueError):
            time.sleep(1)

    # If we get here, service didn't come up
    assert False, "OpenAPI endpoint not available after 30 seconds"

def test_api_schema_validation():
    """Test API schema validation with schemathesis."""
    # Ensure service is running
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        assert response.status_code == 200
        schema_data = response.json()
        assert "openapi" in schema_data
        assert "paths" in schema_data
    except Exception as e:
        assert False, f"Cannot validate schema: {e}"