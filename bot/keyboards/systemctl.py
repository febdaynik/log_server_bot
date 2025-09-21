from typing import Dict, List

from aiogram.utils.keyboard import InlineKeyboardBuilder


def list_services_markup(server_id: int, services: List[Dict[str, str]]) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    for service in services:
        unit = service.get("UNIT")
        service_name = unit.replace(".service", "")
        markup.button(text=unit, callback_data=f"systemctl:get:{server_id}:{service_name}")

    markup.button(text="« Назад", callback_data=f"server:get:{server_id}")
    markup.adjust(1)

    return markup.as_markup()


def service_info_markup(server_id: int, service: str) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="🏓 Логи", callback_data=f"systemctl:logs:{server_id}:{service}")
    markup.button(text="📲 Скачать логи", callback_data=f"systemctl:download_logs:{server_id}:{service}")
    markup.button(text="⏯ Перезапустить сервис", callback_data=f"systemctl:restart:{server_id}:{service}")
    markup.button(text="« Назад", callback_data=f"server:systemctl:{server_id}")
    markup.adjust(1)

    return markup.as_markup()


def service_logs_markup(
    server_id: int,
    service_name: str,
    page: int,
    total_pages: int,
) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(
        text=" " if page == 1 else "⬅",
        callback_data="ignore" if page == 1 else f"systemctl:logs:back:{server_id}:{service_name}:{page-1}",
    )
    markup.button(text=f"{page} / {total_pages}", callback_data="ignore")
    markup.button(
        text=" " if total_pages == page else "➡",
        callback_data="ignore" if total_pages == page else f"systemctl:logs:next:{server_id}:{service_name}:{page+1}",
    )
    markup.button(text="« Назад", callback_data=f"systemctl:get:{server_id}:{service_name}")
    markup.adjust(3, 1)

    return markup.as_markup()
