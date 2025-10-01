import io
import zipfile

import httpx

from app.core.config import Settings
from app.models.db_models import Application


async def create_documents_zip_archive(app: Application, settings: Settings) -> io.BytesIO:
    """
    Orchestrates fetching all documents for an application and zipping them.

    Args:
        app: The SQLAlchemy Application object with its 'files' relationship loaded.
        settings: The application settings, used for service URLs.

    Returns:
        An in-memory BytesIO buffer containing the generated ZIP file.
    """
    zip_buffer = io.BytesIO()

    async with httpx.AsyncClient() as client:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_record in app.files:
                try:
                    link_url = (
                        f'{settings.FILE_STORAGE_SERVICE_URL}/api/v1/files/'
                        f'{file_record.file_id}/download-link'
                    )
                    link_response = await client.get(link_url)
                    link_response.raise_for_status()
                    public_download_url = link_response.json()['download_url']

                    internal_download_url = public_download_url.replace(
                        settings.S3_PUBLIC_URL, settings.S3_ENDPOINT_URL
                    )

                    content_response = await client.get(internal_download_url)
                    content_response.raise_for_status()
                    file_bytes = content_response.content

                    zip_file.writestr(file_record.original_filename, file_bytes)

                except httpx.HTTPStatusError as e:
                    print(
                        f'Failed to download file {file_record.file_id} '
                        f'for application {app.id}: {e}'
                    )
                    error_message = f'Failed to download this file. Error: {e.response.status_code}'
                    zip_file.writestr(f'{file_record.original_filename}.error.txt', error_message)

    zip_buffer.seek(0)
    return zip_buffer
