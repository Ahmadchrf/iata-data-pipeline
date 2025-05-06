import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io

s3 = boto3.client('s3')

class ToParquet:

    bucket = 'iata-pipeline-data'
    input_key = 'raw/original/2m_sales.csv'
    archive_key = 'raw/archive/2m_sales_archived.csv'
    clean_key = 'processd/'

    def __init__(self):
        obj = s3.get_object(Bucket=self.bucket, Key=self.input_key)
        csv_content = obj['Body'].read().decode('utf-8')
        self.df = pd.read_csv(io.StringIO(csv_content))

    def save_data_parquet_partitioned(self):
        for country in self.df['Country'].unique():
            df_country = self.df[self.df['Country'] == country]
            table = pa.Table.from_pandas(df_country)

            buf = io.BytesIO()
            pq.write_table(table, buf)
            buf.seek(0)

            filename = f"{self.clean_key}country={country}/2m_sales.parquet"
            s3.upload_fileobj(buf, self.bucket, filename)

    def archive_original_csv(self):
        s3.copy_object(
            Bucket=self.bucket,
            CopySource={'Bucket': self.bucket, 'Key': self.input_key},
            key=self.archive_key
        )
        s3.delete_object(Bucket=self.bucket, Key=self.input_key)


## still have to add some validation tests and trigger glue crawler (improvements)


def lambda_handler(event, context):
    tp = ToParquet()

    tp.save_data_parquet_partitioned()
    tp.archive_original_csv()
    return {
        "statusCode": 200,
        "body": "CSV data converted to Parquet and archived with country as partition key."
    }
