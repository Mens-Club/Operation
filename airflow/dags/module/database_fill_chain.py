from config.db_connect import get_db_connection 
from config.main_category_utils import *
import logging

def main():
    connection = get_db_connection() 
    
    try: 
        with connection.cursor() as cursor:
            process_recommendations(cursor=cursor)
        logging.info("변환 작업중 ...")
        connection.commit() 
        logging.info("완료")
    finally:
        connection.close() 
