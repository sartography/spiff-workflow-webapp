"""File."""
import enum
from dataclasses import dataclass
from dataclasses import field
from typing import Optional

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from marshmallow import INCLUDE
from marshmallow import Schema
from sqlalchemy import func
from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from spiffworkflow_backend.models.data_store import DataStoreModel


class FileModel(SpiffworkflowBaseDBModel):
    """FileModel."""

    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    process_instance_id = db.Column(
        db.Integer, db.ForeignKey("process_instance.id"), nullable=True
    )
    task_spec = db.Column(db.String(50), nullable=True)
    irb_doc_code = db.Column(
        db.String(50), nullable=False
    )  # Code reference to the documents.xlsx reference file.
    data_stores = relationship(DataStoreModel, cascade="all,delete", backref="file")
    md5_hash = db.Column(db.String(50), unique=False, nullable=False)
    data = deferred(db.Column(db.LargeBinary))  # Don't load it unless you have to.
    size = db.Column(db.Integer, default=0)
    date_modified = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_uid = db.Column(db.String(50), db.ForeignKey("user.uid"), nullable=True)
    archived = db.Column(db.Boolean, default=False)


class FileType(enum.Enum):
    """FileType."""

    bpmn = "bpmn"
    csv = "csv"
    dmn = "dmn"
    doc = "doc"
    docx = "docx"
    gif = "gif"
    jpg = "jpg"
    md = "md"
    pdf = "pdf"
    png = "png"
    ppt = "ppt"
    pptx = "pptx"
    rtf = "rtf"
    svg = "svg"
    svg_xml = "svg+xml"
    txt = "txt"
    xls = "xls"
    xlsx = "xlsx"
    xml = "xml"
    zip = "zip"


CONTENT_TYPES = {
    "bpmn": "text/xml",
    "csv": "text/csv",
    "dmn": "text/xml",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "gif": "image/gif",
    "jpg": "image/jpeg",
    "md": "text/plain",
    "pdf": "application/pdf",
    "png": "image/png",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "rtf": "application/rtf",
    "svg": "image/svg+xml",
    "svg_xml": "image/svg+xml",
    "txt": "text/plain",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xml": "application/xml",
    "zip": "application/zip",
}


@dataclass(order=True)
class File:
    """File."""

    sort_index: str = field(init=False)

    content_type: str
    name: str
    type: str
    document: dict
    last_modified: str
    size: int
    process_instance_id: Optional[int] = None
    irb_doc_code: Optional[str] = None
    data_store: Optional[dict] = field(default_factory=dict)
    user_uid: Optional[str] = None
    file_contents: Optional[str] = None
    process_model_id: Optional[str] = None
    process_group_id: Optional[str] = None
    archived: bool = False

    def __post_init__(self):
        """__post_init__."""
        self.sort_index = f"{self.type}:{self.name}"

    @classmethod
    def from_file_system(
        cls, file_name, file_type, content_type, last_modified, file_size
    ):
        """From_file_system."""
        instance = cls(
            name=file_name,
            content_type=content_type,
            type=file_type.value,
            document={},
            last_modified=last_modified,
            size=file_size,
        )
        return instance


class FileSchema(Schema):
    """FileSchema."""

    class Meta:
        """Meta."""

        model = File
        fields = [
            "id",
            "name",
            "content_type",
            "process_instance_id",
            "irb_doc_code",
            "last_modified",
            "type",
            "archived",
            "size",
            "data_store",
            "document",
            "user_uid",
            "url",
            "file_contents",
            "process_model_id",
            "process_group_id",
        ]
        unknown = INCLUDE

    # url = Method("get_url")
    #
    # def get_url(self, obj):
    #     token = 'not_available'
    #     if hasattr(obj, 'id') and obj.id is not None:
    #         file_url = url_for("/v1_0.crc_api_file_get_file_data_link", file_id=obj.id, _external=True)
    #         if hasattr(flask.g, 'user'):
    #             token = flask.g.user.encode_auth_token()
    #         url = file_url + '?auth_token=' + urllib.parse.quote_plus(token)
    #         return url
    #     else:
    #         return ""
    #
