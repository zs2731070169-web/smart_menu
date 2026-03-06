import os
from dotenv import load_dotenv
import mysql.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class DBConnection:
    def __init__(self):
        self.url = os.getenv("MYSQL_HOST", "localhost")
        self.port = os.getenv("MYSQL_PORT", "3306")
        self.user = os.getenv("MYSQL_USER_NAME", "root")
        self.password = os.getenv("MYSQL_USER_PASSWORD", "root")
        self.database = os.getenv("MYSQL_DB_NAME", "smart_menu")
        self.conn = None
        self.cursor = None

    def init_db(self) -> bool:
        try:
            # 建立数据库连接
            self.conn = mysql.connector.connect(
                host=self.url,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8"
            )

            # 检查连接是否成功
            if self.conn.is_connected():
                # 创建游标对象，设置为字典格式
                self.cursor = self.conn.cursor(dictionary=True)

                logger.info("Successfully connected to MySQL database.")

            return True
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to MySQL: {err}")
            return False

    def close_db(self) -> bool:
        try:
            if self.cursor:
                self.cursor.close() # 关闭游标
                self.cursor = None # 关闭游标并将其设置为 None

            if self.conn and self.conn.is_connected():
                self.conn.close() # 关闭连接
                self.conn = None # 关闭连接并将其设置为 None

            logger.info("MySQL connection closed.")

            return True
        except mysql.connector.Error as err:
            logger.error(f"Error closing MySQL connection: {err}")
            return False

    def __enter__(self):
        """
        initialize db connection when enter context manager
        :return:
        """
        if self.init_db():
            return self
        else:
            raise Exception("Failed to initialize database connection.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        close db connection when exit context manager
        :param exc_type: exp type
        :param exc_val: exp details
        :param exc_tb: exp traceback
        :return:
        """
        self.close_db()

        if exc_type:
            logger.error(f"An error occurred: {exc_val}")

        # return False to propagate the exception if it occurred
        return False

if __name__ == '__main__':
    # Example usage of DBConnection context manager
    with DBConnection() as db:
        db.cursor.execute("SELECT DATABASE()")
        result = db.cursor.fetchone()
        logger.info(f"Current database: {result['DATABASE()']}")

