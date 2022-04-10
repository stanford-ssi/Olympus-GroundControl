
import json
from pathlib import Path

class DataBase:
    """ slow but good place holder for now"""

    def __init__(self, metadata, top):
        self.metadata = metadata
        self.top = top

        def get_id(node, path):
            return ".".join(path[1:])

        self.data = {id: [] for id in self.top.flat_meta(get_id)}

        # self.filename = filename

        # if Path(filename).is_file():
        #     self.local_data = self.load_data(filename)
        # else:
        #     self.local_data = []

        #possibly store data as json encoded - python doesn't need to look at it

        # self.file = open(filename, "a")

    # @staticmethod
    # def load_data(filename):
    #     data = []
    #     with open(filename, "r") as file:
    #         for line in file.readlines():
    #             data.append( json.loads(line) )

    #     return data

    # def __del__(self):
    #     self.file.close()

    def query(self, path, start, stop):
        path = path.split(".")
        assert path[0] == "slate"
        path.pop(0)

        return self.data[path][start:stop]

    def get_path(self, index, path):
        path = path.split(".")
        assert path[0] == "slate"
        path.pop(0)

        node = self.local_data[index]
        for name in path:
            try:
                node = node[name]
            except KeyError:
                return "null"

        return node

    def add_message(self, datapoint):
        self.local_data.append(datapoint)

    def add_multiple(self, datapoints):
        for datapoint in datapoints:
            self.local_data.append(datapoint)
            # self.file.write( json.dumps(datapoint) + '\n')

        # self.file.flush()