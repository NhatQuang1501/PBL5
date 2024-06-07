from google.cloud import storage
from google.oauth2 import service_account
import os

def test_access(bucket_name, object_name, credentials_path):
    # Specify the path to your service account key file
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    # Create a storage client with the specified credentials
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    if blob.exists():
        print(f"Object '{object_name}' exists in bucket '{bucket_name}'.")
    else:
        print(f"Object '{object_name}' does not exist in bucket '{bucket_name}'.")

def download_audio_file_from_storage(bucket_name, file_url, local_file_path):
    try:
        # Extract the blob_name from the file_url
        if file_url.startswith('gs://'):
            blob_name = file_url[len('gs://' + bucket_name + '/'):]  # Remove 'gs://bucket_name/'
        elif file_url.startswith(f'https://storage.googleapis.com/{bucket_name}/'):
            blob_name = file_url[len(f'https://storage.googleapis.com/{bucket_name}/'):]  # Remove full URL
        else:
            raise ValueError(f"Invalid file_url format: {file_url}")

        # Initialize Google Cloud Storage client.
        storage_client = storage.Client()

        # Get the bucket and blob (object) from the specified bucket name and blob name.
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Check if the blob (object) exists.
        if not blob.exists():
            raise ValueError(f"Blob '{blob_name}' does not exist in bucket '{bucket_name}'.")

        # Download the audio file to the specified local path.
        blob.download_to_filename(local_file_path)
        print(f"Successfully downloaded '{blob_name}' to '{local_file_path}'.")
        return True

    except ValueError as ve:
        print(f"Error: {ve}")
        return False

    except Exception as e:
        print(f"Error downloading audio file: {str(e)}")
        return False

# Test access to the object
test_access("pbl5-nhom7.appspot.com", "audio67.wav", "D:\\PBL5\\pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\PBL5\\pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json"
bucket_name = 'pbl5-nhom7.appspot.com'
file_url = 'gs://pbl5-nhom7.appspot.com/audio67.wav'
local_file_path = 'webai/downloaded_audio.wav'

# Download the audio file from Google Cloud Storage
success = download_audio_file_from_storage(bucket_name, file_url, local_file_path)

if success:
    print(f"Downloaded audio file to: {local_file_path}")
else:
    print("Failed to download audio file.")
