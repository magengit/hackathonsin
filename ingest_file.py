import json
import os
from pathlib import Path

import requests
from magen_rest_apis.magen_app import MagenApp
from magen_rest_apis.rest_client_apis import RestClientApis
from magen_rest_apis.server_urls import ServerUrls

from hackathon_globals import HackathonGlobals

src_ver = MagenApp.app_source_version(__name__)
if src_ver:
    # noinspection PyUnresolvedReferences
    import dev.magen_env

SIN_MAGEN_INGESTION_POST_WITH_EMPTY_DOWNLOAD_URL = """
{
    "asset": [
        {
            "name": "finance doc",
            "resource_group": "roadmap",
            "resource_id": 3,
            "client_uuid": "<client_id>",
            "host": "sjc-repenno-nitro10.cisco.com",
            "download_url": ""
        }
    ]
}
"""

home_dir = str(Path.home())
hackathon_data_dir = os.path.join(home_dir, "magen_data", "hackathon")
if not os.path.exists(hackathon_data_dir):
    os.makedirs(hackathon_data_dir)
server_urls_instance = ServerUrls().get_instance()
hackaton_globals = HackathonGlobals()
hackaton_globals.data_dir = hackathon_data_dir
file_name = "test_up.txt"
src_file_full_path = os.path.join(hackaton_globals.data_dir, file_name)
magen_file = open(src_file_full_path, 'w+')
magen_file.write("this is a test")
magen_file.close()
post_json = json.loads(SIN_MAGEN_INGESTION_POST_WITH_EMPTY_DOWNLOAD_URL)
post_json["asset"][0]["download_url"] = "file://" + src_file_full_path
post_resp_obj = RestClientApis.http_post_and_check_success(server_urls_instance.ingestion_server_asset_url,
                                    json.dumps(post_json))
post_resp_json_obj = post_resp_obj.json_body
container_file_path = post_resp_json_obj["response"]["asset"]["file_path"] + ".html"
container_file_name = file_name + ".html"

url = "https://content.dropboxapi.com/2/files/upload"
dropbox_api_arg = '{{\"path\":\"{}\"}}'.format(container_file_name)

headers = {
    "Authorization": "Bearer ddTxTjifXhYAAAAAAAAXo8nJQMUdDtfYAx7QH4enaaf4OED97uskv5-BSmOUz0Lu",
    "Content-Type": "application/octet-stream",
    "Dropbox-API-Arg": "{\"path\":\"/test_up_2.txt.html\",\"mode\": \"overwrite\"}"
}

data = open(container_file_path, "rb").read()
r_upload = requests.post(url, headers=headers, data=data)

url = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"

headers = {
    "Authorization": "Bearer ddTxTjifXhYAAAAAAAAXo8nJQMUdDtfYAx7QH4enaaf4OED97uskv5-BSmOUz0Lu",
    "Content-Type": "application/json"
}

data = {
    "path": "/test_up_2.txt.html",
    "settings": {}
}

r_create_link = requests.post(url, headers=headers, data=json.dumps(data))
if not r_create_link.ok:
    url = "https://api.dropboxapi.com/2/sharing/get_shared_links"

    headers = {
        "Authorization": "Bearer ddTxTjifXhYAAAAAAAAXo8nJQMUdDtfYAx7QH4enaaf4OED97uskv5-BSmOUz0Lu",
        "Content-Type": "application/json"
    }

    data = {
        "path": "/test_up_2.txt.html"
    }

    r_create_link = requests.post(url, headers=headers, data=json.dumps(data))
    create_link_json = r_create_link.json()
    create_link_url = create_link_json["links"][0]["url"]
else:
    create_link_json = r_create_link.json()
    create_link_url = create_link_json["url"]

print(create_link_url)
