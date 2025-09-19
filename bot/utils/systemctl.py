from typing import List


async def parse_systemctl_output(output: str) -> List[str]:
    services = []
    exclude_prefixes = ["systemd-", "dbus", "polkit", "console-", "getty@"]

    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("LOAD") or line.startswith(" "):
            continue

        if line.startswith("●"):  # у systemctl "●" перед failed
            line = line.replace("●", "", 1).strip()

        # проверяем, что это действительно сервис/юнит
        if not (".service" in line or ".socket" in line or ".target" in line):
            continue

        if any(line.startswith(p) for p in exclude_prefixes):
            continue

        parts = line.split(None, 4)  # разбиваем на 5 частей максимум
        if len(parts) == 5:
            unit, load, active, sub, description = parts
            services.append({
                "UNIT": unit,
                "LOAD": load,
                "ACTIVE": active,
                "SUB": sub,
                "DESCRIPTION": description
            })
    return services
