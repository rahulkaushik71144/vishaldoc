from flask import Flask, Response, render_template, request, send_from_directory, jsonify, abort
from helper import get_stats, update_stats, process_request
from werkzeug.utils import secure_filename
from datetime import date
import time
import json
import os


app = Flask(__name__)
app.secret_key = os.urandom(12).hex()

@app.route('/')
def home():
    update_stats('visits')
    return render_template("index.html")

@app.route('/active')
def active():
    update_stats('visits')
    return render_template("active.html")

@app.route('/passive')
def passive():
    update_stats('visits')
    return render_template("passive.html")

@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == "POST":
        update_stats('checked')
        data = request.get_json()
        try:
            response = process_request(data)
            return jsonify(status=True, response=response)
        except Exception as e:
            return jsonify(status=False, response=str(e))
    
    return render_template('process.html', args=request.args)

@app.route("/listen")
def listen():

    def respond_to_client():
        while True:
            stats = get_stats()
            _data = json.dumps(
                {"visits": stats['visits'], "checked": stats['checked'], "phished": stats['phished']})
            yield f"id: 1\ndata: {_data}\nevent: stats\n\n"
            time.sleep(0.5)

    return Response(respond_to_client(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
