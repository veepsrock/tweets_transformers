# read in libraries
import pandas as pd
import numpy as np
import re
import os
import json
import sys
import datetime as dt
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from tner import TransformersNER

# connect to sql
from mysql.connector import (connection)
from mysql.connector import Error

# load functions
with open('project_config.json','r') as fp: 
    project_config = json.load(fp)

module_path = os.path.join(project_config['project_module_relative_path'])
sys.path.append(module_path)

from ner.ner_processing import *




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

# query database ---------------------------------------------------------------------
query =("SELECT * FROM landmine_tweets WHERE date > CURDATE() - INTERVAL 4 day")

#write to df and remove duplicates
df = pd.read_sql_query(query, cnx)
df = df.drop_duplicates(subset=['tweet', 'handle'], keep="first")
df.columns = df.columns.str.lower()

# detect language --------------------------------------------------------------------
nlp = en_core_web_sm.load()

# load spacy nlp model
nlp_model = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp_model.add_pipe('language_detector', last=True)

# create a language column on dataframe
df["language"]= df["tweet"].apply(get_language)


# separate dataframe by eng and non eng tweets --------------------------------------------
# create dataframe for non english tweets
non_eng = df[df["language"] != "en"]

# write to csv
non_eng.to_csv("landmine_tweets_non_eng_processed.csv", index = False)

# create dataframe for english tweets
en = df[df["language"]=="en"]

# clean text on english tweets
en =  clean_tweets(en, 'tweet')

# write to csv
en.to_csv("landmine_tweets_eng_processed.csv", index = False)

# write back to main tweeets file
main = pd.read_csv("main.csv")
main = pd.concat([non_eng, en, main])
main['date']= main['date'].astype(str)
main = main.drop_duplicates(subset=['id', 'handle', 'date'])
main.to_csv("main.csv", index = False)

# run model for eng tweets --------------------------------------------
model = TransformersNER("tner/bert-large-tweetner7-2020")

# list comprehension to combine all ner records
tner_records = []
for row_dict in en.to_dict(orient="records"):
    for ner_tag_dict in [model.predict([row_dict["tweet"]])]:
        for i in range(len(ner_tag_dict['prediction'][0])):
                results_dict = create_dict(i, ner_tag_dict)
                tner_records.append({**row_dict, **results_dict})


# create ner results df
tner_df = create_ner_tag_df_en(tner_records, "tner/bert-large-tweetner7-2020")
tner_df['tagged_text'] = tner_df['tagged_text'].fillna(" ")


# recombine ner tags -----------------------------------------------------------------------

# recombine NER tags
tner_df_combined = combine_ner_tags(tner_df, " ")

# write to csv
tner_df_combined.to_csv("landmine_tweets_ner_results_eng_clean.csv", index = False)


# run model for non eng tweets --------------------------------------------
if non_eng.shape[0]!=0:

    tokenizer = AutoTokenizer.from_pretrained("Davlan/bert-base-multilingual-cased-ner-hrl")
    model = AutoModelForTokenClassification.from_pretrained("Davlan/bert-base-multilingual-cased-ner-hrl")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)

    # apply ner model for non eng tweets
    non_eng["ner"] = non_eng["tweet"].apply(nlp)

    # list comprehension to combine all ner records
    ner_records = []
    for row_dict in non_eng.to_dict(orient="records"):
        for ner_tag_dict in nlp(row_dict["tweet"]):  # I Don't recall exact ner model function call
            ner_records.append({**row_dict, **ner_tag_dict})

    # create ner tag df
    ner_df = create_ner_tag_df_multi(ner_records, "Davlan/bert-base-multilingual-cased-ner-hrl")

    # removing all English characters from ner tag df because the multilingual model isn't great for English text

    # detect language of ner tags
    ner_df["language"]= ner_df["tagged_text"].apply(isEnglish)

    # drop English rows
    ner_df= ner_df[ner_df["language"] == False].drop(columns="language", axis=True)

    # cleaning text
    ner_df['tagged_text'] = ner_df['tagged_text'].fillna(" ")
    ner_df['tagged_text'] = ner_df["tagged_text"].str.replace("##", "")

    # recombine NER tags
    ner_df_combined = combine_ner_tags(ner_df, "")

    # write to csv
    ner_df_combined.to_csv("landmine_tweets_ner_results_non_eng_clean.csv", index = False)

else:
    print("No non-English tweets today")
