import dropbox
import json
import io
import webbrowser
import datetime


APPKEY = 'appkey'
APPSECRET = 'appsecret'
REF = 'ref'
INSTRUCTIONS = 'https://stackoverflow.com/questions/70641660/how-do-you-get-and-use-a-refresh-token-for-the-dropbox-api-python-3-x'


def get_files_from_folder(folder_path=''):
    try:
        client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
        # List files in the specified folder
        files = client.files_list_folder(folder_path).entries

        # Extract file names
        file_names = [file.name for file in files]
    except:
        file_names = []

    return file_names


def upload_data(data, FILE_PATH='/log_data.json'):
    # Convert data to JSON string
    json_data = json.dumps(data)

    # Initialize Dropbox client
    client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    if get_files_from_folder('').__contains__(FILE_PATH[1:]):
        client.files_delete(FILE_PATH)
        print("file deleted")
    else:
        print("No file {} found".format(FILE_PATH[1:]))
    # Upload the JSON data to Dropbox
    response = client.files_upload(json_data.encode('utf-8'), FILE_PATH)

    # Check if the upload was successful
    if response:
        print('Data uploaded successfully: {}'.format(response))
    else:
        print('Data upload failed: {}'.format(response))


def load_data(FILE_PATH='/log_data.json'):
    client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    _, res = client.files_download(FILE_PATH)

    with io.BytesIO(res.content) as stream:
        data = json.load(stream)
    print(data)


def delete_file(FILE_PATH='/log_data.json'):
    client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    if get_files_from_folder('').__contains__(FILE_PATH[1:]):
        client.files_delete(FILE_PATH)
    else:
        print("No file {} found".format(FILE_PATH[1:]))


def create_file(FILE_PATH='/log_data.json'):
    client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    response = client.files_upload("".encode('utf-8'), FILE_PATH)
    if response:
        print('File created successfully: {}'.format(response))
    else:
        print('File created failed: {}'.format(response))


def help_dropbox():
    print("Instructions on how to connect to dropbox")
    webbrowser.open(INSTRUCTIONS)


def download_data(DROPBOX_FILE_PATH='/log_data.json', LOCAL_FILE_PATH='logdownload.json'):
    client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    _, res = client.files_download(DROPBOX_FILE_PATH)
    with io.BytesIO(res.content) as stream:
        data = json.load(stream)
    print(data)
    json.dump(data, open(LOCAL_FILE_PATH, "w"), indent=4)


def upload_file(DROPBOX_FILE_PATH='/log_data.json', LOCAL_FILE_PATH='logupload.json'):
    data = open(LOCAL_FILE_PATH, 'r')
    json_data = json.dumps(data.read())

    # Initialize Dropbox client
    client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    if get_files_from_folder('').__contains__(DROPBOX_FILE_PATH[1:]):
        client.files_delete(DROPBOX_FILE_PATH)
    else:
        print("No file {} found".format(DROPBOX_FILE_PATH[1:]))
    # Upload the JSON data to Dropbox
    response = client.files_upload(json_data.encode('utf-8'), DROPBOX_FILE_PATH)
    if response:
        print('File uploaded successfully: {}'.format(response))
    else:
        print('File upload failed: {}'.format(response))


if __name__ == "__main__":
    # data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

    delete_file(FILE_PATH='/log_data.json')
    now = json.dumps(datetime.datetime.now(), default=str)
    upload_data([
    {"Temperature": 10, "AirHumidity": 52, "SoilHumidity": 62, "WindowsOpened": 2.5, "CreationDateTime": now},
    {"Temperature": 15, "AirHumidity": 16, "SoilHumidity": 25, "WindowsOpened": 30, "CreationDateTime": now}
])
    #upload_data([{'open': 1}, {'open': 2}], FILE_PATH='/log_open.json')
    #files = get_files_from_folder()





