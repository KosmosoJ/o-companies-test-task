"""added search time

Revision ID: f66187060732
Revises: 280d97d28ed6
Create Date: 2024-07-18 13:33:52.290797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f66187060732'
down_revision: Union[str, None] = '280d97d28ed6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usersearches', sa.Column('searched_at', sa.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('usersearches', 'searched_at')
    # ### end Alembic commands ###
