"""Add notify_station_event trigger

Revision ID: 9435e0c2a3f2
Revises: 728ba13d0fad
Create Date: 2024-09-26 10:22:50.934783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9435e0c2a3f2'
down_revision: Union[str, None] = '728ba13d0fad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建函数
    op.execute("""
    CREATE OR REPLACE FUNCTION notify_station_event() RETURNS trigger AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                RAISE NOTICE 'STATION CREATED: %', row_to_json(NEW);
                PERFORM pg_notify('STATION_CREATED', row_to_json(NEW)::text);
                RETURN NEW;
            END IF;
            IF (TG_OP = 'UPDATE') THEN
                RAISE NOTICE 'STATION UPDATED: %', row_to_json(NEW);
                PERFORM pg_notify('STATION_UPDATED', row_to_json(NEW)::text);
                RETURN NEW;
            END IF;
            RETURN NULL; 
        END;
    $$ LANGUAGE plpgsql;
    """)

    # 创建触发器
    op.execute("""
    CREATE TRIGGER station_trigger
    AFTER INSERT OR UPDATE ON test_stations
        FOR EACH ROW EXECUTE FUNCTION notify_station_event();
    """)

    # 创建函数
    op.execute("""
        CREATE OR REPLACE FUNCTION notify_station_deletion() RETURNS TRIGGER AS $$
            BEGIN
                PERFORM pg_notify('STATION_DELETED', row_to_json(OLD)::text);
                RETURN OLD;
            END;
        $$ LANGUAGE plpgsql;
        """)

    # 创建触发器
    op.execute("""
        CREATE TRIGGER station_deleted_trigger
        AFTER DELETE ON test_stations
            FOR EACH ROW EXECUTE FUNCTION notify_station_deletion();
        """)


def downgrade() -> None:
    # 删除触发器
    op.execute("DROP TRIGGER IF EXISTS station_trigger ON test_stations;")
    op.execute("DROP TRIGGER IF EXISTS station_deleted_trigger ON test_stations;")

    # 删除函数
    op.execute("DROP FUNCTION IF EXISTS notify_station_event();")
    op.execute("DROP FUNCTION IF EXISTS notify_station_deletion();")
