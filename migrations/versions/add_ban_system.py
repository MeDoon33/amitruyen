"""Add ban system to users

Revision ID: add_ban_system
Revises: add_comment_replies_reactions
Create Date: 2025-11-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ban_system'
down_revision = 'add_comment_replies_reactions'
branch_labels = None
depends_on = None


def upgrade():
    # Add ban-related columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_banned', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('ban_until', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('ban_reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('banned_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('banned_at', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('fk_users_banned_by', 'users', ['banned_by'], ['id'])


def downgrade():
    # Remove ban-related columns from users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_banned_by', type_='foreignkey')
        batch_op.drop_column('banned_at')
        batch_op.drop_column('banned_by')
        batch_op.drop_column('ban_reason')
        batch_op.drop_column('ban_until')
        batch_op.drop_column('is_banned')
