def test_openapi_exists():
    """Test that openapi.yaml exists"""
    import os
    assert os.path.exists("openapi.yaml"), "openapi.yaml file should exist"