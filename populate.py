import sqlite3
import pymysql
import pandas as pd
import os
import string 
import random

# prepare connection

host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
database = os.getenv('MYSQL_DATABASE')


local = sqlite3.connect('test.db')

remote = pymysql.connect(
    host=host,
    port=int(3306),
    user=user,
    passwd=password,
    db=database)

# query updates

## user table

current = pd.read_sql_query(
    "SELECT * FROM user \
        ORDER BY id DESC \
            LIMIT 1",
    local, parse_dates='last_seen'
)

user = pd.read_sql_query(
    "SELECT * FROM user \
        WHERE id > "+ str(current.iloc[0]['id']),
    remote, index_col='id'
)

## employee table

current = pd.read_sql_query(
    "SELECT * FROM employee \
        ORDER BY id DESC \
            LIMIT 1",
    local, parse_dates='join_date'
)

employee = pd.read_sql_query(
    "SELECT * FROM employee \
        WHERE id > "+ str(current.iloc[0]['id']),
    remote, index_col='id'
)

## workshop table

current = pd.read_sql_query(
    "SELECT * FROM workshop \
        ORDER BY id DESC \
            LIMIT 1",
    local, parse_dates='workshop_start'
)

workshop = pd.read_sql_query(
    "SELECT * FROM workshop \
        WHERE id > "+ str(current.iloc[0]['id']),
    remote, index_col='id'
)

## response table

current = pd.read_sql_query(
    "SELECT * FROM response \
        ORDER BY id DESC \
            LIMIT 1",
    local
)

response = pd.read_sql_query(
    "SELECT * FROM response \
        WHERE id > "+ str(current.iloc[0]['id']),
    remote, index_col='id'
)

## assisstant table

current = pd.read_sql_query(
    "SELECT * FROM assistants \
        ORDER BY workshop_id DESC \
            LIMIT 1",
    local
)

assistant = pd.read_sql_query(
    "SELECT * FROM assistants \
        WHERE workshop_id > "+ str(current.iloc[0]['id']),
    remote, index_col='id'
)

# mask data

## prepare dictionary

letters = list(string.ascii_lowercase)

## randomize function

def rand(stri):
    return random.choice(letters)

## mask new data

employee['name'] = employee['name'].str.replace('[a-z]', rand)
workshop['workshop_name'] = workshop['workshop_name'].str.replace('[a-zA-Z]', rand)
workshop['workshop_venue'] = workshop['workshop_venue'].str.replace('[a-zA-Z]', rand)

# append to local table

if not user.empty:
    user.to_sql('user', con=local, if_exists = 'append')

if not employee.empty:
    employee.to_sql('employee', con=local, if_exists = 'append')

if not workshop.empty:
    workshop.to_sql('workshop', con=local, if_exists = 'append')

if not response.empty:
    response.to_sql('response', con=local, if_exists = 'append')

