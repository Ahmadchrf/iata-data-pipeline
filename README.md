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
- The entire solution should be deployable using an IaC (here CloudFormation as demanded).

The overall logic and architecture decided for this case will be as follows - MVP:

![Data architecture diagram](assets/data_architecture.png) 

Below is the documentation of the project : https://app.eraser.io/workspace/ok6MHw4bd8vew4ZQe5Oy?origin=share

**Repo Explanation**

- cloudformation :
    Contains Infrastructure as Code (IaC) templates to deploy all required AWS resources.

- lambdas:
    Contains the Lambda function source code:
    * fetch_handler.py – handles Step 1: fetching and uncompressing the file.
    * process_handler.py – handles Step 2: converting to Parquet, partitioning, and archiving.
    * metadata_handler.py – handles Step 4: Running Crawler with s3 trigger and saving only schema.

- assets:
    Contains utility files such as images, architecture diagrams, and other documentation assets.


The final s3 structure : [s3 structure](assets/s3_structure.png)