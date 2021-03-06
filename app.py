import subprocess
from flask import Flask, request, redirect
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import HTTPException
import os
import redis
import base64

app = Flask(__name__)

r = redis.Redis.from_url('redis://localhost:6667', db=4, decode_responses=True)
CAPA = 'capa'
RULES = 'capa-rules'
SIGS = 'sigs'

def save_to_db(h, blob):
    r.hset(h, 'blob', base64.b64encode(blob))
    return True

def load_from_db(h):
    return base64.b64decode(r.hget(h, 'blob'))


def analyze(data, sha256):
	ret = ''
	with open(sha256, 'wb') as f:
		f.write(data)
	command = [CAPA, '-r', RULES, '-s', SIGS, sha256]
	result = subprocess.run(command, stdout=subprocess.PIPE)
	print(result)
	os.remove(sha256)
	return result.stdout

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return BadRequest('No file part')
        file = request.files['file']
        if file:
            save_to_db(request.args.get('id'), file.read())
            return ('File saved', 200)
    return BadRequest('Error') 

@app.route('/analyze')
def analyze_route():
	sha256 = request.args.get('id')
	results = r.hget(sha256, 'results')
	if results:
		return (results, 200)
	
	try:
		results = analyze(load_from_db(sha256), sha256)
		r.hset(sha256, 'results', results)
		return (results, 200)
	except Exception as e:
		print(f'{sha256}: {e}')
		raise e
		return (f'{sha256} blob not found or {e}', 404)


if __name__ == '__main__':
    
    app.run(debug=True)
