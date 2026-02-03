from typing import List, Dict

from aiogram.utils.keyboard import InlineKeyboardBuilder


def list_containers_markup(server_id: int, containers: List[Dict[str, str]]) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    DICT_CONTAINER_STATUS = {
        "created": "⏯",
        "running": "✅",
        "exited": "❌",
        "paused": "⏸",
    }

    for container in containers:
        name = container.get("Names")
        container_id = container.get("ID")
        container_status = DICT_CONTAINER_STATUS[container.get("State")]
        markup.button(text=f"{container_status} {name}", callback_data=f"docker:get:{server_id}:{container_id}")

    markup.button(text="« Назад", callback_data=f"server:get:{server_id}")
    markup.adjust(1)

    return markup.as_markup()


def container_info_markup(server_id: int, container_id: str) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="🏓 Логи", callback_data=f"docker:logs:{server_id}:{container_id}")
    markup.button(text="📲 Скачать логи", callback_data=f"docker:download_logs:{server_id}:{container_id}")
    markup.button(text="⏯ Перезапустить контейнер", callback_data=f"docker:restart:{server_id}:{container_id}")
    markup.button(text="« Назад", callback_data=f"server:docker:{server_id}")
    markup.adjust(1)

    return markup.as_markup()


def container_logs_markup(
    server_id: int,
    container_id: str,
    page: int,
    total_pages: int,
) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(
        text=" " if page == 1 else "⬅",
        callback_data="ignore" if page == 1 else f"docker:logs:back:{server_id}:{container_id}:{page-1}",
    )
    markup.button(text=f"{page} / {total_pages}", callback_data="ignore")
    markup.button(
        text=" " if total_pages == page else "➡",
        callback_data="ignore" if total_pages == page else f"docker:logs:next:{server_id}:{container_id}:{page+1}",
    )
    markup.button(text="« Назад", callback_data=f"docker:get:{server_id}:{container_id}")
    markup.adjust(3, 1)

    return markup.as_markup()
