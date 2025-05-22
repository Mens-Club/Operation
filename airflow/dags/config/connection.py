import pymysql
import os
import boto3

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
    
def get_client():
    
    return boto3.client(
        service_name=os.getenv("SERVICE_NAME"),
        endpoint_url=os.getenv("ENDPOINT_URL"),
        region_name=os.getenv("REGION_NAME"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=boto3.session.Config(signature_version="s3v4")
    )