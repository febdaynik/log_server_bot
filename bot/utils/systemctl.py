from typing import List, Dict


async def sorted_systemctl(services: List[Dict[str, str]]) -> List[str]:
    exclude_prefixes = ["systemd-", "dbus", "polkit", "console-", "getty@"]
    return [service for service in services if not any(service.get("unit").startswith(p) for p in exclude_prefixes)]


async def translate_text_info_to_json(info: str) -> Dict[str, str]:
    data = {}
    for line in info.split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            data[key] = value

    return data


async def parse_systemctl_text_output(output: str) -> List[Dict[str, str]]:
    """Парсинг текстового вывода systemctl"""
    services = []
    lines = output.strip().split('\n')

    for line in lines:
        line = line.strip()

        # Пропускаем пустые строки и разделители
        if not line or line.startswith("●") or "LOAD" in line and "ACTIVE" in line and "SUB" in line:
            continue

        # Разбиваем строку, учитывая что пробелов может быть много
        parts = line.split()
        if len(parts) >= 4:
            # Находим индексы перехода между полями
            # Ищем где заканчивается имя сервиса (обычно заканчивается на .service)
            unit_end = 0
            for i, part in enumerate(parts):
                if part.endswith('.service'):
                    unit_end = i
                    break

            if unit_end >= 0 and len(parts) >= unit_end + 4:
                service = {
                    'unit': ' '.join(parts[:unit_end + 1]),
                    'load': parts[unit_end + 1] if unit_end + 1 < len(parts) else '',
                    'active': parts[unit_end + 2] if unit_end + 2 < len(parts) else '',
                    'sub': parts[unit_end + 3] if unit_end + 3 < len(parts) else '',
                    'description': ' '.join(parts[unit_end + 4:]) if unit_end + 4 < len(parts) else ''
                }
                services.append(service)

    return services