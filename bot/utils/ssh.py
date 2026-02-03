import asyncio
import json
from typing import Optional, List, Dict, Union

import asyncssh
from asyncssh import SSHClientConnection, SSHCompletedProcess

from bot.database.models import Server
from bot.utils.systemctl import parse_systemctl_text_output

ERROR_CONNECTION_TEXT = "Ошибка подключения\nПопробуйте ещё раз"


class SshServer:
    def __init__(self, server: Server, ssh_server: Optional[SSHClientConnection] = None, timeout: int = 300):
        self.server: Server = server
        self.ssh_server: SSHClientConnection = ssh_server
        self.timeout: int = timeout  # время жизни соединения (сек)
        self.disconnect_task: Optional[asyncio.Task] = None
        self.is_connected: bool = False

    async def connect(self) -> None:
        private_key = asyncssh.import_private_key(self.server.ssh_key)

        self.ssh_server = await asyncssh.connect(
            self.server.ip_address,
            port=22,
            username=self.server.username,
            client_keys=[private_key],
            known_hosts=None,
        )
        self.refresh_timeout()
        self.is_connected = True

    async def disconnect(self) -> None:
        if self.ssh_server:
            self.ssh_server.close()
            self.ssh_server = None
        if self.disconnect_task:
            self.disconnect_task.cancel()
            self.disconnect_task = None
        self.is_connected = False

    def refresh_timeout(self) -> None:
        """Сбрасывает таймер автоотключения"""
        if self.disconnect_task:
            self.disconnect_task.cancel()
        loop = asyncio.get_event_loop()
        self.disconnect_task = loop.create_task(self._auto_disconnect())

    async def _auto_disconnect(self) -> None:
        try:
            await asyncio.sleep(self.timeout)
            await self.disconnect()
            print(f"SSH {self.server.ip_address} отключен по таймауту")
        except asyncio.CancelledError:
            pass  # таймер сброшен

    async def make_request(self, command: str) -> Optional[SSHCompletedProcess]:
        if not self.ssh_server:
            return None
        try:
            return await self.ssh_server.run(command, check=False)
        except (asyncssh.Error, OSError) as e:
            print(f"Ошибка выполнения команды на {self.server.ip_address}: {e}")
            await self.disconnect()
            return None

    async def get_info(self) -> str:
        # Одна команда для получения всей информации
        cmd = """
        {
          echo '{'
          echo '  "os": "'$(uname -srm)'",'
          echo '  "uptime": "'$(uptime -p | sed \"s/^up //\")'",'
          echo '  "disk_total": "'$(df -h / --output=size | awk "NR==2")'",'
          echo '  "disk_used": "'$(df -h / --output=used | awk "NR==2")'",'
          echo '  "disk_available": "'$(df -h / --output=avail | awk "NR==2")'",'
          echo '  "memory_total": "'$(free -m | awk "NR==2 {print \\$2}")'M",'
          echo '  "memory_used": "'$(free -m | awk "NR==2 {print \\$3}")'M"'
          echo '}'
        }
        """

        result = await self.make_request(cmd)
        if result is None:
            return ERROR_CONNECTION_TEXT

        if result.stderr.strip():
            return result.stderr.strip()

        try:
            info = json.loads(result.stdout)
        except json.JSONDecodeError:
            return "Ошибка обработки JSON"

        return (
            f"<b>🖥 OS:</b> {info.get('os')}\n"
            f"<b>⏰ Время работы:</b> {info.get('uptime')}\n"
            "<b>💽 Диск</b>\n"
            f"├ всего: {info.get('disk_total')}\n"
            f"├ заполнено: {info.get('disk_used')}\n"
            f"└ свободно: {info.get('disk_available')}\n"
            "<b>💾 Память</b>\n"
            f"├ всего: {info.get('memory_total')}\n"
            f"└ используется: {info.get('memory_used')}"
        )

    async def get_ping(self) -> str:
        result = await self.make_request("uptime -p | sed \"s/^up //\"")
        if result is None:
            return ERROR_CONNECTION_TEXT

        return result.stdout.strip() or result.stderr.strip()

    async def get_list_systemctl(self) -> Union[str, List[Dict[str, str]]]:
        """Улучшенная версия с обработкой различных форматов"""

        # Пробуем разные команды по порядку
        commands = [
            "systemctl list-units --type=service --no-pager --output=json",
            "systemctl list-units --type=service --no-pager --no-legend",
            "systemctl list-units --type=service --no-pager"
        ]

        for cmd in commands:
            result = await self.make_request(cmd)

            if result is None:
                continue

            if result.stderr.strip() and "unrecognized option" not in result.stderr:
                # Если это не ошибка неизвестной опции, возвращаем ошибку
                return result.stderr.strip()

            if result.stdout.strip():
                # Пробуем распарсить как JSON
                if cmd.endswith("--output=json"):
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        continue  # Пробуем следующую команду

                # Парсим текстовый вывод
                return await parse_systemctl_text_output(result.stdout)

        return "Не удалось получить список сервисов"

    async def get_info_service(self, service: str) -> Union[str, Dict[str, str]]:
        result = await self.make_request(
            f"systemctl show {service}.service --property=Id,ActiveState,SubState,LoadState,UnitFileState,MainPID,"
            "MemoryCurrent,CPUUsagePercentage --output=json"
        )
        if result is None:
            return {"error": ERROR_CONNECTION_TEXT}

        return result.stdout.strip() or result.stderr.strip()

    async def get_logs_service(self, service: str, page: int = 1) -> Dict[str, str]:
        PAGE_SIZE = 20

        total = await self.make_request(f"journalctl -u {service}.service --no-pager | wc -l")
        if total is None:
            return {
                "page": 1,
                "total_pages": 1,
                "logs": ERROR_CONNECTION_TEXT,
            }

        total_lines = int(total.stdout.strip())
        total_pages = max(1, (total_lines + PAGE_SIZE - 1) // PAGE_SIZE)

        # вычисляем, сколько строк нужно "отбросить" от конца
        skip_from_end = (page - 1) * PAGE_SIZE
        start_line = max(1, total_lines - skip_from_end - PAGE_SIZE + 1)

        # берём кусок
        result = await self.make_request(
            f"journalctl -u {service}.service --no-pager "
            f"| sed -n '{start_line},+{PAGE_SIZE - 1}p'"
        )
        if result is None:
            return {
                "page": 1,
                "total_pages": 1,
                "logs": ERROR_CONNECTION_TEXT,
            }

        logs = result.stdout.strip() or result.stderr.strip()

        return {
            "page": page,
            "total_pages": total_pages,
            "logs": logs,
        }

    async def get_full_logs_service(self, service: str) -> Union[str, Dict[str, str]]:
        result = await self.make_request(f"journalctl -u {service}.service --no-pager")
        if result is None:
            return {"error": ERROR_CONNECTION_TEXT}

        return result.stdout.strip() or result.stderr.strip()

    async def restart_service(self, service: str) -> str:
        result = await self.make_request(f"systemctl restart {service}.service")
        if result is None:
            return {"error": ERROR_CONNECTION_TEXT}

        return result.stdout.strip() or result.stderr.strip()

    async def get_list_docker_containers(self) -> Union[str, List[Dict[str, str]]]:
        result = await self.make_request("docker ps -a --format json")
        if result is None:
            return ERROR_CONNECTION_TEXT

        if result.stderr.strip():
            return result.stderr.strip()

        try:
            return [json.loads(container) for container in result.stdout.strip().split("\n")]
        except json.JSONDecodeError:
            return "Ошибка обработки JSON"

    async def get_info_docker_container(self, container_id: str) -> Union[str, Dict[str, str]]:
        result = await self.make_request(f"docker inspect {container_id} --format json")
        if result is None:
            return {"error": ERROR_CONNECTION_TEXT}

        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return "Ошибка обработки JSON"

        return result.stderr.strip()

    async def get_logs_docker_container(self, container_id: str, page: int = 1) -> Dict[str, str]:
        PAGE_SIZE = 20

        total = await self.make_request(f"docker container logs {container_id} | wc -l")
        if total is None:
            return {
                "page": 1,
                "total_pages": 1,
                "logs": ERROR_CONNECTION_TEXT,
            }

        total_lines = int(total.stdout.strip())
        total_pages = max(1, (total_lines + PAGE_SIZE - 1) // PAGE_SIZE)

        # вычисляем, сколько строк нужно "отбросить" от конца
        skip_from_end = (page - 1) * PAGE_SIZE
        start_line = max(1, total_lines - skip_from_end - PAGE_SIZE + 1)

        # берём кусок
        result = await self.make_request(
            f"docker container logs {container_id} "
            f"| sed -n '{start_line},+{PAGE_SIZE - 1}p'"
        )
        if result is None:
            return {
                "page": 1,
                "total_pages": 1,
                "logs": ERROR_CONNECTION_TEXT,
            }

        logs = result.stdout.strip() or result.stderr.strip()

        return {
            "page": page,
            "total_pages": total_pages,
            "logs": logs,
        }

    async def get_full_logs_docker_container(self, container_id: str) -> Union[str, Dict[str, str]]:
        result = await self.make_request(f"docker container logs {container_id}")
        if result is None:
            return {"error": ERROR_CONNECTION_TEXT}

        return result.stdout.strip() or result.stderr.strip()

    async def restart_docker_container(self, container_id: str) -> str:
        result = await self.make_request(f"docker container restart {container_id}")
        if result is None:
            return {"error": ERROR_CONNECTION_TEXT}
