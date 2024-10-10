## Environment Setup

### Install Dependencies
- `brew install postgresql`
- Start Postgres by command `brew services start postgresql`
- Initialize venv by command `python3.12 -m venv ./postgres_venv`
- Setup dependency packages in requirements.txt
- `pip install -r requirements.txt`
- Config Python interpreter in Pycharm if the code sniffer is needed.

### Alembic Setup for Migrations
- login virtualenv 
- Connect to PostGreSQL prompt by command `psql postgres`
- Create db user and grant privileges
```bash
CREATE USER tsd_harbor WITH PASSWORD 'tsd_harbor';
CREATE DATABASE test_stations;
GRANT ALL PRIVILEGES ON DATABASE test_stations TO tsd_harbor;
```
- quit PostGreSQL prompt by command `\q`
- under project root, input command `alembic init alembic`
- Edit the alembic.ini file and set the sqlalchemy.url to your PostgreSQL database URL:
```ini
sqlalchemy.url = postgresql://tsd_harbor:tsd_harbor@localhost/test_stations
```
- Update the env.py file to include the Base class from your models:
```python
from database import Base

target_metadata = Base.metadata
```
- Implement models for `test_stations` table
```python
class TestStation(Base):
    __tablename__ = "test_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    station_name = Column(String, nullable=False)
    station_description = Column(String, nullable=True)
```
- Fill the `upgrade()` and `downgrade()` methods in the first revision of alembic.
```python
def upgrade() -> None:
    op.create_table(
        TestStation.__tablename__,
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('station_name', sa.String, nullable=False),
        sa.Column('station_description', sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table(TestStation.__tablename__)
```
- Create the Initial Migration
```bash
alembic revision --autogenerate -m "create test_station table"
alembic upgrade head
```
- Write the schema for test_stations

## Test App

### Run FastAPI App
- Implement endpoints 
- `uvicorn main:app --reload`

### Test Database before
- Connect to PostGreSQL prompt by command `psql postgres`
- `\du` to list all Roles, and see whether `tsd_harbor` user had been created successfully.
- `\l` to list all databases, and see whether `test_stations` database had been created successfully.
- `\c test_stations` connected to database.
- `\d test_stations` make sure it is empty.

### Add a Station from Postman
- Send a `POST http://localhost:8000/stations/` request from Postman with Json payload
```json
{
  "station_name": "RF",
  "station_description": "This is a RF station."
}
```
- Received a response message for confirmation of station created.
```json
{
  "station_name": "RF",
  "station_description": "This is a RF station.",
  "id": "3e900584-b7ab-4e57-81eb-16916623a24a"
}
```

### Test Database after
- Connect to PostGreSQL prompt by command `psql -d test_stations -U tsd_harbor`
- Check User Roles: `\du` to list all Roles
```text
                                    List of roles
 Role name  |                         Attributes                         | Member of 
------------+------------------------------------------------------------+-----------
 danielwong | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
 tsd_harbor |                                                            | {}

```
- Check Databases: `\l` to list all databases
```text
                                  List of databases
     Name      |   Owner    | Encoding | Collate | Ctype |     Access privileges     
---------------+------------+----------+---------+-------+---------------------------
 postgres      | danielwong | UTF8     | C       | C     | 
 template0     | danielwong | UTF8     | C       | C     | =c/danielwong            +
               |            |          |         |       | danielwong=CTc/danielwong
 template1     | danielwong | UTF8     | C       | C     | =c/danielwong            +
               |            |          |         |       | danielwong=CTc/danielwong
 test_stations | danielwong | UTF8     | C       | C     | =Tc/danielwong           +
               |            |          |         |       | danielwong=CTc/danielwong+
               |            |          |         |       | tsd_harbor=CTc/danielwong

```
- `\c test_stations` connected to database.
- `\dt` list relations.
```text
               List of relations
 Schema |      Name       | Type  |   Owner    
--------+-----------------+-------+------------
 public | alembic_version | table | tsd_harbor
 public | test_stations   | table | tsd_harbor
(2 rows)
```
- use `SELECT * FROM test_stations;` to check whether record added successfully
```text
                  id                  | station_name |  station_description  
--------------------------------------+--------------+-----------------------
 3e900584-b7ab-4e57-81eb-16916623a24a | RF           | This is a RF station.
(1 row)
```
> [Note:] When use SQL sentences in cmdline, remember to use `;` after each sentence.

### Add Database Trigger
- Add an alembic revision by `alembic`(refer to the code)
- Add Database Trigger in `upgrade()` and `downgrade()`(refer to the code)
- Check whether Database Trigger created successfully
```bash
SELECT event_object_table, trigger_name, action_timing, event_manipulation
FROM information_schema.triggers
WHERE event_object_table = 'test_stations';

 event_object_table |      trigger_name       | action_timing | event_manipulation 
--------------------+-------------------------+---------------+--------------------
 test_stations      | station_trigger         | AFTER         | INSERT
 test_stations      | station_trigger         | AFTER         | UPDATE
 test_stations      | station_deleted_trigger | AFTER         | DELETE
(3 rows)
```
- Check whether Database Trigger had been correctly mapped to corresponding method
```bash
SELECT tgname, tgfoid::regprocedure::text AS function_name, tgtype
FROM pg_trigger
WHERE tgrelid = 'test_stations'::regclass;

         tgname          |       function_name       | tgtype 
-------------------------+---------------------------+--------
 station_trigger         | notify_station_event()    |     21
 station_deleted_trigger | notify_station_deletion() |      9
(2 rows)
```
- Execute `pg_notify` manually
```bash
SELECT pg_notify('STATION_CREATED', '{"station_id": 1, "station_name": "RF"}');
```

### Test Database Trigger

- Launch FastAPI app
```bash
python main.py
```

- Launch db_logger
```bash
python  db_logger.py
```

- Use Postman send a request:
```http request
POST http://localhost:8000/stations/
```
with payload
```json
{
  "station_name": "RF",
  "station_description": "This is a RF station."
}
```

- Then you'll see the notification handler code had been carried out.
```bash
2024-10-10 07:23:36,211 - INFO - Station Created: {'id': 'c765dd3f-4a75-4902-b41c-1d32ecf26eb0', 'station_name': 'RF-4', 'station_description': 'This is a RF station.'}
```
