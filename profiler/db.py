import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import os
from dotenv import load_dotenv
path='../.env'
load_dotenv(dotenv_path=path,verbose=True)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(os.getenv('DATABASE_NAME'))
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("initialise-database")
@with_appcontext
def initialise_database_command():
    init_db()
    click.echo("Successfully created database schema.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(initialise_database_command)