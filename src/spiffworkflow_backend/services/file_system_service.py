"""File_system_service."""
import os
from datetime import datetime
from typing import List
from typing import Optional

import pytz
from flask import current_app
from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.file import CONTENT_TYPES
from spiffworkflow_backend.models.file import File
from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.process_model import ProcessModelInfo


class FileSystemService:
    """FileSystemService."""

    """ Simple Service meant for extension that provides some useful
    methods for dealing with the File system.
    """
    LIBRARY_SPECS = "Library Specs"
    STAND_ALONE_SPECS = "Stand Alone"
    MASTER_SPECIFICATION = "Master Specification"
    REFERENCE_FILES = "Reference Files"
    SPECIAL_FOLDERS = [LIBRARY_SPECS, MASTER_SPECIFICATION, REFERENCE_FILES]
    CAT_JSON_FILE = "process_group.json"
    WF_JSON_FILE = "workflow.json"

    @staticmethod
    def root_path() -> str:
        """Root_path."""
        # fixme: allow absolute files
        dir_name = current_app.config["BPMN_SPEC_ABSOLUTE_DIR"]
        app_root = current_app.root_path
        return os.path.join(app_root, "..", dir_name)

    @staticmethod
    def process_group_path(name: str) -> str:
        """Category_path."""
        return os.path.join(FileSystemService.root_path(), name)

    @staticmethod
    def library_path(name: str):
        """Library_path."""
        return os.path.join(
            FileSystemService.root_path(), FileSystemService.LIBRARY_SPECS, name
        )

    @staticmethod
    def process_group_path_for_spec(spec: ProcessModelInfo) -> str:
        """Category_path_for_spec."""
        if spec.is_master_spec:
            return os.path.join(FileSystemService.root_path())
        elif spec.library:
            process_group_path = FileSystemService.process_group_path(
                FileSystemService.LIBRARY_SPECS
            )
        elif spec.standalone:
            process_group_path = FileSystemService.process_group_path(
                FileSystemService.STAND_ALONE_SPECS
            )
        else:
            process_group_path = FileSystemService.process_group_path(
                spec.process_group_id
            )
        return process_group_path

    @staticmethod
    def workflow_path(spec: ProcessModelInfo) -> str:
        """Workflow_path."""
        if spec.is_master_spec:
            return os.path.join(
                FileSystemService.root_path(), FileSystemService.MASTER_SPECIFICATION
            )
        else:
            process_group_path = FileSystemService.process_group_path_for_spec(spec)
            return os.path.join(process_group_path, spec.id)

    def next_display_order(self, spec: ProcessModelInfo) -> int:
        """Next_display_order."""
        path = self.process_group_path_for_spec(spec)
        if os.path.exists(path):
            return len(next(os.walk(path))[1])
        else:
            return 0

    @staticmethod
    def write_file_data_to_system(file_path: str, file_data: bytes) -> None:
        """Write_file_data_to_system."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f_handle:
            f_handle.write(file_data)

    @staticmethod
    def get_extension(file_name: str) -> str:
        """Get_extension."""
        _, file_extension = os.path.splitext(file_name)
        return file_extension.lower().strip()[1:]

    @staticmethod
    def assert_valid_file_name(file_name: str) -> None:
        """Assert_valid_file_name."""
        file_extension = FileSystemService.get_extension(file_name)
        if file_extension not in FileType._member_names_:
            raise ApiError(
                "unknown_extension",
                "The file you provided does not have an accepted extension:"
                + file_extension,
                status_code=404,
            )

    @staticmethod
    def _timestamp(file_path: str) -> float:
        """_timestamp."""
        return os.path.getmtime(file_path)

    @staticmethod
    def _last_modified(file_path: str) -> datetime:
        """_last_modified."""
        # Returns the last modified date of the given file.
        timestamp = os.path.getmtime(file_path)
        utc_dt = datetime.utcfromtimestamp(timestamp)
        aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        return aware_utc_dt

    @staticmethod
    def file_type(file_name: str) -> FileType:
        """File_type."""
        extension = FileSystemService.get_extension(file_name)
        return FileType[extension]

    @staticmethod
    def _get_files(file_path: str, file_name: Optional[str] = None) -> List[File]:
        """Returns an array of File objects at the given path, can be restricted to just one file."""
        files = []
        items = os.scandir(file_path)
        for item in items:
            if item.is_file():
                if item.name.startswith("."):
                    continue  # Ignore hidden files
                if item.name == FileSystemService.WF_JSON_FILE:
                    continue  # Ignore the json files.
                if file_name is not None and item.name != file_name:
                    continue
                file = FileSystemService.to_file_object_from_dir_entry(item)
                files.append(file)
        return files

    @staticmethod
    def to_file_object(file_name: str, file_path: str) -> File:
        """To_file_object."""
        file_type = FileSystemService.file_type(file_name)
        content_type = CONTENT_TYPES[file_type.name]
        last_modified = FileSystemService._last_modified(file_path)
        size = os.path.getsize(file_path)
        file = File.from_file_system(
            file_name, file_type, content_type, last_modified, size
        )
        return file

    @staticmethod
    def to_file_object_from_dir_entry(item: os.DirEntry) -> File:
        """To_file_object_from_dir_entry."""
        extension = FileSystemService.get_extension(item.name)
        try:
            file_type = FileType[extension]
            content_type = CONTENT_TYPES[file_type.name]
        except KeyError as exception:
            raise ApiError(
                "invalid_type",
                f"Invalid File Type: {extension}, for file {item.name}",
            ) from exception
        stats = item.stat()
        file_size = stats.st_size
        last_modified = FileSystemService._last_modified(item.path)
        return File.from_file_system(
            item.name, file_type, content_type, last_modified, file_size
        )
