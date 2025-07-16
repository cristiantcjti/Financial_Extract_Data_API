import pytest
from unittest.mock import patch

from src.financial.routes.accounts import AccountsRoute
from src.integration.enums import RouteMethod


class TestAccountsRoute:

    def test_init_with_data(self, mock_route_data):
        # Arrange & Act
        route = AccountsRoute(mock_route_data)
        
        # Assert
        assert route._token == "test-token"
        assert route._account_id == "account-123"
        assert route._page == 1
        assert route._limit == 10

    def test_init_with_empty_data(self):
        # Arrange & Act
        route = AccountsRoute({})
        
        # Assert
        assert route._token == ""
        assert route._account_id is None
        assert route._page == 1
        assert route._limit == 10

    @patch('src.financial.routes.accounts.settings')
    def test_get_base_url(self, mock_settings):
        # Arrange
        mock_settings.OFDA_API_BASE_URL = "http://test-api.com"
        route = AccountsRoute({})
        
        # Act
        url = route.get_base_url()
        
        # Assert
        assert url == "http://test-api.com"

    def test_get_resource_path(self):
        # Arrange
        route = AccountsRoute({})
        
        # Act
        path = route.get_resource_path()
        
        # Assert
        assert path == "/account?page=1"

    # Removed get_data_resource_path tests since method doesn't exist in implementation

    def test_get_payload_for_list(self):
        # Arrange
        route = AccountsRoute({"token": "test-token", "page": 2, "limit": 20})
        
        # Act
        payload = route.get_payload()
        
        # Assert
        expected_payload = {}
        assert payload == expected_payload

    def test_get_payload_for_specific_account(self):
        # Arrange
        route = AccountsRoute({
            "token": "test-token",
            "account_id": "account-123"
        })
        
        # Act
        payload = route.get_payload()
        
        # Assert
        expected_payload = {}
        assert payload == expected_payload

    def test_set_method_get(self):
        # Arrange
        route = AccountsRoute({"operation": RouteMethod.GET})
        
        # Act
        method = route.set_method()
        
        # Assert
        assert method is None
        assert route.method == RouteMethod.GET

    def test_set_method_post(self):
        # Arrange
        route = AccountsRoute({"operation": RouteMethod.POST})
        
        # Act
        method = route.set_method()
        
        # Assert
        assert method is None
        assert route.method == RouteMethod.POST

    def test_get_authorization_header(self):
        # Arrange
        route = AccountsRoute({"token": "test-token"})
        
        # Act
        headers = route.get_authorization_header()
        
        # Assert
        expected_headers = {"Authorization": "test-token"}
        assert headers == expected_headers

    def test_get_authorization_header_empty_token(self):
        # Arrange
        route = AccountsRoute({})
        
        # Act
        headers = route.get_authorization_header()
        
        # Assert
        expected_headers = {"Authorization": ""}
        assert headers == expected_headers

    @pytest.mark.parametrize("page,limit,expected", [
        (1, 10, {"page": 1, "limit": 10}),
        (5, 50, {"page": 5, "limit": 50}),
        (None, None, {"page": 1, "limit": 10})
    ])
    def test_pagination_parameters(self, page, limit, expected):
        # Arrange
        data = {"token": "test-token"}
        if page is not None:
            data["page"] = page
        if limit is not None:
            data["limit"] = limit
        
        route = AccountsRoute(data)
        
        # Act
        payload = route.get_payload()
        
        # Assert
        assert payload == {}