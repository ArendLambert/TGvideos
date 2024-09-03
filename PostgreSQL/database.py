import psycopg2
from PostgreSQL.config import host, user, password, db_name


class DataBase:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            self.connection.autocommit = True
            self.get_version_database()
        except Exception as _ex:
            print("[INFO] Error while working with postgreSQL", _ex)

    def get_version_database(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT version();"
            )
            print(f"Server version: {cursor.fetchone()}")

    def insert_data_to_database(self, user_id, username, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(

                f"""UPDATE {table_name} SET username = '{username}' WHERE user_id = {user_id};
                insert into {table_name}(user_id, username)
                    select {user_id}, '{username}'
                    where not exists(select 1 from {table_name}
                        where user_id = {user_id}
                        and coalesce(user_id)=coalesce({user_id})
                    );"""

            )
            print("[INFO] Data was successfully inserted")

    def select_id_from_database(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT * FROM {table_name};"""
            )
            list_id = cursor.fetchall()
            return list_id

    def close_database(self):
        if self.connection:
            self.connection.close()
            print("[INFO] portgreSQL connection closed")

    def delete_row(self, user_id, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""DELETE FROM {table_name}
                   WHERE user_id = {user_id}"""
            )

    def truncate_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"TRUNCATE ONLY {table_name};"
            )
            print("[INFO] Table was truncated")
