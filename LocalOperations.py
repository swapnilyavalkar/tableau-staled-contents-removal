import datetime
import os
import logging
import Variables
import time


LOCAL_BACKUP_DIR = "C:\\BACKUP" # Mention the backup dir to save downloaded dashboards.
LOCAL_BACKUP_THRESHOLD = 30 # No of days to be mentioned to remove local dashboards.
LOG_FILE_GEN_TIME = time.strftime("%Y%m%d-%H%M%S")


def DeleteLocalWorkbooks():
    for root, dirs, files in os.walk(LOCAL_BACKUP_DIR):
        for file in files:
            try:
                local_file_path = os.path.join(LOCAL_BACKUP_DIR, file)
                local_file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(local_file_path))
                difference_in_file_creation = (Variables.TODAY - local_file_creation_time).days
                if difference_in_file_creation > LOCAL_BACKUP_THRESHOLD:
                    logging.debug('Deleting Local File: ' + file + ' Which is older than: '
                                      + str(difference_in_file_creation)
                                      + ' Days' + ' From Local Directory: ' + LOCAL_BACKUP_DIR)
                    os.remove(local_file_path)
            except Exception as e:
                logging.critical("Exception Occurred In : DeleteLocalWorkbooks", exc_info=True)
                Variables.list_of_errors.append(['DeleteLocalWorkbooks', repr(e)])

        for directory in dirs:
            local_directory = os.path.join(LOCAL_BACKUP_DIR, directory)
            logging.debug('Found Local Project Directory: ' + local_directory)
            logging.debug('Traversing Local Project Directory: ' + local_directory)
            for local_workbook in os.listdir(local_directory):
                try:
                    local_file_path = os.path.join(local_directory, local_workbook)
                    local_file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(local_file_path))
                    difference_in_file_creation = (Variables.TODAY - local_file_creation_time).days
                    if difference_in_file_creation > LOCAL_BACKUP_THRESHOLD:
                        logging.debug('Deleting Local File: ' + local_workbook + ' Which is older than: '
                                      + str(difference_in_file_creation)
                                      + ' Days' + ' From Local Directory: ' + local_directory)
                        os.remove(local_file_path)
                except Exception as e:
                    logging.critical("Exception Occurred In : DeleteLocalWorkbooks", exc_info=True)
                    Variables.list_of_errors.append(['DeleteLocalWorkbooks', repr(e)])
            logging.debug('Deleting Local Project Directory: ' + local_directory)


if __name__ == '__main__':
    DeleteLocalWorkbooks()