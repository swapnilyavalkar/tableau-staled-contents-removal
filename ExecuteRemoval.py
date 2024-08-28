import LocalOperations
import tableauserverclient as TSC
import psycopg2
import pandas as pd
import os
import logging
import smtplib
from email.message import EmailMessage
import config
import Variables
import time

LOG_FILE_GEN_TIME = time.strftime("%Y%m%d-%H%M%S")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(module)s:%(funcName)s:%(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    filename='logs/ExecuteRemoval_{0}.log'.format(LOG_FILE_GEN_TIME),
    filemode='a'
)


def sendEmail(SUBJECT, BODY):
    try:
        msg = EmailMessage()
        msg['Subject'] = SUBJECT
        msg['From'] = Variables.FROM
        if "SUCCESS" in SUBJECT:
            msg['To'] = Variables.TO
            msg['Cc'] = Variables.CC
            msg.set_content(BODY)
            msg.add_alternative("<!DOCTYPE html> <html> <body> <p>Hi All,</p></p>Followings are the dashboards "
                                "which are deleted from Tableau server because these have not been used since last "
                                "180 Days : </p><br>" + BODY
                                + "<br><p>Regards, <br>Tableau Admin Team</p> </body> </html>",
                                subtype='html')
            logging.debug('Sending Email To Users For Successful Operation.')
        elif "FAILURE" in SUBJECT:
            msg['To'] = Variables.ADMIN_DL
            msg.set_content(BODY)
            msg.add_alternative(
                "<!DOCTYPE html> <html> <body> <p>Hi Team,</p></p>This activity has been failed due to below errors:  "
                "</p><br>" + BODY + "<p>Regards, <br>Tableau Admin Team</p> </body> </html>",
                subtype='html')
            logging.debug('Sending Email To Users For Failed Operation.')
        else:
            msg['To'] = Variables.ADMIN_DL
            msg.set_content(BODY)
            msg.add_alternative(
                "<!DOCTYPE html> <html> <body> <p>Hi Team,</p><br>" + BODY
                + "<p>Regards, <br>Tableau Admin Team</p> </body> </html>",
                subtype='html')
            logging.debug('Sending Email To Users For Not Required Operation.')
        with smtplib.SMTP(Variables.smtp_host, Variables.smtp_port) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        logging.critical("Exception Occurred In : sendEmail", exc_info=True)
        Variables.list_of_errors.append(['sendEmail', repr(e)])


def DeleteWorkbookFromTableauServer(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME):
    try:
        logging.debug('Deleting Server Workbook: ' + WORKBOOK_NAME + ' From Project: ' + PROJECT_NAME)
        Variables.server.workbooks.delete(WORKBOOK_LUID)
    except Exception as e:
        logging.critical("Exception Occurred In : DeleteWorkbookFromTableauServer", exc_info=True)
        Variables.list_of_errors.append(['DeleteWorkbookFromTableauServer', repr(e)])


def DownloadWorkbook(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME, SITE_NAME):
    try:
        LOCAL_SITE_DIR = os.path.join(LocalOperations.LOCAL_BACKUP_DIR, SITE_NAME)
        LOCAL_PROJECT_DIR = os.path.join(LOCAL_SITE_DIR, PROJECT_NAME)
        if not os.path.exists(LOCAL_SITE_DIR):
            logging.debug('Creating Local Site Directory : ' + LOCAL_SITE_DIR)
            os.mkdir(LOCAL_SITE_DIR)
            if not os.path.exists(LOCAL_PROJECT_DIR):
                logging.debug('Creating Local Project Directory : ' + LOCAL_PROJECT_DIR)
                os.mkdir(LOCAL_PROJECT_DIR)
                logging.debug(
                    'Downloading Server Workbook: ' + WORKBOOK_NAME + ' From Project: ' + PROJECT_NAME
                    + ' To Local Project Directory ' + LOCAL_PROJECT_DIR)
                Variables.server.workbooks.download(WORKBOOK_LUID, filepath=LOCAL_PROJECT_DIR, no_extract=True)
                DeleteWorkbookFromTableauServer(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME)
            else:
                logging.debug(
                    'Downloading Server Workbook: ' + WORKBOOK_NAME + ' From Project: ' + PROJECT_NAME
                    + ' To Local Project Directory ' + LOCAL_PROJECT_DIR)
                Variables.server.workbooks.download(WORKBOOK_LUID, filepath=LOCAL_PROJECT_DIR, no_extract=True)
                DeleteWorkbookFromTableauServer(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME)
        else:
            if not os.path.exists(LOCAL_PROJECT_DIR):
                logging.debug('Creating Local Project Directory : ' + LOCAL_PROJECT_DIR)
                os.mkdir(LOCAL_PROJECT_DIR)
                logging.debug(
                    'Downloading Server Workbook: ' + WORKBOOK_NAME + ' From Project: ' + PROJECT_NAME
                    + ' To Local Project Directory ' + LOCAL_PROJECT_DIR)
                Variables.server.workbooks.download(WORKBOOK_LUID, filepath=LOCAL_PROJECT_DIR, no_extract=True)
                DeleteWorkbookFromTableauServer(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME)
            else:
                logging.debug(
                    'Downloading Server Workbook: ' + WORKBOOK_NAME + ' From Project: ' + PROJECT_NAME
                    + ' To Local Project Directory ' + LOCAL_PROJECT_DIR)
                Variables.server.workbooks.download(WORKBOOK_LUID, filepath=LOCAL_PROJECT_DIR, no_extract=True)
                DeleteWorkbookFromTableauServer(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME)
    except Exception as e:
        logging.critical("Exception Occurred In : DownloadWorkbook", exc_info=True)
        Variables.list_of_errors.append(['DownloadWorkbook', repr(e)])


def TSsignIn(SITE_NAME):
    try:
        Variables.tableau_auth = TSC.TableauAuth(Variables.user_name, Variables.password, SITE_NAME)
        Variables.server = TSC.Server(Variables.server_url)
        Variables.server.add_http_options({'verify': False})
        Variables.server.use_server_version()
        Variables.server.auth.sign_in(Variables.tableau_auth)
    except Exception as e:
        logging.critical("Exception Occurred In : TSsignIn", exc_info=True)
        Variables.list_of_errors.append(['TSsignIn', repr(e)])


def PGsignIn():
    try:
        logging.debug('Connecting to PG SQL Database.')
        # Create the connection object and connect to PG SQL DB.
        paramspg = config.configpg()
        PGSQL_CONNECTION = psycopg2.connect(**paramspg)
        cursor = PGSQL_CONNECTION.cursor()
        logging.debug('Reading PG SQL Query.')
        # Read the SQL File.
        query = open('sql_queries/FirstQuery.sql', 'r')
        logging.debug('Executing PG SQL Query.')
        data = pd.read_sql_query(query.read(), PGSQL_CONNECTION)
        logging.debug('Creating DataFrame.')
        df = pd.DataFrame(data)
        df['LAST_VIEWED_DATE'] = pd.to_datetime(df['LAST_VIEWED_DATE']).dt.strftime('%m-%d-%Y')
        df['NOT_USED_SINCE_DAYS'] = pd.to_numeric(df['NOT_USED_SINCE_DAYS'])
        df_180_days_results = df.query('NOT_USED_SINCE_DAYS > {}'.format(Variables.workbook_age_threshold))
        df.to_excel('data_files\\{}_all_data.xlsx'.format(Variables.env))
        df_180_days_results.to_excel('data_files\\{}_180days_data.xlsx'.format(Variables.env))
        logging.debug('Dashboards Available To Operate Are : \n' + df_180_days_results.to_string())
        for index, row in df_180_days_results.iterrows():
            WORKBOOK_LUID = row['WORKBOOK_LUID']
            WORKBOOK_NAME = row['WORKBOOK_NAME']
            PROJECT_NAME = row['PROJECT_NAME']
            SITE_NAME = row['SITE_NAME']
            if row['SITE_URL_NAMESPACE'] == '':
                TSsignIn('')  # 2
                DownloadWorkbook(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME, SITE_NAME) #3
            else:
                TSsignIn(row['SITE_URL_NAMESPACE'])  # 2
                DownloadWorkbook(WORKBOOK_LUID, WORKBOOK_NAME, PROJECT_NAME, SITE_NAME)  # 3
        logging.debug('Closing Connection to PG SQL Database.')
        PGSQL_CONNECTION.close()
        logging.debug('Closing Connection to Tableau Server.')
        Variables.server.auth.sign_out()
        return df_180_days_results
    except Exception as e:
        logging.critical("Exception Occurred In: PGsignIn", exc_info=True)
        Variables.list_of_errors.append(['PGsignIn', repr(e)])


if __name__ == '__main__':
    try:
        logging.debug(('#' * 15) + ' CleanUp Operation Started ' + ('#' * 15))
        success_df = PGsignIn()  # 1
        df_user_email_data = success_df[['SITE_NAME', 'PROJECT_NAME', 'WORKBOOK_NAME', 'OWNER_NAME',
                                         'NOT_USED_SINCE_DAYS', 'LAST_VIEWED_DATE', 'WORKBOOK_URL']]
        if df_user_email_data.empty and not Variables.list_of_errors:
            logging.debug('Since there are no dashboards older than last 180 days on Tableau Server,'
                          'none is deleted from Tableau Server.')
            sendEmail("NOT REQUIRED - MONTHLY - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY",
                      'Since there are no dashboards older than last 180 days on Tableau Server,'
                      ' none is deleted from Tableau Server.')
        elif not df_user_email_data.empty and not Variables.list_of_errors:
            logging.debug(('#' * 15) + ' CleanUp Operation Completed ' + ('#' * 15))
            df_user_email_data['WORKBOOK_URL'] = '<a href=' + df_user_email_data['WORKBOOK_URL'] + \
                                                 "><div>Click Here</div></a>"
            df_user_email_data.to_excel('data_files\\{}_user_email_data.xlsx'.format(Variables.env))
            sendEmail("SUCCESS - MONTHLY - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY",
                      df_user_email_data.to_html(na_rep="", index=False, render_links=True,
                                                 escape=False).replace('<th>', '<th style="color:white; '
                                                                               'background-color:#180e62">'))
        elif df_user_email_data.empty and Variables.list_of_errors:
            sendEmail("FAILURE - MONTHLY - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY",
                      str(Variables.list_of_errors))
        else:
            sendEmail("FAILURE - MONTHLY - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY",
                      str(Variables.list_of_errors))
    except Exception as e:
        logging.critical("Exception Occurred In: __main__", exc_info=True)
        Variables.list_of_errors.append(['__main__', repr(e)])
        sendEmail("FAILURE - MONTHLY - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY",
                  str(Variables.list_of_errors))
