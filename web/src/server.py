"""
A simple web interface.
"""
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def index(name=None):
    """Serve template"""
    api_url = os.getenv('WEBAPI_URL')

    return render_template('index.html', api_url = api_url)

@app.route('/js/<path:filename>')
def send_js(filename):
    """Serve js static files"""
    return send_from_directory('js', filename)

@app.route('/css/<path:filename>')
def send_css(filename):
    """Serve js static files"""
    return send_from_directory('css', filename)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=80)
