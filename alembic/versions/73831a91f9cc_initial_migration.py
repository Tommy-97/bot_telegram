"""Initial migration

Revision ID: 73831a91f9cc
Revises: 
Create Date: 2024-04-13 14:53:58.762449

"""
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

from alembic import op

# revision identifiers, used by Alembic.
revision = '73831a91f9cc'
down_revision = None
branch_labels = None
depends_on = None



def upgrade():
    inspector = Inspector.from_engine(op.get_bind())

    # Check if the table exists before creating it
    if 'products' not in inspector.get_table_names():
        op.create_table('products',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('name', sa.String(), nullable=True),
                        sa.Column('article', sa.String(), nullable=True),
                        sa.Column('price', sa.Float(), nullable=True),
                        sa.Column('rating', sa.Float(), nullable=True),
                        sa.Column('quantity', sa.Integer(), nullable=True),
                        sa.PrimaryKeyConstraint('id')
                        )
        
        
    
    # Create tables if they don't exist before attempting to drop them
    if 'users' not in inspector.get_table_names():
        op.create_table('users',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('name', sa.String(), nullable=True),
                        sa.Column('email', sa.String(), nullable=True),
                        sa.Column('created_at', sa.DateTime(), nullable=True),
                        sa.PrimaryKeyConstraint('id'),
                        sa.UniqueConstraint('email')
                        )

    if 'items' not in inspector.get_table_names():
        op.create_table('items',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('name', sa.String(), nullable=False),
                        sa.Column('description', sa.String(), nullable=True),
                        sa.Column('created_at', sa.DateTime(), nullable=True),
                        sa.PrimaryKeyConstraint('id'),
                        sa.UniqueConstraint('name')
                        )

    if 'request_history' not in inspector.get_table_names():
        op.create_table('request_history',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.Integer(), nullable=True),
                        sa.Column('timestamp', sa.DateTime(), nullable=True),
                        sa.Column('product_article', sa.String(), nullable=True),
                        sa.PrimaryKeyConstraint('id'),
                        sa.ForeignKeyConstraint(['user_id'], ['users.id'])  # Add Foreign Key Constraint if needed
                        )


def downgrade():
    op.drop_table('request_history')
    op.drop_table('items')
    op.drop_table('users')
    op.drop_table('products')
