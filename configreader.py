from pydantic_settings import BaseSettings

from bot.utils.ssh_manager import SshManager


class Config(BaseSettings):
	bot_token: str

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"
		env_nested_delimiter = "__"


config = Config()
ssh_manager = SshManager(timeout=300)
print(config)
