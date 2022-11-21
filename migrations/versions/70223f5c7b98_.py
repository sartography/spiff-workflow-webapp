"""empty message

Revision ID: 70223f5c7b98
Revises: 
Create Date: 2022-11-20 19:54:45.061376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70223f5c7b98'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('identifier', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_model_identifier'), 'message_model', ['identifier'], unique=True)
    op.create_index(op.f('ix_message_model_name'), 'message_model', ['name'], unique=True)
    op.create_table('permission_target',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uri', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uri')
    )
    op.create_table('spec_reference_cache',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=255), nullable=True),
    sa.Column('process_model_id', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=255), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('relative_path', sa.String(length=255), nullable=True),
    sa.Column('has_lanes', sa.Boolean(), nullable=True),
    sa.Column('is_executable', sa.Boolean(), nullable=True),
    sa.Column('is_primary', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('identifier', 'type', name='_identifier_type_unique')
    )
    op.create_index(op.f('ix_spec_reference_cache_display_name'), 'spec_reference_cache', ['display_name'], unique=False)
    op.create_index(op.f('ix_spec_reference_cache_identifier'), 'spec_reference_cache', ['identifier'], unique=False)
    op.create_index(op.f('ix_spec_reference_cache_type'), 'spec_reference_cache', ['type'], unique=False)
    op.create_table('spiff_logging',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_instance_id', sa.Integer(), nullable=False),
    sa.Column('bpmn_process_identifier', sa.String(length=255), nullable=False),
    sa.Column('bpmn_task_identifier', sa.String(length=255), nullable=False),
    sa.Column('bpmn_task_name', sa.String(length=255), nullable=True),
    sa.Column('bpmn_task_type', sa.String(length=255), nullable=True),
    sa.Column('spiff_task_guid', sa.String(length=50), nullable=False),
    sa.Column('timestamp', sa.DECIMAL(precision=17, scale=6), nullable=False),
    sa.Column('message', sa.String(length=255), nullable=True),
    sa.Column('current_user_id', sa.Integer(), nullable=True),
    sa.Column('spiff_step', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('uid', sa.String(length=50), nullable=True),
    sa.Column('service', sa.String(length=50), nullable=False),
    sa.Column('service_id', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('service', 'service_id', name='service_key'),
    sa.UniqueConstraint('uid'),
    sa.UniqueConstraint('username')
    )
    op.create_table('message_correlation_property',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=50), nullable=True),
    sa.Column('message_model_id', sa.Integer(), nullable=False),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_model_id'], ['message_model.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('identifier', 'message_model_id', name='message_correlation_property_unique')
    )
    op.create_index(op.f('ix_message_correlation_property_identifier'), 'message_correlation_property', ['identifier'], unique=False)
    op.create_table('message_triggerable_process_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_model_id', sa.Integer(), nullable=False),
    sa.Column('process_model_identifier', sa.String(length=50), nullable=False),
    sa.Column('process_group_identifier', sa.String(length=50), nullable=False),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_model_id'], ['message_model.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_model_id')
    )
    op.create_index(op.f('ix_message_triggerable_process_model_process_group_identifier'), 'message_triggerable_process_model', ['process_group_identifier'], unique=False)
    op.create_index(op.f('ix_message_triggerable_process_model_process_model_identifier'), 'message_triggerable_process_model', ['process_model_identifier'], unique=False)
    op.create_table('principal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('NOT(user_id IS NULL AND group_id IS NULL)'),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('group_id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('process_instance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_model_identifier', sa.String(length=255), nullable=False),
    sa.Column('process_group_identifier', sa.String(length=50), nullable=False),
    sa.Column('process_initiator_id', sa.Integer(), nullable=False),
    sa.Column('bpmn_json', sa.JSON(), nullable=True),
    sa.Column('start_in_seconds', sa.Integer(), nullable=True),
    sa.Column('end_in_seconds', sa.Integer(), nullable=True),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('bpmn_version_control_type', sa.String(length=50), nullable=True),
    sa.Column('bpmn_version_control_identifier', sa.String(length=255), nullable=True),
    sa.Column('spiff_step', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['process_initiator_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_process_instance_process_group_identifier'), 'process_instance', ['process_group_identifier'], unique=False)
    op.create_index(op.f('ix_process_instance_process_model_identifier'), 'process_instance', ['process_model_identifier'], unique=False)
    op.create_table('process_instance_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=50), nullable=False),
    sa.Column('report_metadata', sa.JSON(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('created_by_id', 'identifier', name='process_instance_report_unique')
    )
    op.create_index(op.f('ix_process_instance_report_created_by_id'), 'process_instance_report', ['created_by_id'], unique=False)
    op.create_index(op.f('ix_process_instance_report_identifier'), 'process_instance_report', ['identifier'], unique=False)
    op.create_table('refresh_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=1024), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('secret',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('spiff_step_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_instance_id', sa.Integer(), nullable=False),
    sa.Column('spiff_step', sa.Integer(), nullable=False),
    sa.Column('task_json', sa.JSON(), nullable=False),
    sa.Column('timestamp', sa.DECIMAL(precision=17, scale=6), nullable=False),
    sa.Column('completed_by_user_id', sa.Integer(), nullable=True),
    sa.Column('lane_assignment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lane_assignment_id'], ['group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_group_assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'group_id', name='user_group_assignment_unique')
    )
    op.create_table('active_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_instance_id', sa.Integer(), nullable=False),
    sa.Column('actual_owner_id', sa.Integer(), nullable=True),
    sa.Column('lane_assignment_id', sa.Integer(), nullable=True),
    sa.Column('form_file_name', sa.String(length=50), nullable=True),
    sa.Column('ui_form_file_name', sa.String(length=50), nullable=True),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.String(length=50), nullable=True),
    sa.Column('task_name', sa.String(length=50), nullable=True),
    sa.Column('task_title', sa.String(length=50), nullable=True),
    sa.Column('task_type', sa.String(length=50), nullable=True),
    sa.Column('task_status', sa.String(length=50), nullable=True),
    sa.Column('process_model_display_name', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['actual_owner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['lane_assignment_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['process_instance_id'], ['process_instance.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id', 'process_instance_id', name='active_task_unique')
    )
    op.create_table('message_correlation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_instance_id', sa.Integer(), nullable=False),
    sa.Column('message_correlation_property_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('value', sa.String(length=255), nullable=False),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_correlation_property_id'], ['message_correlation_property.id'], ),
    sa.ForeignKeyConstraint(['process_instance_id'], ['process_instance.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('process_instance_id', 'message_correlation_property_id', 'name', name='message_instance_id_name_unique')
    )
    op.create_index(op.f('ix_message_correlation_message_correlation_property_id'), 'message_correlation', ['message_correlation_property_id'], unique=False)
    op.create_index(op.f('ix_message_correlation_name'), 'message_correlation', ['name'], unique=False)
    op.create_index(op.f('ix_message_correlation_process_instance_id'), 'message_correlation', ['process_instance_id'], unique=False)
    op.create_index(op.f('ix_message_correlation_value'), 'message_correlation', ['value'], unique=False)
    op.create_table('message_instance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_instance_id', sa.Integer(), nullable=False),
    sa.Column('message_model_id', sa.Integer(), nullable=False),
    sa.Column('message_type', sa.String(length=20), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('failure_cause', sa.Text(), nullable=True),
    sa.Column('updated_at_in_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at_in_seconds', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_model_id'], ['message_model.id'], ),
    sa.ForeignKeyConstraint(['process_instance_id'], ['process_instance.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('permission_assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('principal_id', sa.Integer(), nullable=False),
    sa.Column('permission_target_id', sa.Integer(), nullable=False),
    sa.Column('grant_type', sa.String(length=50), nullable=False),
    sa.Column('permission', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['permission_target_id'], ['permission_target.id'], ),
    sa.ForeignKeyConstraint(['principal_id'], ['principal.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('principal_id', 'permission_target_id', 'permission', name='permission_assignment_uniq')
    )
    op.create_table('active_task_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('active_task_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['active_task_id'], ['active_task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('active_task_id', 'user_id', name='active_task_user_unique')
    )
    op.create_index(op.f('ix_active_task_user_active_task_id'), 'active_task_user', ['active_task_id'], unique=False)
    op.create_index(op.f('ix_active_task_user_user_id'), 'active_task_user', ['user_id'], unique=False)
    op.create_table('message_correlation_message_instance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_instance_id', sa.Integer(), nullable=False),
    sa.Column('message_correlation_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['message_correlation_id'], ['message_correlation.id'], ),
    sa.ForeignKeyConstraint(['message_instance_id'], ['message_instance.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_instance_id', 'message_correlation_id', name='message_correlation_message_instance_unique')
    )
    op.create_index(op.f('ix_message_correlation_message_instance_message_correlation_id'), 'message_correlation_message_instance', ['message_correlation_id'], unique=False)
    op.create_index(op.f('ix_message_correlation_message_instance_message_instance_id'), 'message_correlation_message_instance', ['message_instance_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_message_correlation_message_instance_message_instance_id'), table_name='message_correlation_message_instance')
    op.drop_index(op.f('ix_message_correlation_message_instance_message_correlation_id'), table_name='message_correlation_message_instance')
    op.drop_table('message_correlation_message_instance')
    op.drop_index(op.f('ix_active_task_user_user_id'), table_name='active_task_user')
    op.drop_index(op.f('ix_active_task_user_active_task_id'), table_name='active_task_user')
    op.drop_table('active_task_user')
    op.drop_table('permission_assignment')
    op.drop_table('message_instance')
    op.drop_index(op.f('ix_message_correlation_value'), table_name='message_correlation')
    op.drop_index(op.f('ix_message_correlation_process_instance_id'), table_name='message_correlation')
    op.drop_index(op.f('ix_message_correlation_name'), table_name='message_correlation')
    op.drop_index(op.f('ix_message_correlation_message_correlation_property_id'), table_name='message_correlation')
    op.drop_table('message_correlation')
    op.drop_table('active_task')
    op.drop_table('user_group_assignment')
    op.drop_table('spiff_step_details')
    op.drop_table('secret')
    op.drop_table('refresh_token')
    op.drop_index(op.f('ix_process_instance_report_identifier'), table_name='process_instance_report')
    op.drop_index(op.f('ix_process_instance_report_created_by_id'), table_name='process_instance_report')
    op.drop_table('process_instance_report')
    op.drop_index(op.f('ix_process_instance_process_model_identifier'), table_name='process_instance')
    op.drop_index(op.f('ix_process_instance_process_group_identifier'), table_name='process_instance')
    op.drop_table('process_instance')
    op.drop_table('principal')
    op.drop_index(op.f('ix_message_triggerable_process_model_process_model_identifier'), table_name='message_triggerable_process_model')
    op.drop_index(op.f('ix_message_triggerable_process_model_process_group_identifier'), table_name='message_triggerable_process_model')
    op.drop_table('message_triggerable_process_model')
    op.drop_index(op.f('ix_message_correlation_property_identifier'), table_name='message_correlation_property')
    op.drop_table('message_correlation_property')
    op.drop_table('user')
    op.drop_table('spiff_logging')
    op.drop_index(op.f('ix_spec_reference_cache_type'), table_name='spec_reference_cache')
    op.drop_index(op.f('ix_spec_reference_cache_identifier'), table_name='spec_reference_cache')
    op.drop_index(op.f('ix_spec_reference_cache_display_name'), table_name='spec_reference_cache')
    op.drop_table('spec_reference_cache')
    op.drop_table('permission_target')
    op.drop_index(op.f('ix_message_model_name'), table_name='message_model')
    op.drop_index(op.f('ix_message_model_identifier'), table_name='message_model')
    op.drop_table('message_model')
    op.drop_table('group')
    # ### end Alembic commands ###
