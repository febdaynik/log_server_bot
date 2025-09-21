from typing import Dict
from bot.database.models import Server
from .ssh import SshServer


class SshManager:
    """Менеджер SSH-подключений для пользователей"""

    def __init__(self, timeout: int = 300):
        self.connections: Dict[int, SshServer] = {}
        self.timeout = timeout

    async def get_connection(self, user_id: int, server: Server) -> SshServer:
        """Возвращает (или создаёт) подключение для пользователя"""
        conn = self.connections.get(user_id)

        if conn is None or conn.ssh_server is None:
            conn = SshServer(server, timeout=self.timeout)
            await conn.connect()
            self.connections[user_id] = conn
        else:
            conn.refresh_timeout()

        return conn

    async def disconnect(self, user_id: int) -> None:
        """Принудительно отключает пользователя"""
        conn = self.connections.get(user_id)
        if conn:
            await conn.disconnect()
            del self.connections[user_id]

    async def disconnect_all(self) -> None:
        """Отключает всех пользователей (например, при остановке бота)"""
        print("Всё выключено")
        for user_id, conn in list(self.connections.items()):
            await conn.disconnect()
            del self.connections[user_id]

    def has_connection(self, user_id: int) -> bool:
        """Проверка: есть ли активное подключение у пользователя"""
        return user_id in self.connections and self.connections[user_id].ssh_server is not None
