"""Default."""
import re
from os import environ

# Does the site allow self-registration of users
SELF_REGISTRATION = environ.get("SELF_REGISTRATION", default=False)

DEVELOPMENT = False

BPMN_SPEC_ABSOLUTE_DIR = environ.get("BPMN_SPEC_ABSOLUTE_DIR", default="")
CORS_DEFAULT = "*"
CORS_ALLOW_ORIGINS = re.split(
    r",\s*", environ.get("CORS_ALLOW_ORIGINS", default=CORS_DEFAULT)
)

PROCESS_WAITING_MESSAGES = (
    environ.get("PROCESS_WAITING_MESSAGES", default="false") == "true"
)
SPIFFWORKFLOW_FRONTEND_URL = environ.get(
    "SPIFFWORKFLOW_FRONTEND_URL", default="http://localhost:7001"
)
SPIFFWORKFLOW_BACKEND_URL = environ.get(
    "SPIFFWORKFLOW_BACKEND_URL", default="http://localhost:7000"
)

# Open ID server
OPEN_ID_SERVER_URL = environ.get("OPEN_ID_SERVER_URL", default="http://localhost:7002")
OPEN_ID_CLIENT_ID = environ.get("OPEN_ID_CLIENT_ID", default="spiffworkflow-backend")
OPEN_ID_REALM_NAME = environ.get("OPEN_ID_REALM_NAME", default="spiffworkflow")
OPEN_ID_CLIENT_SECRET_KEY = environ.get(
    "OPEN_ID_CLIENT_SECRET_KEY", default="JXeQExm0JhQPLumgHtIIqf52bDalHz0q"
)  # noqa: S105

SPIFFWORKFLOW_BACKEND_LOG_TO_FILE = (
    environ.get("SPIFFWORKFLOW_BACKEND_LOG_TO_FILE", default="false") == "true"
)

# service task connector proxy
CONNECTOR_PROXY_URL = environ.get(
    "CONNECTOR_PROXY_URL", default="http://localhost:7004"
)
