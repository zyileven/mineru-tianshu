from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class MineruTianshuProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Validate API server URL
            api_server_url = credentials.get('api_server_url', '').rstrip('/')
            if not api_server_url:
                raise ToolProviderCredentialValidationError("API Server URL is required")

            # Validate URL format
            if not (api_server_url.startswith('http://') or api_server_url.startswith('https://')):
                raise ToolProviderCredentialValidationError("API Server URL must start with http:// or https://")

            # Get optional credentials
            api_key = credentials.get('api_key', '')
            verify_ssl = credentials.get('verify_ssl', True)

            # Prepare headers with optional API key
            headers = {}
            if api_key:
                headers['X-API-Key'] = api_key

            # Test connection with health check endpoint
            import requests
            try:
                response = requests.get(
                    f"{api_server_url}/api/v1/health",
                    headers=headers,
                    timeout=10,
                    verify=verify_ssl
                )
                response.raise_for_status()

                # Optionally verify response structure
                result = response.json()
                if not isinstance(result, dict):
                    raise ToolProviderCredentialValidationError("Invalid API server response format")

            except requests.exceptions.SSLError as e:
                raise ToolProviderCredentialValidationError(
                    f"SSL certificate verification failed: {str(e)}. "
                    "You can disable SSL verification in settings (not recommended for production)."
                )
            except requests.exceptions.Timeout:
                raise ToolProviderCredentialValidationError(
                    f"Connection timeout. Please check if the API server at {api_server_url} is accessible."
                )
            except requests.exceptions.ConnectionError as e:
                raise ToolProviderCredentialValidationError(
                    f"Cannot connect to API server at {api_server_url}: {str(e)}"
                )
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 or e.response.status_code == 403:
                    raise ToolProviderCredentialValidationError(
                        "Authentication failed. Please check your API key."
                    )
                raise ToolProviderCredentialValidationError(
                    f"HTTP error {e.response.status_code}: {str(e)}"
                )
            except ValueError as e:
                raise ToolProviderCredentialValidationError(
                    f"Invalid JSON response from API server: {str(e)}"
                )

        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Unexpected error: {str(e)}")

    #########################################################################################
    # If OAuth is supported, uncomment the following functions.
    # Warning: please make sure that the sdk version is 0.4.2 or higher.
    #########################################################################################
    # def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
    #     """
    #     Generate the authorization URL for mineru-tianshu OAuth.
    #     """
    #     try:
    #         """
    #         IMPLEMENT YOUR AUTHORIZATION URL GENERATION HERE
    #         """
    #     except Exception as e:
    #         raise ToolProviderOAuthError(str(e))
    #     return ""
        
    # def _oauth_get_credentials(
    #     self, redirect_uri: str, system_credentials: Mapping[str, Any], request: Request
    # ) -> Mapping[str, Any]:
    #     """
    #     Exchange code for access_token.
    #     """
    #     try:
    #         """
    #         IMPLEMENT YOUR CREDENTIALS EXCHANGE HERE
    #         """
    #     except Exception as e:
    #         raise ToolProviderOAuthError(str(e))
    #     return dict()

    # def _oauth_refresh_credentials(
    #     self, redirect_uri: str, system_credentials: Mapping[str, Any], credentials: Mapping[str, Any]
    # ) -> OAuthCredentials:
    #     """
    #     Refresh the credentials
    #     """
    #     return OAuthCredentials(credentials=credentials, expires_at=-1)
