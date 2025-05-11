import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io

s3 = boto3.client('s3')

class ToParquet:
    def __init__(self, bucket, input_key, archive_key, clean_key):
        self.bucket = bucket
        self.input_key = input_key
        self.archive_key = archive_key
        self.clean_key = clean_key
        self.df = None
        
    def load_latest_csv(self):
        response = s3.list_objects_v2(Bucket=self.bucket, Prefix=self.input_key)
        csv_files = [obj for obj in response['Contents'] if '.csv' in obj['Key']]
        latest_file = sorted(csv_files, key=lambda x: x['LastModified'], reverse=True)[0]
        self.input_key = latest_file['Key']
        self.archive_key = self.input_key.replace('raw/original/', 'raw/archive/')

        obj = s3.get_object(Bucket=self.bucket, Key=self.input_key)
        csv_content = obj['Body'].read().decode('utf-8')
        self.df = pd.read_csv(io.StringIO(csv_content))
        self.df['order date'] = pd.to_datetime(self.df['order date'], errors='coerce')
        self.df['ship date'] = pd.to_datetime(self.df['ship date'], errors='coerce')

    def save_data_parquet_partitioned(self):
        for country in self.df['Country'].unique():
            df_country = self.df[self.df['Country'] == country]
            table = pa.Table.from_pandas(df_country)

            buf = io.BytesIO()
            pq.write_table(table, buf)
            buf.seek(0)

            filename = f"{self.clean_key}country={country}/data_2msales_{country}.parquet"
            s3.upload_fileobj(buf, self.bucket, filename)

    def archive_original_csv(self):
        s3.copy_object(
            Bucket=self.bucket,
            CopySource={'Bucket': self.bucket, 'Key': self.input_key},
            Key=self.archive_key
        )
        s3.delete_object(Bucket=self.bucket, Key=self.input_key)

def lambda_handler(event, context):
    tp = ToParquet(bucket="iata-pipeline-data",input_key="raw/original/", archive_key="raw/archive/",clean_key="processd/")

    tp.load_latest_csv()
    tp.save_data_parquet_partitioned()
    tp.archive_original_csv()
    
    return {
        "statusCode": 200,
        "body": "CSV data converted to Parquet and archived with country as partition key"}