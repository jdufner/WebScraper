import argparse
from argparse import Namespace
from datetime import datetime
from flask import Flask, render_template, url_for, request, app
import json
import logging
import os

from picturechoice.server.choice import Choice
from picturechoice.server.repository import Repository


class PictureChoiceServer:
    def __init__(self, config: dict):
        self.config = config


def __parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='A file containing all necessary config.')
    return parser.parse_args()


def __load_config() -> dict:
    args: Namespace = __parse_arguments()
    file = open(args.file)
    conf: dict = json.load(file)
    file.close()
    return conf


app: Flask = Flask(__name__,
                   static_folder='../../web/static',
                   template_folder='../../web/templates')


@app.route('/')
def home():
    timestamp = datetime.now().isoformat()
    return render_template('/index.html',
                           img1='/static/images/Pfau.jpg',
                           img2='/static/images/Chilis.jpg',
                           timestamp=timestamp)


@app.route('/choice', methods=['POST'])
def on_click():
    handle_request(request.form)

    timestamp = datetime.now().isoformat()
    return render_template('/index.html',
                           img1='/static/images/Pfau.jpg',
                           img2='/static/images/Chilis.jpg',
                           timestamp=timestamp)


def handle_request(param: dict) -> None:
    request_timestamp: datetime = datetime.fromisoformat(param['timestamp'])
    request_first: str = param['first']
    request_second: str = param['second']
    logging.info(f'timestamp = {request_timestamp}, first = {request_first}, second = {request_second}')
    choice = Choice(request_timestamp, request_first, request_second)
    repository.save(choice)


if __name__ == '__main__':
    config: dict = __load_config()
    now: datetime = datetime.now()
    if not os.path.exists(config["logging"]["path"]):
        os.makedirs(config["logging"]["path"])
    logging.basicConfig(filename=f'{config["logging"]["path"]}/{now: %Y-%m-%d_%Hh%Mm%Ss}_main.log',
                        encoding='utf-8',
                        format='%(asctime)s,%(msecs)-3d - %(levelname)-8s - %(filename)s:%(lineno)d - '
                               '%(module)s - %(funcName)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.getLevelNamesMapping()[config["logging"]["level"].upper()])
    repository = Repository(config)
    app.run(debug=True)
