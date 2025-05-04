
import os
import django
import subprocess
import time
import logging
from datetime import datetime

# Configure logging
log_file_path = '/home/john/backup.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    if current_time == "12:00":
        current_date = now.strftime("%d-%m-%Y")

        # Construct the command to run the other script
        command = f"/home/john/venv/bin/python -Xutf8 /home/john/volunteer_reports/manage.py dumpdata > /home/john/backup/data-{current_date}.json"

        logging.info(f'Start creating file {current_date}')

        # Run the command using subprocess with capture_output=True
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Log the result
        if result.returncode == 0:
            logging.info(f'Created file {current_date}')
        else:
            logging.error(f'Error creating file {current_date}. Output: {result.stdout}. Error: {result.stderr}')

        # Check the number of files in the backup folder
        backup_folder = '/home/john/backup/'

        files = os.listdir(backup_folder)
        file_count = len(files)

        # If there are 5 or more files, delete the oldest file
        if file_count > 5:
            oldest_file = min(files, key=lambda x: os.path.getctime(os.path.join(backup_folder, x)))

            logging.info(f'Delete oldest file {oldest_file}')

            os.remove(os.path.join(backup_folder, oldest_file))

    # Repeat every minute
    time.sleep(60)

