import logging
from json import dumps

import structlog
from structlog import WriteLoggerFactory


def get_structlog_config() -> dict:
    return {
        "processors": get_processors(),
        "cache_logger_on_first_use": True,
        "wrapper_class": structlog.make_filtering_bound_logger(
            logging.getLevelName("INFO")
        ),
        "logger_factory": WriteLoggerFactory(),
    }


def get_processors() -> list:
    def custom_json_serializer(data, *args, **kwargs):
        result = dict()

        # Set keys in specific order
        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        # Add all other fields
        result.update(**data)
        return dumps(result, default=str, ensure_ascii=False)

    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(serializer=custom_json_serializer),
    ]

    return processors
