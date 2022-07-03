import csv
import tempfile

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from helpers.shared import ROOT_PATH, logger, join_path


class ServersConnection:
    def __init__(self, data_path):
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.servers = []

        with open(data_path, 'r') as file:
            for row in csv.DictReader(file):
                self.servers.append(row)
    
    def download_stats(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

        failed_servers = []
        for server in self.servers:
            try:
                self.connect(
                    server['ip'],
                    server['username'],
                    server['password'])
            except Exception as err:
                logger.error('Unable to connect to %s: %s' % (server['ip'], err))
                failed_servers.append(server['ip'])
                continue

            try:
                self.scp(
                    '/tmp/dockerstats.csv', 
                    join_path(self.tmp_dir.name, '%s.csv' % server['ip']))
            except Exception as err:
                logger.error('Unable to copy from %s: %s' % (server['ip'], err))
                failed_servers.append(server['ip'])
                continue
        
        return self.tmp_dir.name, failed_servers

    def connect(self, ip, username, password):
        self.ssh.connect(
            hostname=ip,
            username=username,
            password=password,
            timeout=5
        )

    def scp(self, remote_path, local_path):
        scp = SCPClient(self.ssh.get_transport())
        scp.get(remote_path, local_path)
        scp.close()
