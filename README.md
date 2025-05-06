# iata-data-pipeline

Description of the case study :

The dataset is available at: https://eforexcel.com/wp/wp-content/uploads/2020/09/2m-Sales-Records.zip

The solution should consist of a set of AWS Lambda functions that:
- Fetch the ZIP file from the HTTPS endpoint ;
- Uncompress the file ;
- Convert the data to Parquet format ;
- Partition the Parquet data by the Country field and store it in S3 ;
- The original CSV file should be archived under a different prefix within the same S3 bucket ;
- The final Parquet data must be queryable through Athena ;
- The entire solution should be deployable using an IaC (here CloudFormation).

The overall logic and architecture decided for this case will be as follows :

![Data architecture diagram](assets/data_architecture.png)

Below is the breakdown of the logic and components of this above diagram:

1. Data Ingestion (Fetch + Uncompress)

    - A first Lambda function fetches a ZIP file from an HTTPS endpoint.
    - It uncompresses the ZIP and extracts the CSV.
    - The extracted CSV is stored in s3://iata-pipeline-data/raw/original/

2. Data Transformation (Convert + Partition + Archived)
A second Lambda function is automatically triggered when the CSV lands in the raw folder. It performs the following actions:
    - Converts the CSV into Parquet format.
    - Partitions the data based on the Country column.
    - Stores the output in s3://iata-pipeline-data/processed/
    - The original CSV file is moved to an archive folder: s3://iata-pipeline-data/raw/archive/.

3. Schema Registration & Athena querying
    - A Glue Crawler scans the processed folder and extracts the data schema.
    - The schema is saved in the AWS Glue Data Catalog.
    - A Glue Database is created from this schema.

    -> The structured data can now be queried with SQL using Amazon Athena.

Improvements:

I also would like to :
    - Run data validation checks in step 3. And also automatically trigger a Glue Crawler for schema update ;
    - And save metadata in s3://iata-pipeline-data/metadata/ as demanded.
