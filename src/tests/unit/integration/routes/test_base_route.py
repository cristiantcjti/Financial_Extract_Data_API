import pytest
from unittest.mock import Mock, patch
import requests

from src.integration.routes.base import BaseRoute
from src.integration.enums import RouteMethod
from src.integration.dtos.integration_dtos import IntegrationResultDTO


class TestableRoute(BaseRoute):
    def __init__(self):
        super().__init__()
        self.test_url = "http://test-api.com"
        self.test_path = "/test/"
        self.test_payload = {"test": "data"}

    def get_base_url(self):
        return self.test_url

    def get_resource_path(self):
        return self.test_path

    def get_data_resource_path(self):
        return self.test_path

    def get_payload(self):
        return self.test_payload

    def set_method(self):
        self.method = RouteMethod.GET
        return self.method


class TestBaseRoute:

    @pytest.fixture
    def route(self):
        return TestableRoute()

    @pytest.fixture
    def mock_response(self):
        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"success": True}
        return response

    def test_integrate_success(self, route, mock_response):
        # Arrange
        with patch('requests.get', return_value=mock_response):
            
            # Act
            result = route.integrate()
            
            # Assert
            assert isinstance(result, IntegrationResultDTO)
            assert result.success is True
            assert result.response == mock_response

    def test_integrate_failure(self, route):
        # Arrange
        error_response = Mock()
        error_response.ok = False
        error_response.status_code = 400
        
        with patch('requests.get', return_value=error_response):
            
            # Act
            result = route.integrate()
            
            # Assert
            assert isinstance(result, IntegrationResultDTO)
            assert result.success is False
            assert result.response == error_response

    def test_execute_post(self, route, mock_response):
        # Arrange
        with patch('requests.post', return_value=mock_response) as mock_post:
            
            # Act
            response = route.execute_post()
            
            # Assert
            assert response == mock_response
            mock_post.assert_called_once()

    def test_execute_put(self, route, mock_response):
        # Arrange
        with patch('requests.put', return_value=mock_response) as mock_put:
            
            # Act
            response = route.execute_put()
            
            # Assert
            assert response == mock_response
            mock_put.assert_called_once()

    def test_execute_delete(self, route, mock_response):
        # Arrange
        with patch('requests.delete', return_value=mock_response) as mock_delete:
            
            # Act
            response = route.execute_delete()
            
            # Assert
            assert response == mock_response
            mock_delete.assert_called_once()

    def test_execute_request_with_headers(self, route, mock_response):
        # Arrange
        route.get_authorization_header = Mock(return_value={"Authorization": "Bearer token"})
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            
            # Act
            route.execute_get()
            
            # Assert
            call_kwargs = mock_get.call_args[1]
            assert "headers" in call_kwargs
            assert call_kwargs["headers"]["Authorization"] == "Bearer token"

    def test_execute_request_with_json_payload(self, route, mock_response):
        # Arrange
        with patch('requests.post', return_value=mock_response) as mock_post:
            
            # Act
            route.execute_post()
            
            # Assert
            call_kwargs = mock_post.call_args[1]
            assert "json" in call_kwargs
            assert call_kwargs["json"] == {"test": "data"}

    def test_execute_request_network_error(self, route):
        # Arrange
        with patch('requests.get', side_effect=requests.ConnectionError("Network error")):
            
            # Act & Assert
            with pytest.raises(requests.ConnectionError):
                route.execute_get()

    def test_integrate_with_none_method_raises_error(self, route):
        # Arrange
        route.set_method = Mock(return_value=None)
        route.method = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Method cannot be None"):
            route.integrate()

    @pytest.mark.parametrize("method,expected_function", [
        (RouteMethod.GET, "execute_get"),
        (RouteMethod.POST, "execute_post"),
        (RouteMethod.PUT, "execute_put"),
        (RouteMethod.DELETE, "execute_delete")
    ])
    def test_integrate_method_mapping(self, route, mock_response, method, expected_function):
        # Arrange
        route.method = method
        route.set_method = Mock(return_value=method)
        
        with patch.object(route, expected_function, return_value=mock_response) as mock_method:
            
            # Act
            result = route.integrate()
            # Assert
            mock_method.assert_called_once()
            assert result.success is True