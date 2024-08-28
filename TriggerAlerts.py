import psycopg2
import pandas as pd
import config
import logging
import smtplib
from email.message import EmailMessage
import time
import Variables

LOG_FILE_GEN_TIME = time.strftime("%Y%m%d-%H%M%S")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(module)s:%(funcName)s:%(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    filename='logs/TriggerAlerts_{0}.log'.format(LOG_FILE_GEN_TIME),
    filemode='a'
)


def sendSuccessEmail(BODY):
    try:
        msg = EmailMessage()
        msg['Subject'] = "ALERT - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY"
        msg['From'] = Variables.TGR_FROM
        msg['To'] = Variables.TGR_TO
        msg['Cc'] = Variables.TGR_CC
        msg.set_content(BODY)
        msg.add_alternative("<!DOCTYPE html> <html> <body> <p><b>Hi All,</p></p><b>This is to inform you all that "
                            "followings are the dashboards which "
                            "<b>would be deleted from Tableau Server on 10th of this month. "
                            "If if you find that any dashboard is needed, then kindly click on the links given "
                            "for each dashboard and open any view of that dashboard.</p><br>" + BODY
                            + "<br><p><b>Regards, <br><b>Tableau Admin Team</p> </body> </html>",
                            subtype='html')
        logging.debug('Sending Email To Users For Successful Operation.')
        with smtplib.SMTP(Variables.smtp_host, Variables.smtp_port) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        logging.critical("Exception Occurred In : sendEmail", exc_info=True)
        Variables.list_of_errors.append(['sendEmail', repr(e)])


def sendNAEmail():
    try:
        msg = EmailMessage()
        msg['Subject'] = "ALERT - TABLEAU " + Variables.env + " - DASHBOARD CLEANUP ACTIVITY"
        msg['From'] = Variables.TGR_FROM
        msg['To'] = Variables.TGR_ADMIN_DL
        msg.add_alternative("<!DOCTYPE html> <html> <body> <p><b>Hi Team,</p></p><b>There are no "
                            "<b>dashboards which are not used since last 180 days.</p><br><br><p><b>Regards, "
                            "<br><b>Tableau Admin Team</p> </body> </html>",
                            subtype='html')
        logging.debug('Sending Email To Users For NA Operation.')
        with smtplib.SMTP(Variables.smtp_host, Variables.smtp_port) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        logging.critical("Exception Occurred In : sendNAEmail", exc_info=True)
        Variables.list_of_errors.append(['sendNAEmail', repr(e)])


def signInToPostGresSQL():
    try:
        paramspg = config.configpg()
        PGSQL_CONNECTION = psycopg2.connect(**paramspg)
        query = open('sql_queries/trigger_alerts_query.sql', 'r')
        data = pd.read_sql_query(query.read(), PGSQL_CONNECTION)
        df_trg_all_data = pd.DataFrame(data)
        df_trg_all_data['LAST_VIEWED_DATE'] = pd.to_datetime(df_trg_all_data['LAST_VIEWED_DATE']).dt.strftime(
            '%m-%d-%Y')
        df_trg_all_data['NOT_USED_SINCE_DAYS'] = pd.to_numeric(df_trg_all_data['NOT_USED_SINCE_DAYS'])
        df_wblist_trg_170days = df_trg_all_data.query('NOT_USED_SINCE_DAYS > 175')
        df_trg_all_data.to_excel('data_files\\{}_df_trg_all_data.xlsx'.format(Variables.env))
        df_wblist_trg_170days.to_excel('data_files\\{}_df_wblist_trg_170days.xlsx'.format(Variables.env))
        df_trg_user_email_data = df_wblist_trg_170days[['SITE_NAME', 'PROJECT_NAME', 'WORKBOOK_NAME', 'OWNER_NAME',
                                                        'NOT_USED_SINCE_DAYS', 'LAST_VIEWED_DATE', 'WORKBOOK_URL']]
        if not df_trg_user_email_data.empty:
            df_trg_user_email_data['WORKBOOK_URL'] = '<a href=' + df_trg_user_email_data['WORKBOOK_URL'] + \
                                                     "><div>Click Here</div></a>"
            df_trg_user_email_data.to_excel('data_files\\{}_df_trg_user_email_data.xlsx'.format(Variables.env))
            df_trg_user_email_data.reset_index()
            sendSuccessEmail(df_trg_user_email_data.to_html(na_rep="", index=False, render_links=True,
                                                            escape=False).replace('<th>', '<th style="color:white; '
                                                                                          'background-color:#180e62">'))
        else:
            sendNAEmail()
    except Exception as e:
        print(repr(e))


if __name__ == '__main__':
    signInToPostGresSQL()
