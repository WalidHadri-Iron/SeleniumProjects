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


def check_scraped_product(driver, df_products, row_product):
    ulr_normalized = df_products.iloc[row_product]["url_normalized"]
    indices_same = df_products[df_products.url_normalized == ulr_normalized]
    skus_scraped = list(indices_same["SKU"])
    try:
        driver.get(ulr_normalized)
    except:
        a = pd.DataFrame([[ulr_normalized]*len(list(skus_scraped)), list(skus_scraped),[0]*len(list(skus_scraped))]).T
        a.columns = ['url','SKU','Quantity']
        return a, list(indices_same.index)
    try:
        color_variant_buttons = utils.wait_presents_xpath(driver, xpaths.COLOR_VARIANTS)
        skus_in_stock = []
        for color_button in color_variant_buttons:
            ActionChains(driver).move_to_element(color_button).click(color_button).perform()
            time.sleep(1)
            sizes_in_stock = driver.find_elements(by=By.XPATH, value=xpaths.SIZES_AVAILABLE)+driver.find_elements(by=By.XPATH, value=xpaths.SIZES_AVAILABLE_2)
            skus_in_stock += [(description(driver)["product_code"] + '/' + size_in_stock.text.replace(' ','-') + '-' + utils.get_text_xpath(driver, xpaths.COLOR).replace(' ','-')).replace(' ','-') for size_in_stock in sizes_in_stock]
    except:
        sizes_in_stock = driver.find_elements(by=By.XPATH, value=xpaths.SIZES_AVAILABLE)+driver.find_elements(by=By.XPATH, value=xpaths.SIZES_AVAILABLE_2)
        skus_in_stock = [(description(driver)["product_code"] + '/' + size_in_stock.text.replace(' ','-') + '-' + utils.get_text_xpath(driver, xpaths.COLOR).replace(' ','-')).replace(' ','-') for size_in_stock in sizes_in_stock]
    out_of_stock = set(skus_scraped) - set(skus_in_stock)
    available_in_stock = set(skus_scraped).intersection(set(skus_in_stock))
    a = pd.DataFrame([[ulr_normalized]*len(list(available_in_stock)), list(available_in_stock),[10]*len(list(available_in_stock))]).T
    b = pd.DataFrame([[ulr_normalized]*len(list(out_of_stock)), list(out_of_stock),[0]*len(list(out_of_stock))]).T
    c = pd.concat([a,b])
    c.columns = ['url','SKU','Quantity']
    return c, list(indices_same.index)



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
        cnx.close()

        seen = []
        dump = []
        driver = utils.build_driver(True)
        utils.get_main_url_to_close_pop_up(driver)
        for row_product in tqdm(range(df_products.shape[0])):
            if row_product in seen:
                continue
            else:
                c, indices_same = check_scraped_product(driver, df_products, row_product)   
                seen += indices_same
                dump.append(c)
        df_dump = pd.concat(dump)
        name_output = 'stock_level.csv'
        df_dump = df_dump[["SKU", "Quantity"]]
        df_dump["Location"] = ["SD Warehouse"]*df_dump.shape[0]
        df_dump.to_csv(name_output, index=False)
        s3.upload_file(Filename=name_output,Bucket=settings["BUCKET_NAME"],Key=cs.FOLDER_OUTPUTS+name_output)
        driver.close()

    except:
        print('Check that the database file is available')

    


    

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))