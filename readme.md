# WebScraper

## Introduction and Goals

### Requirements Overview



## Dependencies

### Install From Scratch

    py -m pip install bs4 selenium psycopg

### Create Dependencies File

    py -m pip freeze > requirements.txt

### Install From Dependencies File

    py -m pip install -r requirements.txt

## Database setup

### Execute PostgreSQL script

    C:\Users\jurge>"c:\Program Files\PostgreSQL\16\bin\psql.exe" -U webscraper -d postgres -a -f git-workspace\WebScraper\create_tables_postgres.sql
