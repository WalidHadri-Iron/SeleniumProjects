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
import os



if __name__ == "__main__":
    #Create an S3 access object
    start_time = datetime.now()

    with open('settings.json', 'r') as fp:
        settings = json.load(fp)

    s3 = boto3.client("s3", aws_access_key_id=settings["AWS_SERVER_PUBLIC_KEY"], 
                      aws_secret_access_key=settings["AWS_SERVER_SECRET_KEY"], 
                      region_name=settings["REGION_NAME"])

    download_status = False

    


    s3.download_file(Bucket=settings["BUCKET_NAME"], Filename= cs.TEMP_FILE, Key=cs.FOLDER_INPUTS+settings["INPUT_FILE"])
    download_status = True
    
    if download_status:
        urls = product_urls_from_input_file(cs.TEMP_FILE)
        # urls = product_urls_from_input_file("Category_Search.xlsx")

        driver = utils.build_driver(True)
        utils.get_main_url_to_close_pop_up(driver)


        urls = all_product_urls_from_input_urls(driver, urls)
        products_info_list = urls_to_products_info(urls, driver)

        df_out = dataframe_after_merging(products_info_list)
        name_output = 'output_'+datetime.now().strftime('%b-%d-%I%M%p-%G')+'.xlsx'
        

        # df_out.to_excel(name_output, index=False)
        df_out.to_excel(name_output, index=False)
        s3.upload_file(Filename=name_output,Bucket=settings["BUCKET_NAME"],Key=cs.FOLDER_OUTPUTS+name_output)

        driver.close()
        
        # try:
        print('Using existing database')
        name_database = 'db_temp.db'
        s3.download_file(Bucket=settings["BUCKET_NAME"], Filename= name_database, Key=cs.FOLDER_OUTPUTS+"database.db")
        continue_process = True
        try:
            s3.download_file(Bucket=settings["BUCKET_NAME"], Filename= 'backup-database/backup.db', Key=cs.FOLDER_OUTPUTS+"database.db")
            
        except:
            print('close the backup database')
            continue_process = False
        
        if continue_process:
            cnx = sqlite3.connect(name_database)
            df_in = pd.read_sql_query("SELECT * FROM data", cnx)
            #adding new scraped
            to_db = pd.concat([df_in,df_out]).reset_index(drop=True)
            to_db.drop_duplicates(subset='SKU',keep='last', inplace=True)
            to_db.reset_index(inplace=True, drop=True)
            try:
                to_db.drop(columns=['level_0'], inplace=True)
            except:
                pass
            to_db.to_sql("data", cnx, if_exists="replace")
            cnx.close()
            
     
            
        # except:
            # print('Check that the database is available')
            # cnx = sqlite3.connect('db_temp.db')
            # df_out.drop_duplicates(subset='SKU', keep="last")
            # df_out.to_sql("data", cnx, if_exists="replace")
            # cnx.close()
        

        s3.upload_file(Filename=name_database,Bucket=settings["BUCKET_NAME"],Key=cs.FOLDER_OUTPUTS+"database.db")
        os.remove(name_database)

    
    
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))