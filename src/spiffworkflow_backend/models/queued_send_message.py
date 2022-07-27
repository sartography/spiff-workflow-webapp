"""Principal."""
from dataclasses import dataclass

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey

from spiffworkflow_backend.models.process_instance import ProcessInstanceModel


@dataclass
class QueuedSendMessageModel(SpiffworkflowBaseDBModel):
    """Messages from a process instance that are ready to send to a receiving task."""

    __tablename__ = "queued_send_message"

    id = db.Column(db.Integer, primary_key=True)
    process_instance_id = db.Column(ForeignKey(ProcessInstanceModel.id), nullable=False)  # type: ignore
    bpmn_element_id = db.Column(db.String(50), nullable=False)
    correlation_name = db.Column(db.String(50), nullable=False)
    correlation_value = db.Column(db.String(50), nullable=False)
