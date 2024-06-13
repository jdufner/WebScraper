import argparse
import random
from argparse import Namespace
from datetime import datetime
from flask import Flask, render_template, url_for, request, current_app, redirect, Response
from flask_login import LoginManager, login_required, login_user
import json
import logging
import math
import os
from picturechoice.server.choice import Choice
from picturechoice.server.repository import Repository, SqliteRepository
from picturechoice.server.user import User


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
    image1: (int, str) = __get_random_image(repository)
    image2: (int, str) = __get_random_image(repository)
    return image1, image2


def __is_next_image_not_rated(repository: Repository) -> bool:
    rnd = random.random()
    total_number_images = repository.get_total_number_images()
    number_not_yet_rated_images = repository.get_number_not_yet_rated_images()
    return rnd < 2 * number_not_yet_rated_images / total_number_images


def __get_random_not_yet_rated_image(repository: Repository) -> (int, str):
    rnd = random.random()
    number_not_yet_rated_images = repository.get_number_not_yet_rated_images()
    image: (int, str) = repository.get_not_yet_rated_image_by_row_num(int(rnd * number_not_yet_rated_images) + 1)
    repository.set_image_as_rated_by(image[0])
    return image


def __get_already_rated_image(repository: Repository) -> (int, str):
    rnd = random.random()
    number_already_rated_images = repository.get_number_already_rated_images()
    rnd = math.log2(rnd + 1)
    # rnd = 2 * math.log2(rnd + 1) / math.log2(2 * (rnd + 1))
    image: (int, str) = repository.get_already_rated_image_by_row_num(int(rnd * number_already_rated_images) + 1)
    return image


def __get_random_image(repository: Repository) -> (int, str):
    if __is_next_image_not_rated(repository):
        return __get_random_not_yet_rated_image(repository)
    else:
        return __get_already_rated_image(repository)


def __remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def __next_choice(repository: Repository) -> str:
    image1, image2 = __get_two_random_images(repository)
    timestamp = datetime.now().isoformat()
    return render_template('/choice.html',
                           prefix='',
                           img1=__remove_prefix(image1[1], 'web/'),
                           img2=__remove_prefix(image2[1], 'web/'),
                           img1_id=image1[0],
                           img2_id=image2[0],
                           timestamp=timestamp)


app: Flask = Flask(__name__,
                   static_folder='../../web/static',
                   template_folder='../../web/templates')
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str) -> None | User:
    users: dict = config['security']['users']
    if user_id in users:
        user = User(user_id, users[user_id])
        logging.info(f'user={user}')
        return user
    else:
        logging.info(f'User not found!')
        return None


@login_manager.unauthorized_handler
def unauthorized() -> Response:
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home() -> str:
    return render_template('index.html')
    # return __next_choice(get_repository_from_app_context())


@app.route('/choice', methods=['GET', 'POST'])
@login_required
def choice() -> str:
    if request.method == 'POST':
        __handle_request(get_repository_from_app_context(), request.form)
    return __next_choice(get_repository_from_app_context())


@app.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    users = config['security']['users']
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            user = User(username, password)
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


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
    app.config['SECRET_KEY'] = config['security']['key']
    app.run(debug=True)
