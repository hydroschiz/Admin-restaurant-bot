import logging
import sqlite3


class DatabaseHelper:
    def __init__(self, path_to_db="data/database.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False,
                fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        connection.set_trace_callback(db_logs)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, parameters)
        except Exception as err:
            connection.close()
            return err

        data = None

        if commit:
            connection.commit()

        if fetchone:
            data = cursor.fetchone()

        if fetchall:
            data = cursor.fetchall()

        connection.close()
        return data

    def create_table_admins(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Admins (
                admin_id int NOT NULL,
                message_id int,
                PRIMARY KEY (admin_id)
                );
                """
        return self.execute(sql, commit=True)

    def add_admin(self, admin_id, message_id):
        sql = "INSERT INTO Admins(admin_id, message_id) VALUES (?, ?)"
        parameters = (admin_id, message_id)
        return self.execute(sql, parameters=parameters, commit=True)

    def update_message_id_of_admin(self, admin_id: int, new_message_id: int):
        sql = f"UPDATE Admins SET message_id = ? WHERE admin_id = ?"
        parameters = (new_message_id, admin_id)
        return self.execute(sql, parameters=parameters, commit=True)

    def get_admin(self, admin_id):
        sql = "SELECT * FROM Admins WHERE admin_id = ?"
        parameters = (admin_id, )
        return self.execute(sql, parameters, fetchone=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())


def db_logs(statement):
    logging.info(f"""
Executing: {statement}
""")