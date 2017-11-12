#! /usr/bin/python3
# coding=utf-8
"""
Demo Script dbx_decrypt represents a local agent that is installed on trusted client machine.
The client is getting a shared public link to an encrypted file from DropBox
Client retrieves a metadata of the encrypted file from html container
Gets keys from a Key Service (Policy Server is bypassed to speed up the demo) - both users are accessing same Key Server
Client decrypts the file with key and display it to the user
"""
import os
import requests
from pathlib import Path
from ingestion.ingestion_apis.encryption_api import EncryptionApi
from ingestion.ingestion_apis.container_api import ContainerApi

from magen_rest_apis.rest_client_apis import RestClientApis


KEY_BY_ASSET_ID_URL = 'http://{0}:5010/magen/ks/v3/asset_keys/assets/asset/{1}/'
IN_ASSET_BY_ASSET_ID = 'http://{0}:5020/magen/ingestion/v1/assets/asset/{1}/'

home_dir = str(Path.home())
LOCAL_DIR = os.path.join(home_dir, "magen_data", "ingestion/")


def retrieve_meta_data(f_path: str):
    with open(f_path, 'rb') as encrypted_file:
        meta_data = ContainerApi.extract_meta_from_container(encrypted_file)
    return meta_data


def decrypt_file(file_path, server_ip='localhost'):
    meta_data = retrieve_meta_data(file_path)
    meta_data_dict = meta_data[0]
    file_size = meta_data[1]

    asset_id = meta_data_dict['asset_id']

    resp = requests.get(KEY_BY_ASSET_ID_URL.format(server_ip, asset_id), headers=RestClientApis.get_json_headers)
    key = resp.json()['response']['key']['key']

    enc_b64_file = ContainerApi.create_encrypted_file_from_container(file_path, file_size, data_dir=LOCAL_DIR)

    decrypted = EncryptionApi.decrypt_file_v2(key, enc_b64_file, meta_data_dict)
    print("Decrypted file is: ", decrypted)


def get_filename(f_path, server_ip='localhost'):
    meta_data_dict = retrieve_meta_data(f_path)[0]
    asset_id = meta_data_dict['asset_id']
    resp = requests.get(IN_ASSET_BY_ASSET_ID.format(server_ip, asset_id), headers=RestClientApis.get_json_headers)
    return resp.json()['response']['asset'][0]['file_name']
