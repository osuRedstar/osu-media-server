from lets_common_log import logUtils as log
from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory, jsonify, send_file, Response, jsonify
from functions import *
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/list")
def list():
    return jsonify(read_list())


@app.route('/bg/<id>')
def bg(id):
    return send_file(read_bg(id), mimetype='image/jpeg')

@app.route('/audio/<id>')
def preview(id):
    return send_file(read_audio(id), mimetype='audio/mpeg')

#ffmpeg 도입 시도해보기
@app.route('/preview/<id>')
def audio(id):
    log.debug(id)
    return id
    #return send_file(read_audio(id), mimetype='audio/mpeg')

def stream_osz(id):
    response = send_file(read_osz(id), mimetype='application/x-osu-beatmap-archive')
    response.headers["Content-Disposition"] = f"attachment; filename={read_osz(id).replace('dl/', '')}"
    return response
@app.route('/d/<id>')
def osz(id):
    return stream_osz(id)

def stream_osu(id):
    response = send_file(read_osu(id), mimetype='application/x-osu-beatmap')
    response.headers["Content-Disposition"] = f"attachment; filename={read_osu(id).replace('osu/', '')}"
    return response
@app.route('/osu/<id>')
def osu(id):
    return stream_osu(id)


if __name__ == "__main__":
    folder_check()
    app.run(host= '0.0.0.0', port=6200, threaded= False, debug=True)

