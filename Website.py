import pathlib
import string
import random

from flask import Flask, render_template, request, url_for, redirect

import Client
import Torrent
import parseTorrentFile
from Database import Database

app = Flask(__name__)
db_instance = Database("db_backup/torrents_and_clients.db")

# clients to choose from
Clients = [{"Name": "qBittorrent 4.4.5",
            "peerID": "-qB4450-",
            "User-Agent": "qBittorrent/4.4.5"
            },
           {"Name": "qBittorrent 4.3.1",
            "peerID": "-qB4310-",
            "User-Agent": "qBittorrent/4.3.1"}]


def pretty_size(size):
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size

def parse_size(amount, type):
    match type:
        case 'b':
            return amount

        case 'kb':
            return amount * (10 ** 3)

        case 'mb':
            return amount * (10 ** 6)


def main(torrent_list, client_list):
    @app.route('/')
    def index():
        return render_template('index.html', torrent_list=torrent_list, client_list=client_list,
                               pretty_size=pretty_size)

    @app.route('/clients')
    def display_client_data():
        # reset values
        for client in client_list:
            client.total_uploaded = 0
            client.total_downloaded = 0
            client.upload_speed = 0
            client.download_speed = 0

        for torrent in torrent_list:
            client_list[torrent.client_id].total_downloaded += torrent.downloaded
            client_list[torrent.client_id].total_uploaded += torrent.uploaded
            client_list[torrent.client_id].download_speed += torrent.temp_taken_download
            client_list[torrent.client_id].upload_speed += torrent.temp_taken_upload
        return render_template('clients_page.html', client_list=client_list,
                               pretty_size=pretty_size)

    @app.route('/edit_client/<string:client_name>', methods=["GET", "POST"])
    def edit_client(client_name):
        item = None
        for client in client_list:
            if client.client_name == client_name:
                item = client
                break

        return render_template('edit_client.html', client=item)

    @app.route('/edit_client_post', methods=["POST"])
    def edit_client_post():
        client_name = request.form['client_name']
        download_speed = int(request.form['client_download_limit'])
        download_type = request.form['download_type']
        upload_speed = int(request.form['client_upload_limit'])
        upload_type = request.form['upload_type']
        item = None
        for client in client_list:
            if client.client_name == client_name:
                item = client
                break

        item.download_limit = parse_size(download_speed, download_type)
        item.upload_limit = parse_size(upload_speed, upload_type)
        db_instance.update_client(item)

        return redirect(url_for('index'))


    @app.route('/create_client', methods=["POST", "GET"])
    def create_client():
        if request.method == "GET":
            client_names = [client['Name'] for client in Clients]
            return render_template('create_client.html', client_data_names=client_names, rand_id=''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12)))

        else:
            client_name = request.form["client_name"].replace(" ", "_")
            client_type = request.form["client_type"]
            client_download_limit = int(request.form["client_download_limit"])
            client_download_type = request.form["download_type"]
            client_upload_limit = int(request.form["client_upload_limit"])
            client_upload_type = request.form["upload_type"]
            client_port = int(request.form["client_port"])
            random_id = request.form["random_id"]

            client_download = parse_size(client_download_limit, client_download_type)
            client_upload = parse_size(client_upload_limit, client_upload_type)
            for client in Clients:
                if client_type == client["Name"]:
                    client_type = client
                    break

            new_cli = Client.create_from_user_input(random_id, client_name, client_type["User-Agent"], client_port,
                                                    client_upload, client_download, client_type["peerID"])
            db_instance.add_client(new_cli)
            client_list.append(new_cli)

            return redirect(url_for('index'))

    @app.route('/add_torrents', methods=["POST", "GET"])
    def add_torrents():
        if request.method == "GET":
            return render_template("upload_torrents.html", client_list=client_list)

        if request.method == "POST":
            path = pathlib.Path("success_torrents")
            if not path.exists():
                path.mkdir()

            download_limit = int(request.form["torrents_download_speed"])
            download_type = request.form["download_type"]
            upload_limit = int(request.form["torrents_upload_speed"])
            upload_type = request.form["upload_type"]
            state = True if request.form['state'] == "True" else False
            download_speed = parse_size(download_limit, download_type)
            upload_speed = parse_size(upload_limit, upload_type)
            torrent_set = set()
            old_torrents_set = set(torrent_list)

            torrents = request.files.getlist('file')
            for torrent in torrents:
                try:
                    torrent_data = parseTorrentFile.parse_from_file(torrent)
                except Exception as e:
                    print("ERROR!", e)
                    continue
                if state:
                    downloaded = torrent_data['torrent_size']
                else:
                    downloaded = 0

                sel_client = None
                for i, client in enumerate(client_list):
                    if client.client_name == request.form['client']:
                        sel_client = i
                        break

                cre_torrent = Torrent.create_from_user_input(torrent_data['torrent_name'], torrent_data['torrent_size'],
                                                             download_speed, upload_speed, torrent_data['announce_url'],
                                                             torrent_data['file_hash'], sel_client, downloaded, 0)

                torrent_set.add(cre_torrent)
                torrent.save(pathlib.Path(path / cre_torrent.name))
                torrent.close()

            # now remove duplicates
            torrent_set = torrent_set - old_torrents_set
            if torrent_set:
                db_instance.add_torrents(torrent_set)
            for item in torrent_set:
                torrent_list.append(item)

            return redirect(url_for('index'))

    app.run(port=25564)
