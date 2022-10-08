from flask import Flask, render_template

app = Flask(__name__)
from main import torrent_list, client_list


@app.route('/', methods=["GET"])
def index():
    return render_template('index.html', torrents=torrent_list)
