"""create test_station table

Revision ID: 728ba13d0fad
Revises: 
Create Date: 2024-09-26 09:52:50.144753

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models import TestStation

# revision identifiers, used by Alembic.
revision: str = '728ba13d0fad'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        TestStation.__tablename__,
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('station_name', sa.String, nullable=False),
        sa.Column('station_description', sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table(TestStation.__tablename__)
