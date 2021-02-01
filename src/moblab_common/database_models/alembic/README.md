Alembic is a tool that works with SQLAlchemy to help manage schema migrations.
=================================
Main functionality:
 * maintains current schema version;
 * maintain a list of schema migrations;
 * roll out and roll back schema changes (A.k.a. apply migrations);
 * auto-generate migration scripts from SQLAlchemy models and current db schema;

Generate schema migration
---------------------------------
Alembic uses the same declarative class definitions (or simply db models)
as sqlalchemy to find the differences between your new schema defined in code
and running db.

Follow this steps to create a new revision:
1) Implement the desirable db models changes;

2) Make sure your db is running in a container and 
   schema is up to date with the main branch.
   You can run the whole Moblab locally or start the db only:
   `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock "gcr.io/chromeos-partner-moblab/moblab-compose:autopush" db`;

3) Run `make moblab-db-revision` from `moblab/src` directory.
   This will generate a file in `moblab/src/moblab_common/database_models/alembic/versions/`;

4) Review your migration scripts. Alembic has limitation on
   what it can handle automatically. Additionally, you may have to tweak
   the scripts to avoid data loss.

5) Commit your migration script.

Apply migrations
---------------------------------
`alembic upgrade head` - upgrate to the latest version

---------------------------------
Need to know more, please refer to the official documentation:
https://alembic.sqlalchemy.org/en/latest/
