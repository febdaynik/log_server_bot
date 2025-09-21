import asyncio
from typing import Optional, List, Dict

import asyncssh
from asyncssh import SSHClientConnection

from bot.database.models import Server


class SshServer:
    def __init__(self, server: Server, ssh_server: Optional[SSHClientConnection] = None, timeout: int = 300):
        self.server: Server = server
        self.ssh_server: SSHClientConnection = ssh_server
        self.timeout: int = timeout  # время жизни соединения (сек)
        self.disconnect_task: Optional[asyncio.Task] = None

        if self.ssh_server is None:
            loop = asyncio.get_event_loop()
            loop.create_task(self.connect())

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

    async def disconnect(self) -> None:
        if self.ssh_server:
            self.ssh_server.close()
            self.ssh_server = None
        if self.disconnect_task:
            self.disconnect_task.cancel()
            self.disconnect_task = None

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

    async def get_info(self) -> str:
        info = dict()
        commands = {
            "OS": "uname -a",
            "Uptime": "uptime -p",
            "Disk": "df -h --total | grep total",
            "Memory": "free -m"
        }

        tasks = {k: self.ssh_server.run(cmd, check=False) for k, cmd in commands.items()}
        results = await asyncio.gather(*tasks.values())

        for (k, _), result in zip(tasks.items(), results):
            info[k] = result.stdout.strip() or result.stderr.strip()

        return (
            f"<b>OS:</b> {info.get('OS')}\n"
            f"<b>Uptime:</b> {info.get('Uptime')}\n"
            f"<b>Disk:</b> {info.get('Disk')}\n"
            f"<b>Memory:</b> {info.get('Memory')}"
        )

    async def get_ping(self) -> str:
        result = await self.ssh_server.run("uptime -p", check=False)
        return result.stdout.strip() or result.stderr.strip()

    async def get_list_systemctl(self) -> List[str]:
        result = await self.ssh_server.run("systemctl list-units --type=service --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()

    async def get_info_service(self, service: str) -> str:
        result = await self.ssh_server.run(f"systemctl status {service}.service --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()

    async def get_logs_service(self, service: str, page: int = 1) -> Dict[str, str]:
        PAGE_SIZE = 20

        total = await self.ssh_server.run(f"journalctl -u {service}.service --no-pager | wc -l", check=False)
        total_lines = int(total.stdout.strip())
        total_pages = max(1, (total_lines + PAGE_SIZE - 1) // PAGE_SIZE)

        # вычисляем, сколько строк нужно "отбросить" от конца
        skip_from_end = (page - 1) * PAGE_SIZE
        start_line = max(1, total_lines - skip_from_end - PAGE_SIZE + 1)

        # берём кусок
        result = await self.ssh_server.run(
            f"journalctl -u {service}.service --no-pager "
            f"| sed -n '{start_line},+{PAGE_SIZE - 1}p'",
            check=False,
        )
        logs = result.stdout.strip() or result.stderr.strip()

        return {
            "page": page,
            "total_pages": total_pages,
            "logs": logs,
        }

    async def get_full_logs_service(self, service: str) -> str:
        result = await self.ssh_server.run(f"journalctl -u {service}.service --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()

    async def restart_service(self, service: str) -> str:
        result = await self.ssh_server.run(f"systemctl restart {service}.service", check=False)
        return result.stdout.strip() or result.stderr.strip()
