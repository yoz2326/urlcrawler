import os

bucket_name = os.environ.get('BUCKET_NAME')

def startCrawl(event, context):
  message = f"Crawler started. Result will be uploaded to s3://{bucket_name}"
  print(message)
  return event, message

if __name__ == "__main__":
    startCrawl('', '')