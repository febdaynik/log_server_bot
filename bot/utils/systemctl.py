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
