import boto3
import zipfile
import os
import tempfile
import urllib3

def lambda_handler(event, context) -> dict:
    url = "https://eforexcel.com/wp/wp-content/uploads/2020/09/2m-Sales-Records.zip"
    bucket = "iata-pipeline-data"
    key = "raw/2m_sales.csv"

    http = urllib3.PoolManager()

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "file.zip")
        http_response = http.request('GET', url)
        
        with open(zip_path, 'wb') as f:
            f.write(http_response.data)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        for file in os.listdir(tmpdir):
            if file.endswith(".csv"):
                csv_path = os.path.join(tmpdir, file)
                break

        s3 = boto3.client('s3')
        with open(csv_path, 'rb') as f:
            s3.upload_fileobj(f, bucket, key)

    return {
        "statusCode": 200,
        "body": "File uploaded to S3"
    }
