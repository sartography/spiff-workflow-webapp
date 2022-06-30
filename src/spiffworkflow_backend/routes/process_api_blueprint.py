"""APIs for dealing with process groups, process models, and process instances."""
import json
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import connexion  # type: ignore
import flask.wrappers
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import make_response
from flask.wrappers import Response
from sqlalchemy import desc

from spiffworkflow_backend.exceptions.process_entity_not_found_error import (
    ProcessEntityNotFoundError,
)
from spiffworkflow_backend.models.active_task import ActiveTaskModel
from spiffworkflow_backend.models.file import FileSchema
from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.principal import PrincipalModel
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceApiSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModelSchema
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.services.error_handling_service import ErrorHandlingService
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_instance_service import (
    ProcessInstanceService,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.spec_file_service import SpecFileService

# from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
# from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
# from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

process_api_blueprint = Blueprint("process_api", __name__)


def status() -> flask.wrappers.Response:
    """Status."""
    ProcessInstanceModel.query.filter().first()
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_group_add(
    body: Dict[str, Union[str, bool, int]]
) -> flask.wrappers.Response:
    """Add_process_group."""
    process_model_service = ProcessModelService()
    process_group = ProcessGroupSchema().load(body)
    process_model_service.add_process_group(process_group)
    return Response(
        json.dumps(ProcessGroupSchema().dump(process_group)),
        status=201,
        mimetype="application/json",
    )


def process_group_delete(process_group_id: str) -> flask.wrappers.Response:
    """Process_group_delete."""
    ProcessModelService().process_group_delete(process_group_id)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_group_update(
    process_group_id: str, body: Dict[str, Union[str, bool, int]]
) -> Dict[str, Union[str, bool, int]]:
    """Process Group Update."""
    process_group = ProcessGroupSchema().load(body)
    ProcessModelService().update_process_group(process_group)
    return ProcessGroupSchema().dump(process_group)  # type: ignore


def process_groups_list(page: int = 1, per_page: int = 100) -> flask.wrappers.Response:
    """Process_groups_list."""
    process_groups = sorted(ProcessModelService().get_process_groups())
    batch = ProcessModelService().get_batch(
        items=process_groups, page=page, per_page=per_page
    )
    pages = len(process_groups) // per_page
    remainder = len(process_groups) % per_page
    if remainder > 0:
        pages += 1
    response_json = {
        "results": ProcessGroupSchema(many=True).dump(batch),
        "pagination": {
            "count": len(batch),
            "total": len(process_groups),
            "pages": pages,
        },
    }
    return Response(json.dumps(response_json), status=200, mimetype="application/json")


def process_group_show(
    process_group_id: str,
) -> Any:
    """Process_group_show."""
    process_group = ProcessModelService().get_process_group(process_group_id)
    return ProcessGroupSchema().dump(process_group)


def process_model_add(
    body: Dict[str, Union[str, bool, int]]
) -> flask.wrappers.Response:
    """Add_process_model."""
    process_model_info = ProcessModelInfoSchema().load(body)
    if process_model_info is None:
        raise ApiError(
            code="process_model_could_not_be_created",
            message=f"Process Model could not be created from given body: {body}",
            status_code=400,
        )

    process_model_service = ProcessModelService()
    process_group = process_model_service.get_process_group(
        process_model_info.process_group_id
    )
    if process_group is None:
        raise ApiError(
            code="process_model_could_not_be_created",
            message=f"Process Model could not be created from given body because Process Group could not be found: {body}",
            status_code=400,
        )

    process_model_info.process_group = process_group
    workflows = process_model_service.cleanup_workflow_spec_display_order(process_group)
    size = len(workflows)
    process_model_info.display_order = size
    process_model_service.add_spec(process_model_info)
    return Response(
        json.dumps(ProcessModelInfoSchema().dump(process_model_info)),
        status=201,
        mimetype="application/json",
    )


def process_model_delete(
    process_group_id: str, process_model_id: str
) -> flask.wrappers.Response:
    """Process_model_delete."""
    ProcessModelService().process_model_delete(process_model_id)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_model_update(
    process_group_id: str, process_model_id: str, body: Dict[str, Union[str, bool, int]]
) -> Any:
    """Process_model_update."""
    process_model = ProcessModelInfoSchema().load(body)
    ProcessModelService().update_spec(process_model)
    return ProcessModelInfoSchema().dump(process_model)


def process_model_show(process_group_id: str, process_model_id: str) -> Any:
    """Process_model_show."""
    process_model = get_process_model(process_model_id, process_group_id)
    files = sorted(SpecFileService.get_files(process_model))
    process_model.files = files
    process_model_json = ProcessModelInfoSchema().dump(process_model)
    return process_model_json


def process_model_list(
    process_group_id: str, page: int = 1, per_page: int = 100
) -> flask.wrappers.Response:
    """Process model list!"""
    process_models = sorted(ProcessModelService().get_process_models(process_group_id))
    batch = ProcessModelService().get_batch(
        process_models, page=page, per_page=per_page
    )
    pages = len(process_models) // per_page
    remainder = len(process_models) % per_page
    if remainder > 0:
        pages += 1
    response_json = {
        "results": ProcessModelInfoSchema(many=True).dump(batch),
        "pagination": {
            "count": len(batch),
            "total": len(process_models),
            "pages": pages,
        },
    }

    return Response(json.dumps(response_json), status=200, mimetype="application/json")


def get_file(process_group_id: str, process_model_id: str, file_name: str) -> Any:
    """Get_file."""
    process_model = get_process_model(process_model_id, process_group_id)
    files = SpecFileService.get_files(process_model, file_name)
    if len(files) == 0:
        raise ApiError(
            code="unknown file",
            message=f"No information exists for file {file_name}"
            f" it does not exist in workflow {process_model_id}.",
            status_code=404,
        )

    file = files[0]
    file_contents = SpecFileService.get_data(process_model, file.name)
    file.file_contents = file_contents
    file.process_model_id = process_model.id
    file.process_group_id = process_model.process_group_id
    return FileSchema().dump(file)


def process_model_file_update(
    process_group_id: str, process_model_id: str, file_name: str
) -> flask.wrappers.Response:
    """Process_model_file_save."""
    process_model = get_process_model(process_model_id, process_group_id)

    request_file = get_file_from_request()
    request_file_contents = request_file.stream.read()
    if not request_file_contents:
        raise ApiError(
            code="file_contents_empty",
            message="Given request file does not have any content",
            status_code=400,
        )

    SpecFileService.update_file(process_model, file_name, request_file_contents)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def add_file(process_group_id: str, process_model_id: str) -> flask.wrappers.Response:
    """Add_file."""
    process_model_service = ProcessModelService()
    process_model = get_process_model(process_model_id, process_group_id)
    request_file = get_file_from_request()
    if not request_file.filename:
        raise ApiError(
            code="could_not_get_filename",
            message="Could not get filename from request",
            status_code=400,
        )

    file = SpecFileService.add_file(
        process_model, request_file.filename, request_file.stream.read()
    )
    file_contents = SpecFileService.get_data(process_model, file.name)
    file.file_contents = file_contents
    file.process_model_id = process_model.id
    file.process_group_id = process_model.process_group_id
    if not process_model.primary_process_id and file.type == FileType.bpmn.value:
        SpecFileService.set_primary_bpmn(process_model, file.name)
        process_model_service.update_spec(process_model)
    return Response(
        json.dumps(FileSchema().dump(file)), status=201, mimetype="application/json"
    )


def process_instance_create(
    process_group_id: str, process_model_id: str
) -> flask.wrappers.Response:
    """Create_process_instance."""
    process_instance = ProcessInstanceService.create_process_instance(
        process_model_id, g.user, process_group_identifier=process_group_id
    )
    return Response(
        json.dumps(ProcessInstanceModelSchema().dump(process_instance)),
        status=201,
        mimetype="application/json",
    )


def process_instance_run(
    process_group_id: str,
    process_model_id: str,
    process_instance_id: int,
    do_engine_steps: bool = True,
) -> flask.wrappers.Response:
    """Process_instance_run."""
    process_instance = ProcessInstanceService().get_process_instance(
        process_instance_id
    )
    processor = ProcessInstanceProcessor(process_instance)

    if do_engine_steps:
        try:
            processor.do_engine_steps()
        except Exception as e:
            ErrorHandlingService().handle_error(processor, e)
            task = processor.bpmn_process_instance.last_task
            raise ApiError.from_task(
                code="unknown_exception",
                message=f"An unknown error occurred. Original error: {e}",
                status_code=400,
                task=task,
            ) from e
        processor.save()
        ProcessInstanceService.update_task_assignments(processor)

    process_instance_api = ProcessInstanceService.processor_to_process_instance_api(
        processor
    )
    process_instance_data = processor.get_data()
    process_instance_metadata = ProcessInstanceApiSchema().dump(process_instance_api)
    process_instance_metadata["data"] = process_instance_data
    return Response(
        json.dumps(process_instance_metadata), status=200, mimetype="application/json"
    )


def process_instance_list(
    process_group_id: str,
    process_model_id: str,
    page: int = 1,
    per_page: int = 100,
    start_from: Optional[int] = None,
    start_till: Optional[int] = None,
    end_from: Optional[int] = None,
    end_till: Optional[int] = None,
    process_status: Optional[str] = None,
) -> flask.wrappers.Response:
    """Process_instance_list."""
    process_model = get_process_model(process_model_id, process_group_id)

    results = ProcessInstanceModel.query.filter_by(
        process_model_identifier=process_model.id
    )

    # this can never happen. obviously the class has the columns it defines. this is just to appease mypy.
    if (
        ProcessInstanceModel.start_in_seconds is None
        or ProcessInstanceModel.end_in_seconds is None
    ):
        raise (
            ApiError(
                code="unexpected_condition",
                message="Something went very wrong",
                status_code=500,
            )
        )

    if start_from is not None:
        results = results.filter(ProcessInstanceModel.start_in_seconds >= start_from)
    if start_till is not None:
        results = results.filter(ProcessInstanceModel.start_in_seconds <= start_till)
    if end_from is not None:
        results = results.filter(ProcessInstanceModel.end_in_seconds >= end_from)
    if end_till is not None:
        results = results.filter(ProcessInstanceModel.end_in_seconds <= end_till)
    if process_status is not None:
        results = results.filter(ProcessInstanceModel.status == process_status)

    process_instances = results.order_by(
        ProcessInstanceModel.start_in_seconds.desc(), ProcessInstanceModel.id.desc()  # type: ignore
    ).paginate(page, per_page, False)

    response_json = {
        "results": process_instances.items,
        "pagination": {
            "count": len(process_instances.items),
            "total": process_instances.total,
            "pages": process_instances.pages,
        },
    }

    return make_response(jsonify(response_json), 200)


def process_instance_delete(
    process_group_id: str, process_model_id: str, process_instance_id: int
) -> flask.wrappers.Response:
    """Create_process_instance."""
    process_instance = ProcessInstanceModel.query.filter_by(
        id=process_instance_id
    ).first()
    if process_instance is None:
        raise (
            ApiError(
                code="process_instance_cannot_be_found",
                message=f"Process instance cannot be found: {process_instance_id}",
                status_code=400,
            )
        )

    db.session.delete(process_instance)
    db.session.commit()
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_instance_report(
    process_group_id: str, process_model_id: str, page: int = 1, per_page: int = 100
) -> flask.wrappers.Response:
    """Process_instance_list."""
    process_model = get_process_model(process_model_id, process_group_id)

    process_instances = (
        ProcessInstanceModel.query.filter_by(process_model_identifier=process_model.id)
        .order_by(
            ProcessInstanceModel.start_in_seconds.desc(), ProcessInstanceModel.id.desc()  # type: ignore
        )
        .paginate(page, per_page, False)
    )

    serialized_results = []
    for process_instance in process_instances.items:
        process_instance_serialized = process_instance.serialized
        process_instance_serialized["process_group_id"] = process_model.process_group_id
        processor = ProcessInstanceProcessor(process_instance)
        process_instance_data = processor.get_data()
        process_instance_serialized["data"] = process_instance_data
        serialized_results.append(process_instance_serialized)

    response_json = {
        "results": serialized_results,
        "pagination": {
            "count": len(process_instances.items),
            "total": process_instances.total,
            "pages": process_instances.pages,
        },
    }
    return Response(json.dumps(response_json), status=200, mimetype="application/json")


def task_list_my_tasks(page: int = 1, per_page: int = 100) -> flask.wrappers.Response:
    """Task_list_my_tasks."""
    principal = PrincipalModel.query.filter_by(user_id=g.user.id).first()
    if principal is None:
        raise (
            ApiError(
                code="principal_not_found",
                message=f"Principal not found from user id: {g.user.id}",
                status_code=400,
            )
        )

    active_tasks = (
        ActiveTaskModel.query.filter_by(assigned_principal_id=principal.id)
        .order_by(desc(ActiveTaskModel.id))  # type: ignore
        .paginate(page, per_page, False)
    )

    response_json = {
        "results": active_tasks.items,
        "pagination": {
            "count": len(active_tasks.items),
            "total": active_tasks.total,
            "pages": active_tasks.pages,
        },
    }
    return make_response(jsonify(response_json), 200)


def task_show(task_id: int) -> flask.wrappers.Response:
    """Task_list_my_tasks."""
    principal = PrincipalModel.query.filter_by(user_id=g.user.id).first()
    if principal is None:
        raise (
            ApiError(
                code="principal_not_found",
                message=f"Principal not found from user id: {g.user.id}",
                status_code=400,
            )
        )
    active_task_assigned_to_me = ActiveTaskModel.query.filter_by(
        id=task_id, assigned_principal_id=principal.id
    ).first()
    if active_task_assigned_to_me is None:
        raise (
            ApiError(
                code="task_not_found",
                message=f"Task not found for principal user: {g.user.id} and id: {task_id}",
                status_code=400,
            )
        )

    process_instance = ProcessInstanceModel.query.filter_by(
        id=active_task_assigned_to_me.process_instance_id
    ).first()
    process_model = get_process_model(
        process_instance.process_model_identifier,
        process_instance.process_group_identifier,
    )
    file_contents = SpecFileService.get_data(
        process_model, active_task_assigned_to_me.form_file_name
    )
    active_task_assigned_to_me.form_json = file_contents.decode("utf-8")

    return make_response(jsonify(active_task_assigned_to_me), 200)


def task_submit_user_data(
    task_id: int, body: Dict[str, Any]
) -> flask.wrappers.Response:
    """Task_submit_user_data."""
    print(f"body: {body}")
    print(f"task_id: {task_id}")
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def get_file_from_request() -> Any:
    """Get_file_from_request."""
    request_file = connexion.request.files.get("file")
    if not request_file:
        raise ApiError(
            code="no_file_given",
            message="Given request does not contain a file",
            status_code=400,
        )
    return request_file


def get_process_model(process_model_id: str, process_group_id: str) -> ProcessModelInfo:
    """Get_process_model."""
    process_model = None
    try:
        process_model = ProcessModelService().get_process_model(
            process_model_id, group_id=process_group_id
        )
    except ProcessEntityNotFoundError as exception:
        raise (
            ApiError(
                code="process_model_cannot_be_found",
                message=f"Process model cannot be found: {process_model_id}",
                status_code=400,
            )
        ) from exception

    return process_model
