import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import pkg_resources
from datetime import date
from concurrent.futures import ThreadPoolExecutor

def uploaddrive():
    def upload_file(file_meta):
        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            pkg_resources.resource_filename(__name__, "penyakitlombok-396692ec95bf.json"), 
            scopes=['https://www.googleapis.com/auth/drive'])

        drive = GoogleDrive(gauth)
        file_name, file_path, folder_id = file_meta

        file = drive.CreateFile({'parents': [{'id': folder_id}], 'title': file_name})
        file.SetContentFile(file_path)
        file.Upload()
        print(f"\n--------- {file_name} is Uploaded ----------")

    today = date.today().strftime("%m/%d/%y")

    folder_name = "Hasil Deteksi"
    parent_directory_id = '1pWwGZTkuX2091DVyIU2ufnFF_13jPRnQ'

    folder_meta = {
        "title":  folder_name,
        "parents": [{'id': parent_directory_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Check if folder already exists or not
    folder_id = None
    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        pkg_resources.resource_filename(__name__, "penyakitlombok-396692ec95bf.json"), 
        scopes=['https://www.googleapis.com/auth/drive'])

    drive = GoogleDrive(gauth)
    foldered_list = drive.ListFile(
        {'q': "'"+parent_directory_id+"' in parents and trashed=false"}).GetList()

    # Check if the folder name already exists, if so, modify the name
    existing_folder_names = [folder['title'] for folder in foldered_list]
    folder_name_base = folder_name
    counter = 1
    while folder_name in existing_folder_names:
        folder_name = f"{folder_name_base}_{counter}"
        counter += 1

    for file in foldered_list:
        if file['title'] == folder_name:
            folder_id = file['id']

    if folder_id is None:
        folder_meta["title"] = folder_name
        folder = drive.CreateFile(folder_meta)
        folder.Upload()
        folder_id = folder['id']

    # Upload files from the output_frames folder
    output_frames_folder = 'output_frames'
    file_list = []

    for root, dirs, files in os.walk(output_frames_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_list.append((file_name, file_path, folder_id))

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(upload_file, file_meta) for file_meta in file_list]

        # Waiting for all uploads to finish
        for future in futures:
            future.result()

    # Generate link to the folder
    folder_obj = drive.CreateFile({'id': folder_id})
    folder_link = folder_obj['alternateLink']

    # Save the folder link to a text file
    with open('folder_link.txt', 'w') as f:
        f.write(folder_link)

    print("\n--------- Folder is Uploaded ----------")
    print(f"Folder Link: {folder_link}")
    print("Folder link saved to folder_link.txt")

# Call the function to upload files to Google Drive
# upload_files_to_gdrive()
