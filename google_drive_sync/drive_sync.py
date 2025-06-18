import os.path
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveSync:
    def __init__(self, local_path="tasks.json", remote_name="tasks.json"):
        self.local_path = local_path
        self.remote_name = remote_name
        self.creds = None
        self.service = self.authenticate()

    def authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        return build('drive', 'v3', credentials=self.creds)

    def upload_file(self):
        from googleapiclient.http import MediaFileUpload
        print(f"Attempting to upload: {self.local_path}")
        response = self.service.files().list(q=f"name='{self.remote_name}'", fields="files(id)").execute()
        files = response.get('files', [])
        media = MediaFileUpload(self.local_path, resumable=True, mimetype='application/json')

        if files:
            file_id = files[0]['id']
            self.service.files().update(fileId=file_id, media_body=media).execute()
            print(f"Uploaded to Google Drive: {self.remote_name}")
        else:
            self.service.files().create(body={"name": self.remote_name}, media_body=media).execute()

    def download_file(self):
        results = self.service.files().list(q=f"name='{self.remote_name}'", fields="files(id)").execute()
        files = results.get('files', [])
        if not files:
            print("No remote tasks.json found, skipping download")
            return
        file_id = files[0]['id']
        request = self.service.files().get_media(fileId=file_id)
        with open(self.local_path, 'wb') as f:
            from googleapiclient.http import MediaIoBaseDownload
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()