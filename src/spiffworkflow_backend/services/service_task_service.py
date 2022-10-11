"""ServiceTask_service."""
import json
from typing import Any
from typing import Dict

import requests
from flask import current_app

from spiffworkflow_backend.services.file_system_service import FileSystemService
from spiffworkflow_backend.services.secret_service import SecretService


def connector_proxy_url() -> Any:
    """Returns the connector proxy url."""
    return current_app.config["CONNECTOR_PROXY_URL"]


class ServiceTaskDelegate:
    """ServiceTaskDelegate."""

    @staticmethod
    def normalize_value(value: Any) -> Any:
        """Normalize_value."""
        if isinstance(value, dict):
            value = json.dumps(value)

        secret_prefix = "secret:"  # noqa: S105
        if value.startswith(secret_prefix):
            key = value.removeprefix(secret_prefix)
            secret = SecretService().get_secret(key)
            assert secret  # noqa: S101
            return secret.value

        file_prefix = "file:"
        if value.startswith(file_prefix):
            file_name = value.removeprefix(file_prefix)
            full_path = FileSystemService.full_path_from_relative_path(file_name)
            with open(full_path) as f:
                return f.read()

        return value

    @staticmethod
    def call_connector(name: str, bpmn_params: Any, task_data: Any) -> str:
        """Calls a connector via the configured proxy."""
        params = {
            k: ServiceTaskDelegate.normalize_value(v["value"])
            for k, v in bpmn_params.items()
        }
        params['spiff__task_data'] = json.dumps(task_data)

        proxied_response = requests.get(f"{connector_proxy_url()}/v1/do/{name}", params)

        if proxied_response.status_code != 200:
            print("got error from connector proxy")

        return proxied_response.text


class ServiceTaskService:
    """ServiceTaskService."""

    @staticmethod
    def available_connectors() -> Any:
        """Returns a list of available connectors."""
        try:
            response = requests.get(f"{connector_proxy_url()}/v1/commands")

            if response.status_code != 200:
                return []

            parsed_response = json.loads(response.text)
            return parsed_response
        except Exception as e:
            print(e)
            return []
