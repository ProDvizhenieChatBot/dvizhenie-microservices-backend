# services/bot_service/src/app/internal_clients/api_client.py
import httpx

from app.core.config import settings


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_telegram_session(self) -> str | None:
        """
        Calls the API service to create a session for a Telegram user.
        Returns the session_token if successful, otherwise None.
        """
        # TODO: Implement robust error handling (try-except blocks, logging)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{self.base_url}/api/v1/sessions/telegram')
                response.raise_for_status()
                data = response.json()
                # The API now returns 'session_token' which corresponds to the application ID.
                token = data.get('session_token')
                return str(token) if token is not None else None
            except httpx.HTTPStatusError as e:
                print(f'HTTP error occurred: {e}')
                return None
            except Exception as e:
                print(f'An unexpected error occurred: {e}')
                return None


# Singleton instance of the API client
api_client = ApiClient(base_url=settings.API_SERVICE_URL)
