import sqlmodel

import services.database


def truncate(db_session: sqlmodel.Session):
    services.database.truncate_table(db_session=db_session, table_name="workers")