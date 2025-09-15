from pydantic_settings import BaseSettings


class Config(BaseSettings):
	bot_token: str

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"
		env_nested_delimiter = "__"


config = Config()
print(config)
