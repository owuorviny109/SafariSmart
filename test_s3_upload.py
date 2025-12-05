import boto3
import os
from botocore.exceptions import ClientError
from decouple import config

# Load credentials from .env
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

print(f"Testing S3 Connection...")
print(f"Bucket: {AWS_STORAGE_BUCKET_NAME}")
print(f"Key ID: {AWS_ACCESS_KEY_ID[:5]}...{AWS_ACCESS_KEY_ID[-5:]}")

# Create S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)

# 1. Try to List Files (Checks Read Permission)
print("\n1. Testing READ permission (List Objects)...")
try:
    response = s3.list_objects_v2(Bucket=AWS_STORAGE_BUCKET_NAME, MaxKeys=5)
    if 'Contents' in response:
        print("✅ Success! Found files:")
        for obj in response['Contents']:
            print(f" - {obj['Key']}")
    else:
        print("✅ Success! Bucket is empty but accessible.")
except ClientError as e:
    print(f"❌ FAILED: {e}")

# 2. Try to Upload File (Checks Write Permission)
print("\n2. Testing WRITE permission (Upload)...")
test_filename = 'test_upload.txt'
with open(test_filename, 'w') as f:
    f.write('This is a test upload from SafariSmart developer.')

try:
    s3.upload_file(
        test_filename, 
        AWS_STORAGE_BUCKET_NAME, 
        test_filename
    )
    print(f"✅ Success! Uploaded {test_filename}")
    print(f"URL: https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{test_filename}")
except ClientError as e:
    print(f"❌ FAILED: {e}")

# Cleanup
if os.path.exists(test_filename):
    os.remove(test_filename)
