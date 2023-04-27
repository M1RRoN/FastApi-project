"""add token

Revision ID: 225d83688f4d
Revises: f885bf20b7dc
Create Date: 2023-04-26 23:00:16.984746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '225d83688f4d'
down_revision = 'f885bf20b7dc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_images_filename', table_name='images')
    op.drop_index('ix_images_id', table_name='images')
    op.drop_table('images')
    op.drop_index('ix_blacklist_tokens_id', table_name='blacklist_tokens')
    op.drop_index('ix_blacklist_tokens_token', table_name='blacklist_tokens')
    op.drop_table('blacklist_tokens')
    op.drop_index('ix_projects_description', table_name='projects')
    op.drop_index('ix_projects_id', table_name='projects')
    op.drop_index('ix_projects_title', table_name='projects')
    op.drop_table('projects')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(), nullable=True),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('owner_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_title', 'projects', ['title'], unique=False)
    op.create_index('ix_projects_id', 'projects', ['id'], unique=False)
    op.create_index('ix_projects_description', 'projects', ['description'], unique=False)
    op.create_table('blacklist_tokens',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('token', sa.VARCHAR(length=255), nullable=True),
    sa.Column('blacklisted_at', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_blacklist_tokens_token', 'blacklist_tokens', ['token'], unique=False)
    op.create_index('ix_blacklist_tokens_id', 'blacklist_tokens', ['id'], unique=False)
    op.create_table('images',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('filename', sa.VARCHAR(), nullable=True),
    sa.Column('project_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_images_id', 'images', ['id'], unique=False)
    op.create_index('ix_images_filename', 'images', ['filename'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.Column('is_superuser', sa.BOOLEAN(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    # ### end Alembic commands ###
