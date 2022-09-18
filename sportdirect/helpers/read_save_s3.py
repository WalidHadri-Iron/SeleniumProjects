import boto3  # pip install boto3

def download_file(Bucket, FileName, Key):
    """
    In AWS Lambda make sure to use Filename = "/temp/"+file_name
    """

    # Let's use Amazon S3
    s3 = boto3.resource("s3")
    
    # Download the file
    s3.download_file(Bucket=Bucket, Filename=FileName, Key=Key)

def save_file(Bucket, FileName, Key):
    
    # Let's use Amazon S3
    s3 = boto3.resource("s3")
    
    #Upload file
    s3.upload_file(Filename=FileName,Bucket=Bucket,Key=Key)



