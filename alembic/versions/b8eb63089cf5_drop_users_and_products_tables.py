"""Drop users and products tables

Revision ID: b8eb63089cf5
Revises: 64e589a3ed65
Create Date: 2024-04-14 13:18:14.361229

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b8eb63089cf5'
down_revision = '64e589a3ed65'
branch_labels = None
depends_on = None


def upgrade():
    # Проверяем отсутствие таблиц перед их созданием
    inspector = sa.inspect(op.get_bind().engine)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        op.create_table('users',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('name', sa.String(), nullable=True),
                        sa.Column('email', sa.String(), nullable=True),
                        sa.Column('created_at', sa.DateTime(), nullable=True),
                        sa.PrimaryKeyConstraint('id'),
                        sa.UniqueConstraint('email')
                        )

    if 'products' not in tables:
        op.create_table('products',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('name', sa.String(), nullable=True),
                        sa.Column('article', sa.String(), nullable=True),
                        sa.Column('price', sa.Float(), nullable=True),
                        sa.Column('rating', sa.Float(), nullable=True),
                        sa.Column('quantity', sa.Integer(), nullable=True),
                        sa.PrimaryKeyConstraint('id')
                        )

