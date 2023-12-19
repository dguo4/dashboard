import subprocess
from datetime import datetime

# current time
current_time = datetime.now()
current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

# write log
log_file_path = '/home/miahappy/pyProject/autoTask/investment-dashboard/refresh_log.txt'

def restart_heroku_app(app_name):
    command = f"heroku restart -a {app_name}"
    try:
        subprocess.run(command, shell=True, check=True)
        with open(log_file_path, 'a') as file:
            file.write(f"{curent_time}: Heroku app '{app_name}' restarted successfully.")
    except subprocess.CalledProcessError as e:
        with open(log_file_path, 'a') as file:
            file.write(f"{current_time}: Error restarting Heroku app '{app_name}': {e}")

if __name__ == "__main__":
    # Replace 'investment-dashboa
    app_name = "investment-dashboard"
    
    restart_heroku_app(app_name)
