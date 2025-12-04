"""add comment replies and reactions

Revision ID: add_comment_replies_reactions
Revises: 6a9ef31bcf54
Create Date: 2025-11-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_comment_replies_reactions'
down_revision = '6a9ef31bcf54'  # Latest migration - add_is_hidden_field_to_comment_model
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to comments table
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('dislikes_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.create_foreign_key('fk_comment_parent', 'comments', ['parent_id'], ['id'])
    
    # Create comment_reactions table
    op.create_table('comment_reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('reaction_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_reaction')
    )


def downgrade():
    # Drop comment_reactions table
    op.drop_table('comment_reactions')
    
    # Remove columns from comments table
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comment_parent', type_='foreignkey')
        batch_op.drop_column('dislikes_count')
        batch_op.drop_column('likes_count')
        batch_op.drop_column('parent_id')
