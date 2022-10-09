from flask import Flask, render_template

app = Flask(__name__)


def main(torrent_list, client_list):
    @app.route('/')
    def index():
        return render_template('index.html', torrent_list=torrent_list, client_list=client_list)

    @app.route('/clients')
    def display_client_data():
        return render_template('clients_page.html', client_list=client_list)

    @app.route('/edit_client/<string:client_name>')
    def edit_client(client_name):
        return client_name

    app.run(port=25565, debug=False)
