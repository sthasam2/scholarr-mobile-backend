import os
from pathlib import Path

import dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent.__str__()

config = dotenv.dotenv_values(BASE_DIR + "/.env")


def get_environ_variable(var_name: str) -> str:
    """
    Get the environment variable from your os or return an exception
    """
    try:
        if config.get(var_name):
            print("dotenv", var_name)
            return config.get(var_name)
        elif os.environ[var_name]:
            print("environ", var_name)
            return os.environ[var_name]
        else:
            raise KeyError

    except KeyError:
        error_msg = f"{var_name} not found!\nSet the '{var_name}' environment variable"
        raise ImproperlyConfigured(error_msg)


def get_dotenv_variable(var_name: str) -> str:
    """
    Get the environment variable from your os or return an exception
    """

    try:
        return config.get(var_name)
    except KeyError:
        error_msg = f"{var_name} not found!\nSet the '{var_name}' environment variable"
        raise ImproperlyConfigured(error_msg)
