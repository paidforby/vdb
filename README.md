# vdb  
a lightly-protected video+audio data base running on flask, plus an audio extractor+downloader feature
NOTE: this is becoming a place where I store random python/flask related ideas

For testing and development, execute the following commands,  
```
git clone https://github.com/paidforby/vdb
cd vdb
python -m venv .venv
source .venv/bin/activate
pip3 install Flask configparser celery youtube-dl
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8000
```
Then go to http://localhost:8000/vdb and enter the default password `NameOfYourFirstPet` and you should be able to watch the test movie *Pencilo de Colores*.  

To run the audio extractor and downloader portion of this flask app, you will also need to run a celery worker like so,
```
celery worker -A app.celery --loglevel=debug
```

For production, use a web server gateway of your choice. I used Gunicorn and ran it as a systemd service. A wsgi.py for gunicorn and an example service file are included. Modify these files for your web server. It is also advisable to create a special user with sudo privleges for this webapp, such as `vdb_user`. Then log into your web server as `vdb_user` and execute the following,  
```
sudo apt update
sudo apt install python python-pip rabbitmq-server git
sudo pip install virtualenv
git clone https://github.com/paidforby/vdb
cd vdb
virtualenv .env
source .env/bin/activate
pip install Flask configparser gunicorn celery youtube-dl
sudo cp vdb.service /etc/systemd/system/.
sudo systemctl start vdb
sudo cp celery.service /etc/systemd/system/.
sudo cp celerybeat.service /etc/systemd/system/.
sudo cp -r conf.d /etc/.
mkdir /var/log/celery
mkdir /var/run/celery
sudo chown -R vdb_user /var/log/celery
sudo chown -R vdb_user /var/run/celery
sudo systemctl start celery
```
Now, you should be able to navigate to your server's IP address and see the placeholder website. If this website will be linked to a domain and you are using something like nginx you can modify the root block of to that website's nginx config to look like this,
```
location / {
    include proxy_params;
    proxy_pass http://unix:/home/vdb_user/vdb/vdb.sock;
}
```
and run `sudo systemctl restart nginx`  

For more complicated setups, reference nginx (or whatever you are using) documentation.  

To update and redeploy on a live web server, perform the following steps,
```
git fetch origin 
git checkout FETCH_HEAD -- app.py README.md
sudo systemctl restart vdb
```
This will only update any functional changes made to the python application. The content of your website, the videos in your database, and configurations for your server will not be modified. These must be managed manually.  

Finally, place your video files in the `vdb/` directory and link to them from `vdb.html`.  

Disclaimer: the security of this web app is in no way verified and should be consider *very* light protection. Do not place any sensitive content in the protected files or directory.  
