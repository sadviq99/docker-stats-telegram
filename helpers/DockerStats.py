import re
import glob

import pandas as pd

from helpers.shared import ROOT_PATH, join_path


class DockerStats:
    """Gets all of the statistic callculation by querying the CSV files"""
    __header_list = ['DATE', 'IP', 'CPU COUNT', 'NAME', 'CPU %', 'MEM %', 'NET IO']
    __size_suffixes = ['MB', 'GB', 'TB']

    def __init__(self, data_path):
        self.df = pd.concat(map(lambda f: pd.read_csv(f, delimiter=';', names=DockerStats.__header_list), glob.glob(join_path(ROOT_PATH, data_path))))
        self.df['CPU %'] = self.df['CPU %'].apply(self.__percentage_to_float())
        self.df['MEM %'] = self.df['MEM %'].apply(self.__percentage_to_float())
        self.df[['NET INPUT', 'NET OUTPUT']] = self.df['NET IO'].str.split(' / ', expand=True)
        self.df['NET INPUT'] = self.df['NET INPUT'].apply(lambda x: self.__to_float_mb(x))
        self.df['NET OUTPUT'] = self.df['NET OUTPUT'].apply(lambda x: self.__to_float_mb(x))
        self.df.drop(['NET IO'], inplace=True, axis=1)
        self.df['DATE'] = pd.to_datetime(self.df['DATE'])

    def champions(self):
        """Returns the IP which generated the most of the traffic"""
        return self.df[self.df['NET OUTPUT'] == self.df['NET OUTPUT'].max()]['IP'].unique()

    def traffic_max(self, ip=''):
        """Returns the amount of traffic generated in total or per specific IP"""
        if ip:
            return self.__to_human_size(self.df.loc[self.df['IP'] == ip, 'NET OUTPUT'].max())
        return self.__to_human_size(self.df.groupby(['IP'])['NET OUTPUT'].max().sum()) 

    def duration(self, ip=''):
        """Returns the duration of the longest attack or per specific IP. It substracts
        the last timestamp value from the first one for the particular IP"""
        if ip:
            return self.df.loc[self.df['IP'] == ip, 'DATE'].iloc[-1] - self.df.loc[self.df['IP'] == ip, 'DATE'][1]
        
        dur_list = []
        for ip in self.df['IP'].unique():
            dur_list.append(self.df.loc[self.df['IP'] == ip, 'DATE'].iloc[-1] - self.df.loc[self.df['IP'] == ip, 'DATE'][1])
            continue
        return pd.DataFrame(dur_list).max()[0]

    def cpu_avg(self, ip):
        """Returns the average CPU load per IP"""
        return round(self.df.loc[self.df['IP'] == ip, 'CPU %'].mean()/self.df.loc[self.df['IP'] == ip, 'CPU COUNT'].iloc[0], 2)

    def memory_avg(self, ip):
        """Returns the average Memory load per IP"""
        return round(self.df.loc[self.df['IP'] == ip, 'MEM %'].mean(), 2)

    @staticmethod
    def __percentage_to_float():
        """Converts percentage to float so it will be possible to aggregate 
        and process the data"""
        return lambda x: float((x.replace('%', '')))

    @staticmethod
    def __to_float_mb(value):
        """Converts different data sized to MB to simplify calcullations"""
        multi = 1.0
        value = str(value).upper()
        if 'T' in value:
            multi = 1048576 
        elif 'G' in value:
            multi = 1024.0
        elif 'K' in value:
            multi = 0.001024
        return multi * float(''.join(re.findall('[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+', value)))
    
    @staticmethod
    def __to_human_size(value):
        """Converts MB to human readable data sizes"""
        i = 0
        while value >= 1024 and i < len(DockerStats.__size_suffixes)-1:
            value /= 1024.
            i += 1
        f = ('%.2f' % value).rstrip('0').rstrip('.')
        return '%s %s' % (f, DockerStats.__size_suffixes[i])
    