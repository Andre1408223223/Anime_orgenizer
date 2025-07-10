import requests
from config import qb_url, qb_user, qb_paswd
import paramiko
import os

def list_remote_files(path, host="100.100.22.66", username="andre", password='Andrerob32'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname=host, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command(f"ls {path}")

    files = stdout.read().decode()
    ssh.close()
    return(files)

session = requests.Session()

login_url = f"{qb_url}/api/v2/auth/login"
login_data = {
    'username': qb_user,
    'password': qb_paswd
}
session.post(login_url, data=login_data)

def add_torrent(torrent): 
 with open(torrent, 'rb') as torrent_file:
     files = {'torrents': torrent_file}
     data = {'category': 'tv-shows'}
 
     response = session.post(f"{qb_url}/api/v2/torrents/add", files=files, data=data)
 
 print("Torrent file added:", response.status_code)

def list_all_files():
    info_url = f"{qb_url}/api/v2/torrents/info"
    response = session.get(info_url)
    torrents = response.json()

    for torrent in torrents:
       category = torrent['category']
       name = torrent['name']
       content_path = torrent['content_path']

       files = list_remote_files(path=content_path)
       
       # chek if files is empty
       if files == "":
          temp_path = torrent['download_path']

          folder = list_remote_files(path=temp_path)

          files = list_remote_files(path=os.path.join(temp_path, folder))


list_all_files()

# add_torrent("test.torrent")