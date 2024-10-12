import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from sqlalchemy import create_engine, text


def set_up_data_layer(sqlite_file_path: str = ".chainlit/data.db"):
    # Import sqlalchemy. Connect to `sqlite+aiosqlite:///:memory:`.
    # Read the SQL file at `.chainlit/schema.sql`. Execute the SQL commands in the file to create the tables.
    engine = create_engine(f"sqlite:///{sqlite_file_path}")
    with open(".chainlit/schema.sql") as f:
        schema_sql = f.read()
    sql_statements = schema_sql.strip().split(";")  # Split by semicolon
    with engine.connect() as conn:
        for statement in sql_statements:
            if statement.strip():  # Avoid executing empty statements
                conn.execute(text(statement))
    # Set the data layer to use the SQLAlchemyDataLayer with the connection info.
    cl_data._data_layer = SQLAlchemyDataLayer(
        conninfo=f"sqlite+aiosqlite:///{sqlite_file_path}"  # https://stackoverflow.com/a/72334692/27163563
    )
