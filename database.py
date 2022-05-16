
import json
# from pathlib import Path
import datetime

import aiofiles
import os

class DataBase:
    """ slow but good place holder for now"""

    def __init__(self, metadata, top, filename):
        return #currently disabled because loging isn't priority

        # self.metadata = metadata
        self.top = top

        # self.history = {key: [] for key in  self.top.flat_meta( lambda node, path: ".".join(path) ) }

        # def get_id(node, path):
        #     return ".".join(path[1:])

        # self.data = {id: [] for id in self.top.flat_meta(get_id)}

        self.filename = "../logs/" + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M_') + filename + ".log"
        print("making new log file", self.filename)

        os.makedirs("../logs", exist_ok=True)

        #possibly store data as json encoded - python doesn't need to look at it

        # self.file = open(filename, "a")

    async def add_log_line(self, name, obj):
        return
        async with aiofiles.open(self.filename, mode='a') as f:
            await f.write(json.dumps({name: obj})) 

    # @staticmethod
    # def load_data(filename):
    #     data = []
    #     with open(filename, "r") as file:
    #         for line in file.readlines():
    #             data.append( json.loads(line) )

    #     return data

    # def __del__(self):
    #     self.file.close()

    # def last_n(self, ids, last_n):
    #     out = {}
    #     for id in data["ids"]:
    #         out[id] = self.history["slate." + id][-last_n:]
    #     return out

    # def query(self, path, start, stop):
    #     path = path.split(".")
    #     assert path[0] == "slate"
    #     path.pop(0)

    #     return self.data[path][start:stop]

    # def get_path(self, index, path):
    #     path = path.split(".")
    #     assert path[0] == "slate"
    #     path.pop(0)

    #     node = self.local_data[index]
    #     for name in path:
    #         try:
    #             node = node[name]
    #         except KeyError:
    #             return "null"

    #     return node

    # def add_message(self, datapoint):
    #     self.local_data.append(datapoint)

    # def add_multiple(self, datapoints):
    #     for datapoint in datapoints:
    #         self.local_data.append(datapoint)
    #         # self.file.write( json.dumps(datapoint) + '\n')

        # self.file.flush()