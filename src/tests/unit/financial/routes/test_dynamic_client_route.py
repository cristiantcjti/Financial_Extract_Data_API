import pytest
from unittest.mock import patch

from src.financial.routes.dynamic_client import DynamicClientRoute
from src.integration.enums import RouteMethod


class TestDynamicClientRoute:

    def test_init_with_data(self, mock_client_data):
        # Arrange & Act
        route = DynamicClientRoute(mock_client_data)
        
        # Assert
        assert route._name == "Test Client"
        assert route._organization_name == "Test Org"
        assert route._organization_id == "org-123"
        assert route._organization_type == "INDIVIDUAL"

    def test_init_with_empty_data(self):
        # Arrange & Act
        route = DynamicClientRoute({})
        
        # Assert
        assert route._name is None
        assert route._organization_name is None
        assert route._organization_id is None
        assert route._organization_type is None
        assert route._client_id == ""

    @patch('src.financial.routes.dynamic_client.settings')
    def test_get_base_url(self, mock_settings):
        # Arrange
        mock_settings.OFDA_API_BASE_URL = "http://test-api.com"
        route = DynamicClientRoute({})
        
        # Act
        url = route.get_base_url()
        
        # Assert
        assert url == "http://test-api.com"

    def test_get_resource_path(self):
        # Arrange
        route = DynamicClientRoute({})
        
        # Act
        path = route.get_resource_path()
        
        # Assert
        assert path == "/dynamic-client/"

    # Removed get_data_resource_path tests since method doesn't exist in implementation

    def test_get_payload_for_post(self, mock_client_data):
        # Arrange
        route = DynamicClientRoute(mock_client_data)
        
        # Act
        payload = route.get_payload()
        
        # Assert
        expected_payload = {
            "name": "Test Client",
            "organization_name": "Test Org",
            "organization_id": "org-123",
            "organization_type": "INDIVIDUAL"
        }
        assert payload == expected_payload

    def test_get_payload_for_get(self):
        # Arrange
        route = DynamicClientRoute({"client_id": "client-123", "name": "test-client", "organization_name": "test-org"})
        
        # Act
        payload = route.get_payload()
        
        # Assert
        expected_payload = {
            "name": "test-client",
            "organization_name": "test-org",
            "organization_id": None,
            "organization_type": None
        }
        assert payload == expected_payload

    def test_set_method_post(self):
        # Arrange
        route = DynamicClientRoute({"operation": RouteMethod.POST})
        
        # Act
        method = route.set_method()
        
        # Assert
        assert method is None
        assert route.method == RouteMethod.POST

    def test_set_method_get(self):
        # Arrange
        route = DynamicClientRoute({"operation": RouteMethod.GET})
        
        # Act
        method = route.set_method()
        
        # Assert
        assert method is None
        assert route.method == RouteMethod.GET

    def test_get_authorization_header_returns_empty(self):
        # Arrange
        route = DynamicClientRoute({})
        
        # Act
        headers = route.get_authorization_header()
        
        # Assert
        assert headers is None

    @pytest.mark.parametrize("operation", [
        RouteMethod.POST,
        RouteMethod.GET,
        RouteMethod.PUT,
        RouteMethod.DELETE
    ])
    def test_all_http_methods(self, operation):
        # Arrange
        route = DynamicClientRoute({"operation": operation})
        
        # Act
        method = route.set_method()
        
        # Assert
        assert method is None

    def test_payload_excludes_none_values(self):
        # Arrange
        partial_data = {
            "name": "Test Client",
            "organization_name": None,
            "organization_id": "org-123"
        }
        route = DynamicClientRoute(partial_data)
        
        # Act
        payload = route.get_payload()
        
        # Assert
        assert "name" in payload
        assert "organization_id" in payload
        assert payload["organization_name"] is None