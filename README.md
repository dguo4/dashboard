# dashboard

After making changes on the code, there are two steps needed to be done: 

1. Your own repo
    
    changes can be uploaded to Github repo through PyCharm 


2. Heroku repo
    
    using below commands to upload changes to heroku
   
   ```powershell 
   git add . 
   git commit -am "commit comments"
   heroku git:remote -a investment-dashboard
   ```
   