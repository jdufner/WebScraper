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
