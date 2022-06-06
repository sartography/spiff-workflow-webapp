"""Process_model."""
import marshmallow
from marshmallow import post_load
from marshmallow import Schema
from dataclasses import dataclass
from typing import List
import json

from spiffworkflow_backend.models.file import File


class ProcessModelInfo:
    """ProcessModelInfo."""

    def __init__(
        self,
        id,
        display_name,
        description,
        is_master_spec=False,
        standalone=False,
        library=False,
        primary_file_name="",
        primary_process_id="",
        libraries=None,
        process_group_id="",
        display_order=0,
        is_review=False,
        files=None,
    ):
        """__init__."""
        self.id = id  # Sting unique id
        self.display_name = display_name
        self.description = description
        self.display_order = display_order
        self.is_master_spec = is_master_spec
        self.standalone = standalone
        self.library = library
        self.primary_file_name = primary_file_name
        self.primary_process_id = primary_process_id
        self.is_review = is_review
        self.process_group_id = process_group_id

        if libraries is None:
            libraries = []
        self.libraries = libraries

        if files is None:
            files = []
        self.files = files

    def __eq__(self, other):
        """__eq__."""
        if not isinstance(other, ProcessModelInfo):
            return False
        if other.id == self.id:
            return True
        return False


class ProcessModelInfoSchema(Schema):
    """ProcessModelInfoSchema."""

    class Meta:
        """Meta."""

        model = ProcessModelInfo

    id = marshmallow.fields.String(required=True)
    display_name = marshmallow.fields.String(required=True)
    description = marshmallow.fields.String()
    is_master_spec = marshmallow.fields.Boolean(required=True)
    standalone = marshmallow.fields.Boolean(required=True)
    library = marshmallow.fields.Boolean(required=True)
    display_order = marshmallow.fields.Integer(allow_none=True)
    primary_file_name = marshmallow.fields.String(allow_none=True)
    primary_process_id = marshmallow.fields.String(allow_none=True)
    is_review = marshmallow.fields.Boolean(allow_none=True)
    process_group_id = marshmallow.fields.String(allow_none=True)
    libraries = marshmallow.fields.List(marshmallow.fields.String(), allow_none=True)
    files = marshmallow.fields.List(
        marshmallow.fields.Nested("FileSchema")
    )

    @post_load
    def make_spec(self, data, **kwargs):
        """Make_spec."""
        return ProcessModelInfo(**data)
