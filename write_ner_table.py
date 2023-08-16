# import libraries
import pandas as pd
from mysql.connector import (connection)
import os
from mysql.connector import Error
from pipelines.database.sql import SQLCaller

# SQL connection ------------------------------------------------------------------

# fetch values from environment variables and set the target database
hostname = os.environ['MYSQL_HOST']
username = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
dbname = 'found'

# establish connection to db1 database in your mysql service
cnx = connection.MySQLConnection(user=username,
                                 password=password,
                                 host=hostname,
                                 database=dbname)

# connect to sql
from mysql.connector import (connection)
from mysql.connector import Error

# fetch values from environment variables and set the target database
hostname = os.environ['MYSQL_HOST']
username = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
dbname = 'found'

# establish connection to db1 database in your mysql service
cnx = connection.MySQLConnection(user=username,
                                 password=password,
                                 host=hostname,
                                 database=dbname)


# Load all functions ------------------------------------------------------------
def create_sql_query(csv):
    """
    Function takes in a NER tags dataframe and creates the sql query to write to table
    csv = csv file as string
    """
    df = pd.read_csv(csv)
    columns = list(df.columns)
    column_str = f"({', '.join(columns)})"
    insert_placeholder = ", ".join(["%s" for _ in column_str.split(",")])
    ner_val_dict = df.dropna().to_dict("records")
    save_data = [tuple(row.values()) for row in ner_val_dict]
    ner_query = f"INSERT INTO ner_tagged_landmine_tweets {column_str} VALUES ({insert_placeholder});"
    return ner_query


# Read in csv files and write to SQL  ------------------------------------------------------------------
csv_list = ["landmine_tweets_ner_results_non_eng_clean.csv", "landmine_tweets_ner_results_eng_clean.csv"]

for csv in csv_list:
    ner_query = create_sql_query(csv)
    sql = SQLCaller()
    sql.run_insert_query(ner_query, save_data)