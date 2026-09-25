import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CREDENTIALS_FILE="credentials.json"
IMAGE_FILE="src/x.jpg"

SCOPES=["https://www.googleapis.com/auth/drive"]

def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print("credentials.json not found.")
        return

    if not os.path.exists(IMAGE_FILE):
        print(f"{IMAGE_FILE} not found.")
        return

    creds=Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )

    service=build("drive","v3",credentials=creds)

    file_metadata={
        "name":os.path.basename(IMAGE_FILE)
    }

    media=MediaFileUpload(
        IMAGE_FILE,
        mimetype="image/jpeg"
    )

    file=service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,webViewLink"
    ).execute()

    print("Upload successful!")
    print(f"Name: {file['name']}")
    print(f"ID: {file['id']}")
    print(f"Link: {file.get('webViewLink')}")

if __name__=="__main__":
    main()