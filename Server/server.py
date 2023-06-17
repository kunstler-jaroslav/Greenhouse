from flask import Flask, json, request
from flask_cors import CORS
import dropbox
import io

APPKEY = 'appkey'
APPSECRET = 'apppsecret'
REF = 'ref'
DATA_PATH = '/log_data.json'
OPEN_PATH = '/log_open.json'

client = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
_, res = client.files_download(DATA_PATH)
with io.BytesIO(res.content) as stream:
    try:
        data_arr = json.load(stream)
    except:
        data_arr = []

_, res = client.files_download(OPEN_PATH)
with io.BytesIO(res.content) as stream:
    try:
        open_arr = json.load(stream)
    except:
        open_arr = []

api = Flask(__name__)
CORS(api)


@api.route('/data-actual', methods=['GET'])
def get_data_actual():
    if not data_arr:
        return None
    return json.dumps(data_arr[-1])


@api.route('/open-actual', methods=['GET'])
def get_open_actual():
    if not open_arr:
        return None
    return json.dumps(open_arr[-1])


@api.route('/data-all', methods=['GET'])
def get_data_all():
    if not data_arr:
        return None
    return json.dumps(data_arr)


@api.route('/open-all', methods=['GET'])
def get_open_all():
    if not open_arr:
        return None
    return json.dumps(open_arr)


@api.route('/data-refresh_database', methods=['GET'])
def refresh_data():
    clnt = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    _, res = clnt.files_download(DATA_PATH)
    global data_arr
    with io.BytesIO(res.content) as stream:
        try:
            data_arr = json.load(stream)
        except:
            data_arr = []
    if not data_arr:
        return None
    return json.dumps(data_arr[-1])


@api.route('/open-refresh_database', methods=['GET'])
def refresh_open():
    clnt = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    _, res = clnt.files_download(OPEN_PATH)
    global open_arr
    with io.BytesIO(res.content) as stream:
        try:
            open_arr = json.load(stream)
        except:
            open_arr = []
    if not open_arr:
        return None
    return json.dumps(open_arr[-1])


@api.route('/data-post', methods=['PUT'])
def add_data():
    if request.method == "PUT":
        incoming = request.get_json()
        data_arr.append(incoming)
        send_data(data_arr,  F_P=DATA_PATH)
        return "OK"


@api.route('/open-post', methods=['PUT'])
def add_open():
    if request.method == "PUT":
        incoming = request.get_json()
        open_arr.append(incoming)
        send_data(open_arr, F_P=OPEN_PATH)
        return "OK"


def send_data(data, F_P='/log_data.json'):
    # Convert data to JSON string
    json_data = json.dumps(data)
    # Initialize Dropbox client
    clnt = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
    if get_files_from_folder('').__contains__(F_P[1:]):
        client.files_delete(F_P)
    else:
        print("No file {} found".format(F_P[1:]))
    # Upload the JSON data to Dropbox
    response = clnt.files_upload(json_data.encode('utf-8'), F_P)
    return True


def get_files_from_folder(folder_path=''):
    try:
        clnt = dropbox.Dropbox(app_key=APPKEY, app_secret=APPSECRET, oauth2_refresh_token=REF)
        # List files in the specified folder
        files = clnt.files_list_folder(folder_path).entries

        # Extract file names
        file_names = [file.name for file in files]
    except:
        file_names = []

    return file_names


if __name__ == '__main__':
    api.run()
