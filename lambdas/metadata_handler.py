import boto3

glue=boto3.client('glue')

def lambda_handler(event,context):
    
    response = glue.start_crawler(Name='IataCrawler-data')
    
    ##still have to add metadata save in s3, check get_paginator method
    return {
        "statusCode": 200,
        "body": "New metadat generated with the Crawler"
    }