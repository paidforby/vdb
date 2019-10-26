# vdb  
a lightly-protected video data base running on flask  

For testing and development, execute the following commands,  
```
virtualenv .env
source .env/bin/activate
pip install Flask configparser
export FLASK_APP=app.py
flask run
```
Then go to http://localhost:5000/vdb and enter the default password `NameOfYourFirstPet` and you should be able to watch the test movie *Pencilo de Colores*.  

For production, use a web server gateway of your choice. I used Gunicorn and ran it as a systemd service. A wsgi.py for gunicorn and an example service file are included. Modify these files for your web server.  

Place your video files in the `vdb/` directory and link to them from `vdb.html`.  

Disclaimer: the security of this web app is in no way verified and should be consider *very* light protection. Do not place any sensitive content in the protected files or directory.  
