import pymysql
import os

def get_db_connection():
    return pymysql.connect(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        db=os.environ['MYSQL_DATABASE'],
        port=int(os.environ['MYSQL_PORT']),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )