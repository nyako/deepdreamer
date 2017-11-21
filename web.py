from flask import Flask, render_template, send_file, jsonify, request, Response, abort
from flask_socketio import SocketIO, emit
import sys, os, threading
import string, random

sys.path.append('./lib')
from dreamer_thread import Dreamer

class ExtFlask(Flask):
  # reconfigure Jinja's interpolation symbols
  jinja_options = Flask.jinja_options.copy()
  jinja_options.update(dict(
    block_start_string='{%',
    block_end_string='%}',
    variable_start_string='[[',
    variable_end_string=']]',
    comment_start_string='{#',
    comment_end_string='#}'
  ))

app = ExtFlask(__name__)
socketio = SocketIO(app)
DREAMER_PREFIX = 'dreamer-'


@app.route("/")
def index():
  return render_template('index.html')

@app.route("/fetch/<identifier>")
def fetch(identifier):
  # fetches dream output, if it exists
  filepath = 'tmp/' + DREAMER_PREFIX + identifier + '.png'
  if os.path.exists(filepath):
    return send_file(filepath)
  else:
    abort(404)

@app.route("/get/<index>")
def get(index):
  # renders an image from our stock
  images = get_files_list()
  return send_file(images[int(index)])

@app.route('/files')
def files():
  return jsonify(files=get_files_list())

@socketio.on('dream')
def dream(filename):
  # send to deep dream; you can stream logging by establishing a separate websocket channel
  identifier = unique_identifier()
  thread_name = DREAMER_PREFIX + identifier
  t = Dreamer(filename, thread_name)
  t.start()
  emit('dream-ack', dict(id=identifier))

@socketio.on('dreamstats')
def dreamstats(identifier):
  emit('dreamstats-ack-'+identifier, check_dream_status(identifier))

@app.context_processor
def utility_processor():
  return dict(list_files=get_files_list)

def get_files_list():
  images = []
  for subdir in sorted(os.listdir('static/images')):
    subdir_path = os.path.join('static', 'images', subdir)
    if os.path.isdir(subdir_path):
      files = os.listdir(subdir_path)
      for f in files:
        fullpath = os.path.join('static', 'images', subdir, f)
        if os.path.isdir(fullpath) == False:
          # ignore sub-subdirectories
          images.append(fullpath)
    else:
      images.append(subdir_path)
  return images

def unique_identifier():
  space = string.ascii_lowercase + string.ascii_uppercase + string.digits
  return ''.join(random.SystemRandom().choice(space) for _ in xrange(8))

def check_dream_status(identifier):
  thread_name = "dreamer-" + identifier
  status = {}

  for t in threading.enumerate():
    if t.name == thread_name:
      if t.is_alive():
        status['alive'] = True
      else:
        status['alive'] = False
      status['log'] = t.read_logger()
      return status

  # if you can't find the thread, then the thread is done or has died (error)
  status['alive'] = False
  return status
