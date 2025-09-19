import asyncio
from typing import Optional, List

import asyncssh
from asyncssh import SSHClientConnection

from bot.database.models import Server


class SshServer:
    def __init__(self, server: Server, ssh_server: Optional[SSHClientConnection] = None):
        self.server: Server = server
        self.ssh_server: SSHClientConnection = ssh_server

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

    async def disconnect(self) -> None:
        self.ssh_server.close()

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

    async def get_logs_service(self, service: str) -> str:
        result = await self.ssh_server.run(f"journalctl -u {service}.service -n 50 --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()

    async def restart_service(self, service: str) -> str:
        result = await self.ssh_server.run(f"systemctl restart {service}.service", check=False)
        return result.stdout.strip() or result.stderr.strip()
