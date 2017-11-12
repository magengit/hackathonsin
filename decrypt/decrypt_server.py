#! /usr/bin/python3
# coding=utf-8
"""
/Users/alenalifar/cisco/Projects/opensource/hackathonsin/decrypt/assets
"""
import argparse
import os
import flask
import sys
import uuid

import requests
from flask import Flask, Blueprint, request

from decrypt.dbx_decrypt import decrypt_file, LOCAL_DIR, get_filename

SERVER_IP = 'localhost'

decrypt_app = Flask(__name__)
decrypt_app.template_folder = 'data/'
decrypt_bp = Blueprint('decrypt_bp', __name__)


def rename_file(f_path):
    dir_path = '/'.join(f_path.split('/')[:-1]) + '/'
    true_filename = get_filename(f_path, SERVER_IP)
    os.rename(f_path, dir_path+true_filename+'.html')


@decrypt_bp.route('/', methods=['GET', 'POST'])
def index():
    return flask.render_template('index.html')


@decrypt_bp.route('/repo/', methods=['GET'])
def get_files():
    repo_files = os.listdir(LOCAL_DIR)
    return flask.render_template('repo.html', files=repo_files)


@decrypt_bp.route('/repo/<req_path>/', methods=['GET'])
def view_file(req_path):
    if request.args.get('raw_view', None):
        return flask.send_file(LOCAL_DIR+req_path)
    if 'html' not in req_path:
        return flask.send_file(LOCAL_DIR+req_path)
    global SERVER_IP
    decrypt_file(LOCAL_DIR+req_path, server_ip=SERVER_IP)
    req_path = '.'.join(req_path.split('.')[:-1])
    out_filename = LOCAL_DIR+req_path+'.out'
    os.rename(out_filename, LOCAL_DIR+req_path)
    with open(LOCAL_DIR+req_path, 'r') as f:
        read_lines = f.readlines()
    read_lines = ' '.join(read_lines)
    return flask.render_template('viewer.html', file=read_lines)


@decrypt_bp.route('/download/', methods=['GET'])
def get_download_form():
    return flask.render_template('ingestion_form.html')


@decrypt_bp.route('/download/', methods=['POST'])
def browse_link():
    link = request.form['link']
    filename = 'tmp_filename' + uuid.uuid4().hex
    if not link:
        return flask.render_template('ingestion_form.html')
    with requests.Session() as session:
        downloaded = session.get(link)
    if downloaded.status_code == 410 or downloaded.status_code == 404:
        return downloaded.content
    with open(LOCAL_DIR+filename, 'wb') as downloaded_file:
        downloaded_file.write(downloaded.content)
    rename_file(LOCAL_DIR+filename)
    return downloaded.content


def main(args):
    parser = argparse.ArgumentParser(description='Magen Decrypt Agent',
                                     usage=("\npython3 dbx_decrypt.py "
                                            "--server-ip"
                                            "\n\nnote:\n"
                                            "root privileges may be required "))
    global SERVER_IP
    parser.add_argument('--server-ip',
                        help='Set Key Server IP and port in form <IP>:<PORT>'
                             'Default is %s' % SERVER_IP)

    args, _ = parser.parse_known_args(args)
    if not args.server_ip:
        print('Default Key Server IP is used... : {}', SERVER_IP)
    else:
        SERVER_IP = args.server_ip

    decrypt_app.register_blueprint(decrypt_bp)
    decrypt_app.run('0.0.0.0', port=5000)


if __name__ == '__main__':
    main(sys.argv[1:])

