import subprocess
from datetime import datetime


# current time
current_time = datetime.now()
current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

# Define the commit message
commit_message = "commit comments"

# Git commands
git_add_command = "git add ."
git_commit_command = f'git commit -am "{commit_message}"'
git_push_command = "git push heroku master"


# write log
log_file_path = '/home/miahappy/pyProject/autoTask/dashboard_refresh_log.txt'
# Run Git commands
try:
    # git add .
    subprocess.run(git_add_command, shell=True, check=True)

    # git commit -am "commit comments"
    subprocess.run(git_commit_command, shell=True, check=True)

    # git push heroku master
    subprocess.run(git_push_command, shell=True, check=True)
    with open(log_file_path, 'a') as file:
        file.write(f"{current_time}: Git commands executed successfully \n")
except subprocess.CalledProcessError as e:
    with open(log_file_path, 'a') as file:
        file.write(f"{current_time}: Error executing Git command: {e} \n") 

