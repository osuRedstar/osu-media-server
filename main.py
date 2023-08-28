from lets_common_log import logUtils as log
from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory, jsonify, send_file
from functions import *
import os

app = Flask(__name__)

@app.route('/bg/<id>')
def bg(id):
    return send_file(read_bg(id), mimetype='image/jpeg')
    


if __name__ == "__main__":
    folder_check()
    app.run(host= '0.0.0.0', port=6200, threaded= False, debug=False)

