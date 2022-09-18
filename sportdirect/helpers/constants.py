# SELENIUM DRIVER FILE PATH
FIREFOX_DRIVER_PATH = "geckodriver.exe"
CHROME_DRIVER_PATH = "chromedriver.exe"

# MAIN WEBSITE URL
MAIN_URL = "https://www.sportsdirect.com/"

# PRODUCT URLS
PRODUCT_URLS_COLUMN_NAME = 'URL'
URL_TYPE = "TYPE"

# CATEGORY PAGES
SPECIAL_STRING_TO_BE_REPLACED = '__page_number__'
CATEGORY_URL_SUFFIX_PATTERN = f'#dcp={SPECIAL_STRING_TO_BE_REPLACED}&dppp=120&OrderBy=rank'

# RESULTS SETTINGS
EXPORT_FILE_NAME = 'export.xlsx'

# MISC
MAX_LOOP_COUNT = 1000

# CLEANING STRINGS
DESCRIPTION_PROHIBITED_TEXTS = ['sportsdirect.com', "sportsdirect", "sports direct"]
URL_REGEX = r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([' \
            r'^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'



#S2 Settings
FOLDER_OUTPUTS = 'folder_outputs/'
FOLDER_INPUTS = 'folder_inputs/'
FOLDER_TEMP = "/tmp/"
BUCKET_NAME = "data-selenium"
INPUT_FILE = "Category_Search.xlsx"
TEMP_FILE = "output_temp.xlsx"

AWS_SERVER_PUBLIC_KEY = "AKIAS6O4XTZQJHJJHTSR"
AWS_SERVER_SECRET_KEY = "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"
AWS_REGION = "eu-west-3"


