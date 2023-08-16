#! /bin/bash 

AWS_PROFILE=RFDataScience aws s3 cp main.csv s3://rfds-ds-twitter/
AWS_PROFILE=RFDataScience aws s3 cp ner_tagged_landmine_tweets.csv s3://rfds-ds-twitter/