import boto3
import json
import datetime as dt
import io


bucket='iata-pipeline-data'
key='metadata'


def upload_to_s3(data, bucket, path):
    s3=boto3.client('s3')
    json_bytes = json.dumps(data).encode('utf-8')
    s3.upload_fileobj(io.BytesIO(json_bytes), bucket, path)
    
    
def lambda_handler(event,context):
    
    glue=boto3.client('glue')
    # crawler run
    response = glue.start_crawler(Name='IataCrawler-data')
    
    #Save schema in s3
    paginator = glue.get_paginator('get_tables')
    pages = paginator.paginate(DatabaseName='iata_datadb')
    current_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    all_tables = []
    for page in pages:
        for element in page['TableList']:
            all_tables.append({
                'TableName': element['Name'],
                'Columns': [{'Name': col['Name'], 'Type': col['Type']}
                    for col in element['StorageDescriptor']['Columns']
                ]
            })
            
    file_path = f'{key}/metadata_{current_time}.json'
    upload_to_s3(all_tables,bucket, file_path)
    
    return {
        'statusCode': 200,
        'body': json.dumps(all_tables)
    }