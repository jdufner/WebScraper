import argparse
from argparse import Namespace
from datetime import datetime
import logging
import os
from downloader.walker import Walker


def __parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-bl', '--blacklist', type=str, default='blacklist.txt',
                        help='Name of the file containing black listed URL that will not be visited.')
    parser.add_argument('-pl', '--print_links', default=False, action='store_true')
    parser.add_argument('-pi', '--print_images', default=False, action='store_true')
    parser.add_argument('-ll', '--log_level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                        default='info', help='Log level for log file.')
    parser.add_argument('-lp', '--log_path', type=str, default='./logs',
                        help='Path to write log file.')
    parser.add_argument('-np', '--number_pages', type=int, default=0,
                        help='Number pages to be scraped.')
    parser.add_argument('url', type=str, default='http://www.heise.de/',
                        help='URL where to start scraping.')
    return parser.parse_args()


if __name__ == '__main__':
    args: Namespace = __parse_arguments()
    now: datetime = datetime.now()
    if not os.path.exists(args.log_path):
        os.makedirs(args.log_path)
    logging.basicConfig(filename=f'{args.log_path}/{now: %Y-%m-%d_%Hh%Mm%Ss}.log',
                        encoding='utf-8',
                        format='%(asctime)s,%(msecs)-3d - %(levelname)-8s - %(filename)s:%(lineno)d - '
                               '%(module)s - %(funcName)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.getLevelNamesMapping()[args.log_level.upper()])
    logging.debug(f'url = {args.url} '
                  f'blacklist = {args.blacklist} '
                  f'print_links = {args.print_links} '
                  f'print_images = {args.print_images} '
                  f'log_level = {args.log_level} '
                  f'logging.level = {logging.getLevelNamesMapping()[args.log_level.upper()]} '
                  f'log_path = {args.log_path} '
                  f'number_pages = {args.number_pages} ')
    Walker(args).walk(args.url, args.number_pages)
