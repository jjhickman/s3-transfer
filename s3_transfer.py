import os
import argparse
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')

def create_presigned_url(client, bucket_name, object_name, expiration=3600):
  try:
    response = client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
    print(response)
  except ClientError as e:
    print(e)
    return None
  return response

def download_file(client, bucket, object_name, file_name=None):
  if file_name is None:
    file_name = os.path.basename(object_name)
  client.download_file(bucket, object_name, file_name)

def upload_file(client, bucket, object_name=None, file_name="hello.txt"):
  if object_name is None:
    object_name = file_name

  try:
    response = client.upload_file(file_name, bucket, object_name)
    print(response)
  except ClientError as e:
    print(e)
    return False
  return True

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-k", "--key", type=str, default=(str(os.getenv("AWS_ACCESS_KEY_ID")) if os.getenv("AWS_ACCESS_KEY_ID") else ""), help="AWS Access Key ID (defaults to AWS_ACCESS_KEY_ID environment variable if defined)")
  parser.add_argument("-s", "--secret", type=str, default=(str(os.getenv("AWS_SECRET_ACCESS_KEY")) if os.getenv("AWS_SECRET_ACCESS_KEY") else ""), help="AWS Secret Access Key")
  parser.add_argument("-t", "--token", type=str, default=(str(os.getenv("AWS_SESSION_TOKEN")) if os.getenv("AWS_SESSION_TOKEN") else ""), help=" AWS session token - only needed with temporary credentials")

  parser.add_argument("-b", "--bucket", type=str, default=(str(os.getenv("AWS_S3_BUCKET")) if os.getenv("AWS_S3_BUCKET") else ""), help="AWS S3 Bucket Name (must exist)")
  parser.add_argument("-o", "--object", type=str, default=(str(os.getenv("AWS_S3_OBJECT")) if os.getenv("AWS_S3_OBJECT") else "hello.txt"), help="AWS S3 object name in bucket")
  parser.add_argument("-f", "--file", type=str, default=(str(os.getenv("AWS_S3_FILE")) if os.getenv("AWS_S3_FILE") else "hello.txt"), help="Local file name")

  mode_group = parser.add_mutually_exclusive_group()
  mode_group.add_argument("-u", "--upload", action="store_true", help="Enable upload mode (default)")
  mode_group.add_argument("-d", "--download", action="store_true", help="Enable download mode")

  presigned_url_group = parser.add_argument_group()
  presigned_url_group.add_argument("-p", "--presigned_url", action="store_true", help="Generate a pre-signed URL for temporary access")
  presigned_url_group.add_argument("-e", "--expiration", type=int, default=3600, help="Presigned URL expiration time in seconds (default: 3600)")
  args = parser.parse_args()

  if args.token:
    s3_client = boto3.client(
      's3',
      aws_access_key_id=args.key,
      aws_secret_access_key=args.secret,
      aws_session_token=args.token
    )
  else:
    s3_client = boto3.client(
      's3',
      aws_access_key_id=args.key,
      aws_secret_access_key=args.secret,
      aws_session_token=args.token
    )

  if args.upload:
    upload_file(s3_client, args.bucket, args.object, args.file)
  elif args.download:
    download_file(s3_client, args.bucket, args.object, args.file)
  elif not args.presigned_url:
    print("No actionable arguments!")
    parser.print_usage()
    exit(1)

  if args.presigned_url:
    create_presigned_url(s3_client, args.bucket, args.object, args.expiration)
  
  print("Done!")
  exit(0)