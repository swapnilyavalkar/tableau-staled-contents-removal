import datetime


env = 'PROD'
server_url = "https://abc.com/"
user_name = ''
password = ''
site_id = ""
workbook_age_threshold = 180

# Variables used for Execution #
FROM = 'admin@abc.com'
TO = 'xyz@abc.com'
CC = ''
ADMIN_DL = '' 

# Variables used for Execution #

# Variables used for Trigger Alerts #
TGR_FROM = 'admin@abc.com'
TGR_TO = ''
TGR_CC = ''
TGR_ADMIN_DL = ''

# Variables used for Trigger Alerts #


TODAY = datetime.datetime.now()

smtp_host = 'mail.abc.com'
smtp_port = 25

tableau_auth = ''
server = ''
pgsql_connection = ''
list_of_errors = []
