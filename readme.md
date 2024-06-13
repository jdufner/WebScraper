# WebScraper

## Introduction and Goals

### Requirements Overview



## Dependencies

| Name                   | Library          | Purpose                                  |
|:-----------------------|------------------|------------------------------------------|
| OpenCV                 | opencv-python    |                                          |
| Beautiful Soup         | bs4              |                                          |
| PostgresSQL Connection | psycopg[binary]  | Library to connect to PostgreSQL server. |
| Selenium               | selenium         |                                          |
| Sqlite                 | sqlite           |                                          |
| Certificates for SSL   | pip-system-certs |                                          |


### Install From Scratch

    py -m pip install bs4 selenium psycopg[binary]

### Create Dependencies File

    py -m pip freeze > requirements.txt

### Install From Dependencies File

    py -m pip install -r requirements.txt

## Database setup

### Execute PostgreSQL script

    C:\Users\jurge>"c:\Program Files\PostgreSQL\16\bin\psql.exe" -U webscraper -d postgres -a -f git-workspace\WebScraper\create_tables_postgres.sql

## Solution Strategy

### Ranker

#### Images to be ranked

##### Requirements

1. Images without rating should be displayed more often then already rated images.
2. High rated images should be displayed more often than low rated images.
3. Images with old rating should be displayed more often than newly rated images.

Constants

    probability_not_yet_displayed_images = 0.8
    probability_high_rated_images = 0.5
    probability_older_rated_images = 0.2

Variables

    total_number_images
    number_of_not_yet_rated_images
    number_of_already_rated_images
    quotient_not_yet_rated_images = number_of_not_yet_rated_images / total_number_images
    quotient_already_rated_images = number_of_already_rated_images / total_number_images

