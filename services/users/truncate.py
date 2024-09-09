import sqlmodel

import services.database


def truncate(db_session: sqlmodel.Session):
    table_names = ["users"]

    for table_name in table_names:
        services.database.truncate_table(db_session=db_session, table_name=table_name)
