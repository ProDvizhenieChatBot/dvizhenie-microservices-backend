import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


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
                logger.error(
                    f'HTTP error creating session for {telegram_id}: {e.response.status_code} - '
                    f'{e.response.text}'
                )
                return None
            except Exception as e:
                logger.error(
                    f'Unexpected error creating session for {telegram_id}: {e}', exc_info=True
                )
                return None

    async def get_telegram_application_status(self, telegram_id: int) -> str | None:
        """
        Calls the API service to get the status of the latest application
        for a Telegram user.
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {'telegram_id': telegram_id}
                response = await client.get(
                    f'{self.base_url}/api/v1/sessions/telegram/status', params=params
                )

                if response.status_code == 404:
                    return 'not_found'

                response.raise_for_status()
                data = response.json()
                return data.get('status')
            except httpx.HTTPStatusError as e:
                logger.error(
                    f'HTTP error getting status for {telegram_id}: {e.response.status_code} - '
                    f'{e.response.text}'
                )
                return None
            except Exception as e:
                logger.error(
                    f'Unexpected error getting status for {telegram_id}: {e}', exc_info=True
                )
                return None


# Singleton instance of the API client
api_client = ApiClient(base_url=settings.API_SERVICE_URL)
