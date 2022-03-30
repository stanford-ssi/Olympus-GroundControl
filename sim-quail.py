

from argparse import ArgumentParser
import os.path

import json

import socket





class Sim:
    def __init__(self, filename):
        self.slate = None
        self.file =  open(filename):

    def run(self):
        for line in self.file:
            self.parse_line(line)

    def parse_line(self, line):

        json_object = json.loads(line)
        if "meta" in json_object:
            self.slate = json_object['meta']
        elif "update" in json_object:
            self.send_message(json_object)

    def __del__(self):
        self.file.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="simualtes a quail from a log file")
    parser.add_argument("-i", dest="filename", required=True, help="path to the log file")
    args = parser.parse_args()
    sim = Sim(args.filename)


