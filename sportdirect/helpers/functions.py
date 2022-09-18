import re
import uuid
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import helpers.utils as utils
import helpers.xpaths as xpaths
import helpers.constants as cs
from helpers.custom_exceptions import _NotFoundException
import pandas as pd
import logging
from bs4 import BeautifulSoup
from bs4 import element as bs_element
from selenium.webdriver.common.action_chains import ActionChains
from tqdm import tqdm

# logging.basicConfig(
#     format='%(asctime)s %(levelname)s %(process)-4s %(message)s ',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S')
    


def check_current_url(_driver):
    """
    Check if url is valid or not
    """
    try:
        utils.wait_visible_xpath(_driver, xpaths.ERROR_HEAD, 0.5)
        return False
    except _NotFoundException:
        return True


def product_urls_from_input_file(_input_file):
    """
    Reading the urls from the input file
    """
    if 'xlsb' in _input_file:
        urls_df = pd.read_excel(_input_file, engine='pyxlsb')
    else:
        urls_df = pd.read_excel(_input_file)
    return urls_df[[cs.PRODUCT_URLS_COLUMN_NAME, cs.URL_TYPE]]


# get products url from one single multi product page
def product_urls_from_page(_driver, _url):
    """
    Takes in the url of category or search page and return the links to the products in the results
    """
    _d = _driver
    _products_urls = []
    _d.get(_url)
    if not check_current_url(_d):
        return []
    

    results = _d.find_elements(by=By.XPATH, value='//*[@id="navlist"]//li')
    for result in results:
        while True:
            try:
                url_product = result.find_element_by_xpath('.//*[@class="ProductImageList"]').get_attribute('href')
                break
            except:
                pass
        try:
            result.find_element_by_xpath('.//*[@class="fromProductPrice"]')
            from_status = True
        except:
            from_status = False
        _products_urls.append((url_product, from_status))
    
#     products_elements = _d.find_elements(by=By.XPATH, value=xpaths.PRODUCT_IMAGE_IN_LIST)
#     _products_urls = [e.get_attribute('href') for e in products_elements]
    return _products_urls


# get all products url from all the input url pages (1,2, ...)
def all_product_urls_from_input_urls(_driver, _input_urls):
    """
    Takes in a list of urls (category+search page) return the products of the urls by iterating over the _input_urls
    """
    all_products_urls = []
    _d = _driver
    for i in range(_input_urls.shape[0]):
        if _input_urls.iloc[i][cs.URL_TYPE] == "product":

            all_products_urls.append((_input_urls.iloc[i][cs.PRODUCT_URLS_COLUMN_NAME], True))
        else:
            _input_url = _input_urls.iloc[i][cs.PRODUCT_URLS_COLUMN_NAME]
            all_products_urls += product_urls_from_page(_d, _input_url)
            last_page_info = _d.find_elements(by=By.XPATH, value=xpaths.LAST_PAGE_NUMBER)
            if last_page_info:
                last_page_number = int(last_page_info[-1].text)
            else:
                last_page_number = 2
            print('Getting the product urls from the main page')
            for count in tqdm(range(2, last_page_number)):
                _input_url_not_first = _input_url + \
                                    cs.CATEGORY_URL_SUFFIX_PATTERN.replace(cs.SPECIAL_STRING_TO_BE_REPLACED,
                                                                            str(count))
                _urls = product_urls_from_page(_d, _input_url_not_first)
                if not _urls:
                    logging.info(r"'Products not found' page reached!")
                    break
                all_products_urls += _urls

    return list(set(all_products_urls))


def size_variation_id(_driver):
    _xpath = xpaths.SIZE_VARIATION_ID
    try:
        elem = _driver.find_element(by=By.XPATH, value=_xpath)
        return elem.get_attribute('value')
    except NoSuchElementException:
        logging.error(f"Can't find the size variation id, xpath={_xpath}")


def images_url(_driver):
    _d = _driver
    images_dict = dict()
    # images processing
    # first we find the image container
    # if found, we fetch all the children's srczoom values
    # if not, we return an empty list
    try:
        images_elements = utils.wait_presents_xpath(_d, xpaths.IMAGES, 3)
        if images_elements:
            i = 1
            for e in images_elements:
                images_dict[f"IMAGE URL {i}"] = e.get_attribute('srczoom')
                i += 1
            return images_dict
        else:
            return images_dict
    except _NotFoundException:
        logging.info("No group of images elements found")
        return images_dict


def description(_driver):
    _d = _driver
    # description processing
    _description = {
        "product_code": "",
        "full_description_no_html": "",
        "full_description_html": "",
#         "top_description": "",
        "item_specifics": dict(),
        "bullet_points": dict()
    }
    try:
        desc_element = utils.wait_visible_xpath(_d, xpaths.DESCRIPTION)
        soup_desc = BeautifulSoup(desc_element.get_attribute('innerHTML'), "html.parser")
#         full_desc_text = ""
#         for elem in soup_desc.contents:
#             '''
#             First, we try to find the top description (it is the only NavigableString that is not '\n')
#             At this point we assume that it is impossible to have bullet points without the top description
#             So if there is no bullet points, the full description will remain empty
#             '''
#             if isinstance(elem, bs_element.NavigableString) and elem != '\n':
#                 top_desc = elem
# #                 _description["top_description"] = utils.clean_description(top_desc)
#                 # we check if there is a bullet points container
#                 if soup_desc.find_all('ul'):
#                     '''
#                     We go from sibling to sibling until we find the bullet points container.
#                     We append each <br> element as '\n'.
#                     '''
#                     full_desc_text += elem
#                     current_elem = elem.nextSibling
#                     while current_elem.name != 'ul':
#                         if current_elem.name == 'br':
#                             full_desc_text += '\n'
#                         current_elem = current_elem.nextSibling
#                     '''
#                     We read the children of the bullet points container which are the bullet points.
#                     We then format them by adding '\n' and a bullet point ascii character as unicode
#                     '''
#                     bullet_points = current_elem.findChildren('li')
#                     for bp in bullet_points:
#                         full_desc_text += '\n'
#                         full_desc_text += '\u25AA' + ' '
#                         full_desc_text += bp.text
#                     _description["full_description_no_html"] = utils.clean_description(full_desc_text)
#                 break

        
        # fetching item specifics
        item_specifics_soup = soup_desc.find('dl')
        if item_specifics_soup:
            keys = [x.text for x in item_specifics_soup.findChildren('dt')]
            values = [x.text for x in item_specifics_soup.findChildren('dd')]
            _description["item_specifics"] = dict(zip(keys, values))
        # get product code
        product_code_soup = soup_desc.find('p')
        product_code = ''
        if product_code_soup and re.findall(r'\d+', product_code_soup.text):
            product_code = re.findall(r'\d+', product_code_soup.text)[0]
        _description["product_code"] = product_code
        # get bullet points
        bullet_points_container_soup = soup_desc.find('ul')
        if bullet_points_container_soup:
            bullet_points = bullet_points_container_soup.findChildren('li')
            i = 1
            for bp in bullet_points:
                _description["bullet_points"][f"Bullet {i}"] = bp.text
                i += 1
        # decomposing unwanted html tags in order to get the html version of the full description (top + bullet points)
        [x.decompose() for x in soup_desc.find_all(['h2', 'b', 'p', 'dl', 'div'])]
#         _description["full_description_html"] = soup_desc
#         _description["full_description_no_html"] = soup_desc.get_text()

        _description["full_description_html"] = "\n".join(_d.find_element_by_xpath('//*[@class="infoTabPage"]//*').get_attribute('innerHTML').split('\n')[:-4]).replace('<dt>', '<dt><strong>').replace('</dt>', '<dt></strong>')
        _description["full_description_no_html"] = "\n".join(_d.find_element_by_xpath('//*[@class="infoTabPage"]//*').text.split('\n')[:-1])
        return _description
    except _NotFoundException:
        logging.info("description not found")
        return _description


def product_infos(_driver, _product_url, size_variation_consider=False):
    _d = _driver
    _d.get(_product_url)

    _product_infos = []

    '''
    First, we check if the link is broken = ERROR 404
    '''
    _product_info = dict()
    _product_info["product_url"] = _product_url
    _product_info["id"] = uuid.uuid1()
    if not check_current_url(_d):
#         _product_info["Size Variation"] = ""
        _product_info["Variation Group"] = ""
        _product_info["Colour ID"] = ""
        _product_info["Master SKU"] = ""
        _product_info["Colour Variation"] = ""
        _product_info["Brand Name"] = ""
        _product_info["Retail Price"] = ""
        _product_info["RRP Price"] = ""
        _product_info["STOCK"] = ""
        _product_info["SKU"] = ""
        _product_info["Size Variation ID"] = ""
        _product_info["images"] = dict()
#         _product_info["top_description"] = ""
        _product_info["full_description_html"] = ""
        _product_info["full_description_no_html"] = ""
        _product_info["item_specifics"] = dict()
        _product_infos.append(_product_info)
        return _product_infos

#     '''
#     At this point, we have product urls. Let's click on all colors and each time, click on the available
#     sizes to ensure that if something depends on color or size, we will see it when it changes.
#     '''

    def append_product_info_of_all_sizes(_pis, _size_buttons):
        i = 0
        for size_button in _size_buttons:
            #size_button.click()
            while True:
                try:
                    ActionChains(_d).move_to_element(size_button).click(size_button).perform()
                    break
                except:
                    pass
            if i == 0:
                _pi = dict()
                _pi["product_url"] = _d.current_url
                _pi["id"] = uuid.uuid1()
                #_pi["Size Variation"] = utils.elem_to_span_child_text(_d, size_button)
                _pi["Size Variation"] = size_button.text
                _pi["Variation Group"] = utils.get_text_xpath(_d, xpaths.BRAND) + ' ' + utils.get_text_xpath(_d, xpaths.VARIATION_GROUP)
                _pi["Colour ID"] = colour_id_from_url(_d.current_url)
                _pi["Master SKU"] = description(_d)["product_code"] + '-MASTER'
                _pi["Colour Variation"] = utils.get_text_xpath(_d, xpaths.COLOR)
                _pi["Brand Name"] = utils.get_text_xpath(_d, xpaths.BRAND)
                _pi["Retail Price"] = utils.get_text_xpath(_d, xpaths.RETAIL_PRICE)
                _pi["RRP Price"] = utils.get_text_xpath(_d, xpaths.RRP_PRICE)
                _pi["STOCK"] = ""
                _pi["Size Variation ID"] = size_variation_id(_d)
                _pi["SKU"] = (description(_d)["product_code"] + '/' + size_button.text.replace(' ','-') + '-' + utils.get_text_xpath(_d, xpaths.COLOR).replace(' ','-')).replace(' ','-')
                _pi["images"] = images_url(_d)
#                 _pi["top_description"] = description(_d)["top_description"]
                _pi["full_description_html"] = description(_d)["full_description_html"]
                _pi["full_description_no_html"] = description(_d)["full_description_no_html"]
                _pi["item_specifics"] = description(_d)["item_specifics"]
                _pi["bullet_points"] = description(_d)["bullet_points"]
                # add id to item_specifics and images to be used while merging
                _pi["item_specifics"]["id"] = _pi["id"]
                _pi["images"]["id"] = _pi["id"]
                _pi["bullet_points"]["id"] = _pi["id"]
                i = 1
            else:
                _pi = dict(_pi)
                id_ = uuid.uuid1()
                _pi["id"] = id_
                _pi["Size Variation"] = size_button.text
                _pi["item_specifics"] = dict(_pi["item_specifics"])
                _pi["item_specifics"]["id"] = id_
                _pi["images"] = dict(_pi["images"])
                _pi["images"]["id"] = id_
                _pi["bullet_points"] = dict(_pi["bullet_points"])
                _pi["bullet_points"]["id"] = id_
                _pi["SKU"] = (description(_d)["product_code"] + '/' + size_button.text.replace(' ','-') + '-' + utils.get_text_xpath(_d, xpaths.COLOR).replace(' ','-')).replace(' ','-')
            _pis.append(_pi)
                
       
    if not size_variation_consider:
        i = 0
        results = _d.find_elements_by_xpath(xpaths.SIZES_AVAILABLE) + _d.find_elements_by_xpath(xpaths.SIZES_AVAILABLE_2)
        for size in results:
            if i == 0:
                _pi = dict()
                _pi["product_url"] = _d.current_url
                _pi["id"] = uuid.uuid1()
                #_pi["Size Variation"] = utils.elem_to_span_child_text(size_button)
                _pi["Size Variation"] = size.text
                _pi["Variation Group"] = utils.get_text_xpath(_d, xpaths.BRAND) + ' ' + utils.get_text_xpath(_d, xpaths.VARIATION_GROUP)
                _pi["Colour ID"] = colour_id_from_url(_d.current_url)
                _pi["Master SKU"] = description(_d)["product_code"] + '-MASTER'
                _pi["Colour Variation"] = utils.get_text_xpath(_d, xpaths.COLOR)
                _pi["Brand Name"] = utils.get_text_xpath(_d, xpaths.BRAND)
                _pi["Retail Price"] = utils.get_text_xpath(_d, xpaths.RETAIL_PRICE)
                _pi["RRP Price"] = utils.get_text_xpath(_d, xpaths.RRP_PRICE)
                _pi["STOCK"] = ""
                _pi["SKU"] = (description(_d)["product_code"] + '/' + size.text.replace(' ','-') + '-' + utils.get_text_xpath(_d, xpaths.COLOR).replace(' ','-')).replace(' ','-')
                _pi["Size Variation ID"] = size_variation_id(_d)
                _pi["images"] = images_url(_d)
#                 _pi["top_description"] = description(_d)["top_description"]
                _pi["full_description_html"] = description(_d)["full_description_html"]
                _pi["full_description_no_html"] = description(_d)["full_description_no_html"]
                _pi["item_specifics"] = description(_d)["item_specifics"]
                _pi["bullet_points"] = description(_d)["bullet_points"]
                # add id to item_specifics and images to be used while merging
                _pi["item_specifics"]["id"] = _pi["id"]
                _pi["images"]["id"] = _pi["id"]
                _pi["bullet_points"]["id"] = _pi["id"]
                _product_infos.append(_pi)
                i = 1
            else:
                _pi = dict(_pi)
                id_ = uuid.uuid1()
                _pi["id"] = id_
                _pi["Size Variation"] = size.text
                _pi["item_specifics"] = dict(_pi["item_specifics"])
                _pi["item_specifics"]["id"] = id_
                _pi["images"] = dict(_pi["images"])
                _pi["images"]["id"] = id_
                _pi["bullet_points"] = dict(_pi["bullet_points"])
                _pi["bullet_points"]["id"] = id_
                _pi["SKU"] = (description(_d)["product_code"] + '/' + size.text.replace(' ','-') + '-' + utils.get_text_xpath(_d, xpaths.COLOR).replace(' ','-')).replace(' ','-')
                _product_infos.append(_pi)
        return _product_infos
    try:
        available_size_variations_buttons = utils.wait_presents_xpath(_d, xpaths.SIZES_AVAILABLE)
        append_product_info_of_all_sizes(_product_infos, available_size_variations_buttons)
    except:
        available_size_variations_buttons = utils.wait_presents_xpath(_d, xpaths.SIZES_AVAILABLE_2)
        append_product_info_of_all_sizes(_product_infos, available_size_variations_buttons)
#     try:
#         color_variant_buttons = utils.wait_presents_xpath(_d, xpaths.COLOR_VARIANTS)
#         for color_button in color_variant_buttons:
#             #color_button.click()
#             ActionChains(_d).move_to_element(color_button).click(color_button).perform()
#             try:
#                 available_size_variations_buttons = utils.wait_presents_xpath(_d, xpaths.AVAILABLE_SIZE_VARIATIONS)
#                 append_product_info_of_all_sizes(_product_infos, available_size_variations_buttons)
#             except _NotFoundException:
#                 pass
#     except _NotFoundException:
#         try:
#             available_size_variations_buttons = utils.wait_presents_xpath(_d, xpaths.AVAILABLE_SIZE_VARIATIONS)
#             append_product_info_of_all_sizes(_product_infos, available_size_variations_buttons)
#         except _NotFoundException:
#             pass

    return _product_infos


#def urls_to_products_info(_urls, _driver):
def urls_to_products_info(_urls, driver):
    _d = driver
    _products_info_list = []
    print("Scraping Products")
    for _url in tqdm(_urls):
        _products_info_list += product_infos(_d, _url[0], _url[1])
    return _products_info_list


def colour_id_from_url(_product_url):
    _url = _product_url
    _colour_id = ''
    if re.findall('#colcode=[0-9]+', _url):
        _colour_id = re.findall('#colcode=[0-9]+', _url)[0]
        _colour_id = _colour_id.replace('#colcode=', '')
    return _colour_id


def merge_item_specifics(_df_before_merge):
    _df_item_specifics = pd.DataFrame(list(_df_before_merge["item_specifics"]))
    del _df_before_merge["item_specifics"]
    _df_merged = pd.merge(_df_before_merge, _df_item_specifics, on='id')
    _df_merged.fillna('', inplace=True)
    return _df_merged


def merge_images(_df_before_merge):
    _df_images = pd.DataFrame(list(_df_before_merge["images"]))
    del _df_before_merge["images"]
    _df_merged = pd.merge(_df_before_merge, _df_images, on='id')
    _df_merged.fillna('', inplace=True)
    return _df_merged


def merge_bullet_points(_df_before_merge):
    _df_bullet_points = pd.DataFrame(list(_df_before_merge["bullet_points"]))
    del _df_before_merge["bullet_points"]
    _df_merged = pd.merge(_df_before_merge, _df_bullet_points, on='id')
    _df_merged.fillna('', inplace=True)
    return _df_merged


def dataframe_after_merging(_list_of_dict):
    _df_before_merge = pd.DataFrame(_list_of_dict)
    _df_merged = merge_item_specifics(_df_before_merge)
    _df_merged = merge_images(_df_merged)
    _df_merged = merge_bullet_points(_df_merged)
    del _df_merged['id']
    return _df_merged


# if __name__ == "__main__":


#     start = timeit.default_timer()


#     driver = utils.build_driver(False)
#     utils.get_main_url_to_close_pop_up(driver)
#     # later on the input_urls will contain the url or urls typed as input in the interface
#     input_urls = ["https://www.sportsdirect.com/mens/clothing/hoodies"]
#     urls = all_product_urls_from_input_urls(driver, input_urls)
#     # example for testing : two urls with different item specifics => to test the merge
#     # urls = [
#     #     "https://www.sportsdirect.com/adidas-essentials-fleece-3-stripes-full-zip-hoodie-mens-533033#colcode=53303308"
#     # ]
#     # urls = all_urls_by_colors(urls, driver)
#     # products_info_list = urls_to_products_info(urls, driver)
#     # export_after_merging(cs.EXPORT_FILE_NAME, products_info_list)
#     driver.quit()
#     stop = timeit.default_timer()
#     print('Time: ', stop - start) 
