"""Tabla Plato Categoria

Revision ID: 8784df9cbdda
Revises: f905d37d7cdb
Create Date: 2025-06-16 19:05:54.385553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '8784df9cbdda'
down_revision: Union[str, None] = 'f905d37d7cdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('platoscategoria',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('platoscategoria')
    # ### end Alembic commands ###
