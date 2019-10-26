from flask import Flask, render_template, session, send_from_directory, redirect, request, url_for
import os
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
path = os.path.join(os.getcwd(), 'vdb')
app = Flask(__name__, instance_path=path)
app.secret_key = config['Opts']['AppKey']

def check_login():
    if not session.get('logged_in'):
        return False     
    else:
        return True 

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/vdb', methods=['GET', 'POST'])
def vdb():
    if request.method == "POST":
        if request.form['password'] == config['Opts']['Password1']:
            session['logged_in'] = True

    if check_login():
        return render_template('vdb.html')
    else:
        return render_template('login.html')

@app.route('/vdb/<path:filename>')
def protected(filename):
    if check_login():
        return send_from_directory(
            os.path.join(app.instance_path, ''),
            filename
        )
    else: 
        return render_template('login.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
