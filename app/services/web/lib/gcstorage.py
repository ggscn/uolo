from google.cloud import storage

from google.oauth2 import service_account
import json
import six
import os
import base64
from io import BytesIO

class Bucket():
    def __init__(self, bucket_name='fyllo'):
        credentials = self.get_credentials()
        self.client = storage.Client(project='fyllo-237201',credentials=credentials)
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(self.bucket_name)

    def get_credentials(self):
        credentials_raw = os.environ.get('GOOGLE_CREDENTIALS')
        service_account_info = json.loads(credentials_raw)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info)
        return credentials

    def create_bucket(self, bucket_name):
        self.client.create_bucket(bucket_name)

    def upload_photo(self, img_b64, filename, folder='plant-photos'):
        img_str = base64.b64decode(
            img_b64.encode('UTF-8'))

        destination_filename = '{}/{}'.format(
            folder, filename)

        public_url = self.upload_blob_from_bytes(
            img_str, destination_filename, make_public=True).public_url

        return public_url, destination_filename

    def upload_blob_from_file(self, source_file_name, destination_blob_name, make_public=False):
        """Uploads a file to the bucket."""
        bucket = self.bucket
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        if make_public:
            blob.make_public()
        return blob

    def upload_blob_from_bytes(self, file_obj, destination_blob_name, make_public=False):
        try:
            bucket = self.bucket
            blob = bucket.blob(destination_blob_name)

            blob.upload_from_string(file_obj, content_type='image/jpeg')

            if make_public:
                blob.make_public()
            return blob          

        except Exception as e:
            print(e)

        return None

    def delete_blob(self, blob_name):
        blob = self.bucket.blob(blob_name)
        blob.delete()

