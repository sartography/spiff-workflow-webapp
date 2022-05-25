"""User."""
from typing import Any

from flask_bpmn.models.db import db

from spiff_workflow_webapp.models.process_group import ProcessGroupModel
from spiff_workflow_webapp.models.user import UserModel


def find_or_create_user(username: str = "test_user1") -> Any:
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        user = UserModel(username=username)
        db.session.add(user)
        db.session.commit()

    return user


def find_or_create_process_group(name: str = "test_group1") -> Any:
    process_group = ProcessGroupModel.query.filter_by(name=name).first()
    if process_group is None:
        process_group = ProcessGroupModel(name=name)
        db.session.add(process_group)
        db.session.commit()

    return process_group
