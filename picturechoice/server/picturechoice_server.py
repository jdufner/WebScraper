import argparse
from argparse import Namespace
from datetime import datetime
from flask import Flask, render_template, url_for, request, app, current_app
import json
import logging
import os
from picturechoice.server.choice import Choice
from picturechoice.server.repository import Repository, SqliteRepository


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


def __handle_request(repository: Repository, param: dict) -> None:
    request_timestamp: datetime = datetime.fromisoformat(param['timestamp'])
    request_first: str = param['first']
    request_second: str = param['second']
    choice = Choice(request_timestamp, request_first, request_second)
    repository.save_choice(choice)


def __get_two_random_images(repository: Repository) -> ((int, str), (int, str)):
    image1: (int, str) = repository.get_random_image()
    image2: (int, str) = repository.get_random_image()
    while image1[0] == image2[0]:
        image2 = repository.get_random_image()
    return image1, image2


def __next_choice(repository: Repository) -> str:
    image1, image2 = __get_two_random_images(repository)
    timestamp = datetime.now().isoformat()
    return render_template('/index.html',
                           prefix='/static/images/',
                           img1=image1[1],
                           img2=image2[1],
                           timestamp=timestamp)


app: Flask = Flask(__name__,
                   static_folder='../../web/static',
                   template_folder='../../web/templates')


@app.route('/')
def home() -> str:
    return __next_choice(get_repository_from_app_context())


@app.route('/choice', methods=['POST'])
def on_click() -> str:
    __handle_request(get_repository_from_app_context(), request.form)
    return __next_choice(get_repository_from_app_context())


def __get_repository() -> Repository:
    if config["database"]["type"].lower() == 'postgres':
        # repository: Repository = PostgresqlRepository(config)
        pass
    else:
        repository: Repository = SqliteRepository(config)
    return repository


def get_repository_from_app_context() -> Repository:
    return current_app.config['repository']


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
    with app.app_context():
        app.config['repository'] = __get_repository()
    app.run(debug=True)
