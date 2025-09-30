# services/bot_service/src/app/internal_clients/api_client.py
import httpx

from app.core.config import settings


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_telegram_session(self, telegram_id: int) -> str | None:
        """
        Calls the API service to create or resume a session for a Telegram user.
        Sends the user's telegram_id in the request body.
        Returns the application_uuid if successful, otherwise None.
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {'telegram_id': telegram_id}
                response = await client.post(
                    f'{self.base_url}/api/v1/sessions/telegram', json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data.get('application_uuid')
            except httpx.HTTPStatusError as e:
                print(f'HTTP error occurred while creating session for {telegram_id}: {e}')
                return None
            except Exception as e:
                print(f'An unexpected error occurred while creating session for {telegram_id}: {e}')
                return None


# Singleton instance of the API client
api_client = ApiClient(base_url=settings.API_SERVICE_URL)
