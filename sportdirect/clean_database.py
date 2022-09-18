from helpers.functions import *
import datetime
import time
import boto3
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
import threading
from datetime import datetime
import json
import sqlite3


if __name__ == "__main__":
    start_time = datetime.now()

    with open('settings.json', 'r') as fp:
        settings = json.load(fp)

    s3 = boto3.client("s3", aws_access_key_id=settings["AWS_SERVER_PUBLIC_KEY"], 
                      aws_secret_access_key=settings["AWS_SERVER_SECRET_KEY"], 
                      region_name=settings["REGION_NAME"])



    try:
        s3.download_file(Bucket=settings["BUCKET_NAME"], Filename= "db_temp2.db", Key=cs.FOLDER_OUTPUTS+"database.db")
        cnx = sqlite3.connect('db_temp2.db')
        df_products = pd.read_sql_query("SELECT * FROM data", cnx)
        df_products['url_normalized'] = df_products['product_url'].apply(lambda x: x.split("#")[0])
        before_clean = df_products['url_normalized'].shape[0]

        cnx.close()

        still_on = []
        driver = utils.build_driver(True)
        utils.get_main_url_to_close_pop_up(driver)
        for i in range(df_products.shape[0]):
            if driver.get(df_products.iloc[i]['url_normalized']):
                still_on.append(i)

        driver.close()
        df_out = 

    except:
        print('Check that the database file is available')

    


    

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))