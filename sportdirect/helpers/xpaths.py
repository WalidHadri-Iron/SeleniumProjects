# PRODUCT PAGE XPATHS
BRAND = '//*[@id="productDetails"]//*[@id="lblProductBrand"]'
RETAIL_PRICE = '//*[@id="productDetails"]//*[@id="lblSellingPrice"]'
RRP_PRICE = '//*[@id="productDetails"]//*[@id="lblTicketPrice"]'
COLOR = '//*[@id="productDetails"]//*[@id="colourName"]'
COLOR_VARIANTS = '//*[contains(@class,"colorImgli")]'
SIZES = '//*[@id="productDetails"]//*[@id="ulSizes"]'
AVAILABLE_SIZE_VARIATIONS = '//*[contains(@class,"tooltip sizeButtonli") and not(contains(@class,"greyOut"))]//a'
SIZE_VARIATION_ID = "//*[@id='hdnSelectedSizeVarId']"
VARIATION_GROUP = '//span[@id="lblProductName"]'
META_OG_IMAGE = '//meta[contains(@name,"viewport")]'
DESCRIPTION = '//div[@class="infoTabPage"]//span[@itemprop="description"]'
IMAGES_CONTAINER = '//div[@id="productImages"]//ul[@id="piThumbList"]'
IMAGES = '//div[@id="productImages"]//ul[@id="piThumbList"]//a'
#SIZES_AVAILABLE  = '//*[@id="productDetails"]//*[@id="ulSizes"]//*[@class="tooltip sizeButtonli"]'
SIZES_AVAILABLE = '//*[@id="productDetails"]//*[@id="ulSizes"]//*[@id="liItem"]'
SIZES_AVAILABLE_2 = '//*[@id="productDetails"]//*[@id="ulSizes"]//*[@class="tooltip sizeButtonli "]'

# CATEGORY PAGE XPATHS
PRODUCT_IMAGE_IN_LIST = '//*[@class="ProductImageList"]'
LAST_PAGE_NUMBER = '//*[@class="swipeNumberClick"]'


# GENERAL XPATHS
ERROR_HEAD = '//*[contains(@class,"ErrorHead")]'
COUNTRY_POP_UP_CLOSE_BUTTON = "//div[@class='CountryRedirectModal modal in']//button[@class='close']"

