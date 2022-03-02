
import json
from pathlib import Path

class DataBase:
    """ slow but good place holder for now"""

    def __init__(self, filename):
        if Path(filename).is_file():
            self.local_data = self.load_data(filename)
        else:
            self.local_data = []

        #possibly store data as json encoded - python doesn't need to look at it

        self.file = open(filename, "a")

    @staticmethod
    def load_data(filename):
        data = []
        with open(filename, "r") as file:
            for line in file.readlines():
                data.append( json.loads(line) )

        return data

    def __del__(self):
        self.file.close()

    def query(self, idx):
        return [self.local_data[index] for index in idx]

    def add(self, datapoints):
        for datapoint in datapoints:
            self.local_data.append(datapoint)
            self.file.write( json.dumps(datapoint) + '\n')

        self.file.flush()