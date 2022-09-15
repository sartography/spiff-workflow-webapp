"""Test_secret_service."""
import pytest

from flask.app import Flask
from flask.testing import FlaskClient
from flask_bpmn.api.api_error import ApiError
from spiffworkflow_backend.services.file_system_service import FileSystemService
from spiffworkflow_backend.services.process_model_service import ProcessModelService

from tests.spiffworkflow_backend.helpers.base_test import BaseTest

from spiffworkflow_backend.models.secret_model import SecretModel, SecretAllowedProcessPathModel
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.secret_service import SecretService


class TestSecretService(BaseTest):
    """TestSecretService."""

    test_key = "test_key"
    test_value = "test_value"
    test_process_group_id = "test"
    test_process_group_display_name = "My Test Process Group"
    test_process_model_id = "make_cookies"
    test_process_model_display_name = "Cooooookies"
    test_process_model_description = "Om nom nom delicious cookies"

    def add_test_secret(self, user: UserModel) -> SecretModel:
        """Add_test_secret."""
        return SecretService().add_secret(self.test_key, self.test_value, user.id)

    def add_test_process(self, client, user):
        self.create_process_group(
            client, user, self.test_process_group_id, display_name=self.test_process_group_display_name
        )
        self.create_process_model_with_api(
            client,
            process_group_id=self.test_process_group_id,
            process_model_id=self.test_process_model_id,
            process_model_display_name=self.test_process_model_display_name,
            process_model_description=self.test_process_model_description,
        )
        process_model_info = ProcessModelService().get_process_model(
            self.test_process_model_id, self.test_process_group_id
        )
        return process_model_info

    def test_add_secret(self, app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
        """Test_add_secret."""
        user = self.find_or_create_user()
        test_secret = self.add_test_secret(user)

        assert test_secret is not None
        assert test_secret.key == self.test_key
        assert test_secret.value == self.test_value
        assert test_secret.creator_user_id == user.id

    def test_add_secret_duplicate_key_fails(self, app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
        user = self.find_or_create_user()
        self.add_test_secret(user)
        with pytest.raises(ApiError) as ae:
            self.add_test_secret(user)
        assert "Duplicate entry" in ae.value.message

    def test_get_secret(self, app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
        """Test_get_secret."""
        user = self.find_or_create_user()
        self.add_test_secret(user)

        secret = SecretService().get_secret(self.test_key)
        assert secret is not None
        assert secret == self.test_value

    def test_get_secret_bad_key(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_get_secret_bad_service."""
        user = self.find_or_create_user()
        self.add_test_secret(user)

        bad_secret = SecretService().get_secret("bad_key")
        assert bad_secret is None

    def test_secret_add_allowed_process(
        self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_secret_add_allowed_process."""
        user = self.find_or_create_user()
        process_model_info = self.add_test_process(client, user)
        process_model_relative_path = FileSystemService.process_model_relative_path(
            process_model_info
        )

        test_secret = self.add_test_secret(user)
        allowed_process_model = SecretService().add_allowed_process(
            key=test_secret.key, user_id=user.id, allowed_relative_path=process_model_relative_path
        )
        assert allowed_process_model is not None
        assert isinstance(allowed_process_model, SecretAllowedProcessPathModel)
        assert allowed_process_model.secret_id == test_secret.id
        assert (
            allowed_process_model.allowed_relative_path == process_model_relative_path
        )

        assert len(test_secret.allowed_processes) == 1
        assert test_secret.allowed_processes[0] == allowed_process_model

    def test_secret_add_allowed_process_bad_user(
        self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        user = self.find_or_create_user()
        process_model_info = self.add_test_process(client, user)
        process_model_relative_path = FileSystemService.process_model_relative_path(
            process_model_info
        )
        test_secret = self.add_test_secret(user)
        with pytest.raises(ApiError) as ae:
            SecretService().add_allowed_process(
                key=test_secret.key, user_id=user.id+1, allowed_relative_path=process_model_relative_path
            )
        assert ae.value.message == f"User: {user.id+1} cannot modify the secret with key : test_key"

    def test_update_secret(self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None) -> None:
        """Test update secret."""
        user = self.find_or_create_user()
        self.add_test_secret(user)
        secret = SecretService.get_secret(self.test_key)
        assert secret == self.test_value
        SecretService.update_secret(self.test_key, 'new_secret_value', user.id)
        new_secret = SecretService.get_secret(self.test_key)
        assert new_secret == 'new_secret_value'

    def test_update_secret_bad_user(self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None) -> None:
        user = self.find_or_create_user()
        self.add_test_secret(user)
        with pytest.raises(ApiError) as ae:
            SecretService.update_secret(self.test_key, 'new_secret_value', user.id+1)
        assert ae.value.message == f"User: {user.id+1} cannot update the secret with key : test_key"

    def test_delete_secret(
        self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test delete secret."""
        user = self.find_or_create_user()
        self.add_test_secret(user)
        secrets = SecretModel.query.all()
        assert len(secrets) == 1
        assert secrets[0].creator_user_id == user.id
        SecretService.delete_secret(self.test_key, user.id)
        secrets = SecretModel.query.all()
        assert len(secrets) == 0

    def test_delete_secret_bad_user(self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None):
        user = self.find_or_create_user()
        self.add_test_secret(user)
        with pytest.raises(ApiError) as ae:
            SecretService.delete_secret(self.test_key, user.id+1)
        assert ae.value.message == f"User: {user.id+1} cannot delete the secret with key : test_key"



# class TestSecretServiceApi(BaseTest):
#     """TestSecretServiceApi."""
#
#     test_service = "test_service"
#     test_client = "test_client"
#     test_key = "1234567890"
#
#     def test_add_secret(
#         self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
#     ) -> None:
#         """Test_add_secret."""
#         user = self.find_or_create_user()
#         secret_model = SecretModel(
#             service=self.test_service,
#             client=self.test_client,
#             key=self.test_key,
#             creator_user_id=user.id,
#         )
#         # data = json.dumps({"service": self.test_service,
#         #                    "client": self.test_client,
#         #                    "key": self.test_key})
#         data = json.dumps(SecretModelSchema().dump(secret_model))
#         response = client.post(
#             "/v1.0/secrets",
#             headers=self.logged_in_headers(user),
#             content_type="application/json",
#             data=data,
#         )
#         print(response)
#
#     def test_get_secret(
#         self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
#     ) -> None:
#         """Test get secret."""
#         ...
#
#     def test_delete_secret(
#         self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
#     ) -> None:
#         """Test delete secret."""
#         ...
