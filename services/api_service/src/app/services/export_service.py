import io
from typing import Any

import pandas as pd

from app.models.db_models import Application


def generate_xlsx_export(applications: list[Application]) -> io.BytesIO:
    """
    Generates an XLSX file in memory from a list of Application objects.

    Args:
        applications: A list of SQLAlchemy Application models.

    Returns:
        An in-memory BytesIO buffer containing the XLSX file data.
    """
    if not applications:
        return io.BytesIO()

    flat_data: list[dict[str, Any]] = []
    for app in applications:
        app_dict = {
            'ID': str(app.id),
            'Telegram ID': app.telegram_id,
            'Status': app.status,
            'Admin Comment': app.admin_comment,
            'Created At': app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Updated At': app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if isinstance(app.data, dict):
            app_dict.update(app.data)
        flat_data.append(app_dict)

    df = pd.DataFrame(flat_data)

    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Applications', index=False)

    output_buffer.seek(0)

    return output_buffer
