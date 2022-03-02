import io

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

class Drive: 
	def __init__(self, config) -> None:
		# google auth flow, create the service var
		creds = None

		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('token.json'):
			creds = Credentials.from_authorized_user_file('token.json', SCOPES)
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('token.json', 'w') as token:
				token.write(creds.to_json())

		self.service = build('drive', 'v3', credentials=creds)
		self.config = config['GDRIVE']

	def lsf(self) :
		"""
		List drives folders
		"""
		# Call the Drive v3 API
		results = self.service.files().list(q = "mimeType = 'application/vnd.google-apps.folder'", pageSize=900, fields="nextPageToken, files(id, name)").execute()
		folders = results.get('files', [])

		return {folder["name"]: folder["id"] for folder in folders}

	def listChildrenFolder(self, folder_id):
		results = self.service.files().list(q = f'\'{folder_id}\' in parents and mimeType = \'application/vnd.google-apps.folder\'', pageSize=900, fields="nextPageToken, files(id, name)").execute()
		folders = results.get('files', [])

		return {folder["name"]: folder["id"] for folder in folders}
	
	def get_rocketTemp(self):
		results = self.service.files().list(q = f'\'{self.config["RocketTempId"]}\' in parents', pageSize=900, fields="nextPageToken, files(id, name)").execute()
		files = results.get('files', [])

		return {driveFile["name"]: driveFile["id"] for driveFile in files}
		

	def downloadFile(self, file_name, file_id, file_path):
		if os.path.exists(f"{file_path}/{file_name}"):
			name, ext = os.path.splitext(file_name)
			return self.downloadFile(f"{name}-copy{ext}", file_id, file_path)
			
		request = self.service.files().get_media(fileId=file_id)
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		fh = io.FileIO(f"{file_path}/{file_name}", 'wb')
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
			# print(f"Downloading {file_name} → {int(status.progress() * 100)}%")

	
	def moveFile(self, file_id, folder_id, copy=False):
		file = self.service.files().get(fileId=file_id, fields='parents').execute()
		
		if copy:
			previous_parents = ''
		else:
			previous_parents = ",".join(file.get('parents'))

		file = self.service.files().update(
			fileId=file_id,
			addParents=folder_id,
			removeParents=previous_parents,
			fields='id, parents'
		).execute()
	
	def createFolder(self, folder_name, parents=[]):
		folder_metadata = {
			'name': folder_name,
			'parents': parents,
			'mimeType': 'application/vnd.google-apps.folder'
		}

		folder = self.service.files().create(body=folder_metadata, fields='id').execute()

		return folder.get('id')

