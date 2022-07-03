import os
import csv
import tempfile

from pssh.clients import ParallelSSHClient
from pssh.config import HostConfig
from gevent import joinall

from helpers.shared import join_path


class ServersConnection:
    """Establish parallel SSH connection and download files from 
    remote servers over SCP protocol"""

    def __init__(self, data_path):
        self.servers = []
        with open(data_path, 'r') as file:
            for row in csv.DictReader(file):
                self.servers.append(row)

        self.client = ParallelSSHClient(self.servers)
    
    def download_stats(self):
        """Downloads files from the remote server in parallel over SCP"""

        tmp_dir = tempfile.TemporaryDirectory().name

        hosts = self.hosts()
        host_configs = self.host_configs()

        # This is the right place to twick retry options.
        client = ParallelSSHClient(hosts, 
                                   host_config=host_configs, 
                                   num_retries=0, 
                                   retry_delay=0)

        # It will download files to the temp directory and 
        # save them in format "dockerstats.csv_<ip>".
        cmds = client.copy_remote_file(
            '/tmp/dockerstats.csv',
            join_path(tmp_dir, 'dockerstats.csv'))

        # The raise_error parameter needs to be set to False,
        # otherwise it will exit on the first failure.
        joinall(cmds, raise_error=False)

        # Since it's hard to extract failed connections from pssh & gevent 
        # implementation, we just compare amount of files downloaded with 
        # the number of servers overall. If files in the source dir don't 
        # exist, it also will be reported as failed connection.
        if os.path.isdir(tmp_dir):
            succeed_servers = [ csv.split('_')[-1] for csv in os.listdir(tmp_dir) ]
            failed_servers = [ host for host in hosts if host not in succeed_servers ]
        else:
            failed_servers = hosts
        
        return tmp_dir, failed_servers

    def hosts(self):
        """Extract servers IP values from DictReader object and 
        returns the list"""
        return [ server['ip'] for server in self.servers ]

    def host_configs(self):
        """Defines individual connection config for each host"""
        host_config = []

        # This is the right place to twick timeout value.
        for server in self.servers:
            host_config.append(HostConfig(
                user=server['username'],
                password=server['password'],
                timeout=5
            ))
        return host_config
