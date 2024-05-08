"""Add article column to products table

Revision ID: 64e589a3ed65
Revises: 73831a91f9cc
Create Date: 2024-04-14 13:02:56.660740

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '64e589a3ed65'
down_revision = '73831a91f9cc'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем столбец article в таблицу products
    op.add_column('products', sa.Column('article', sa.String(), nullable=True))


def downgrade():
    # Удаляем столбец article из таблицы products при откате миграции
    op.drop_column('products', 'article')


def upgrade():
    op.create_table('products',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('article', sa.String(), nullable=True),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )

    op.create_table('items',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('request_history',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.Column('product_article', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id']),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('request_history')
    op.drop_table('items')
    op.drop_table('users')
    op.drop_table('products')
