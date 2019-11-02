from flask import Flask, render_template, session, send_from_directory, redirect, request, url_for, send_file, jsonify
import os
import configparser
import youtube_dl
import shutil
from celery import Celery
config = configparser.ConfigParser()
config.read('config.ini')
path = os.path.join(os.getcwd(), 'vdb')
app = Flask(__name__, instance_path=path)
app.config['UPLOAD_FOLDER'] = '/tmp' 
app.secret_key = config['Opts']['AppKey']
ydl = youtube_dl.YoutubeDL({'outtmpl': '%(playlist_index)s-%(title)s.%(ext)s'})
broker_url = 'amqp://guest@localhost'
celery = Celery(app.name, broker=broker_url)
celery.config_from_object('celeryconfig')

def check_login():
    if not session.get('logged_in'):
        return False     
    else:
        return True 

@celery.task(bind=True)
def dl(self, url):
    if url.find('list') == -1:
        typ='single'
    else:
        typ='playlist'

    if typ == 'single':
        file_template = 'tmp/%(title)s.%(ext)s'
    else:
        file_template = 'tmp/%(playlist_index)s-%(title)s.%(ext)s'

    ydl_opts = {
        'outtmpl': file_template, 
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'restrictfilenames':True,
        'forcefilename':True,
    }

    self.update_state(state='PROGRESS',
                          meta={'current': 50, 'total': 100,
                                'status': 'download started', 'result': 0})

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        title=result['title']

    if typ == 'playlist':
        shutil.make_archive('tmp', 'zip', 'tmp') # create tmp.zip
        shutil.rmtree('tmp') # delete tmp folder
        os.makedirs('tmp') # then recreate tmp folder
        return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': title}
    else:
        return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': title}

#adapted from https://github.com/miguelgrinberg/flask-celery-example
@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = dl.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...',
            'result': 0
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
            'result': task.info['result']
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
            'result': 0
        }
    return jsonify(response)

#accepts a filename parameter like so /download?title=Rubber%20Factory
@app.route('/download')
def download():
    title = request.args.get('title')
    #os.remove('tmp.zip') # need to find place for this after downloading tmp.zip
    return send_file('tmp.zip', as_attachment=True, attachment_filename=title)

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

#accepts parameters encoded like so /ytdl?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Ds 
@app.route('/ytdl', methods=['GET', 'POST'])
def ytdl():
    if request.method == "POST":
        video_url = request.args.get('url')
        task = dl.delay(video_url)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    else:
        return render_template('ytdl.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
