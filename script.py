import requests

from utils import find_dcm_files

def send_dicom(files: list):
    if type(files) != list:
        files = [files]

    url = 'http://localhost:8042/'

    # Testing connectivity
    r = requests.get(url + 'tools/now')
    assert r.status_code == 200

    for file in files:
        with open(file, 'rb') as f:
            dicom = f.read()
            r = requests.post(url + 'instances', data=dicom)
        print(r.status_code)


if __name__ == '__main__':
    files = find_dcm_files('data')
    send_dicom(files)