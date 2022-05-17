

from aiohttp import web
import aiohttp
import socketio
import asyncio
import random
import secrets

import aiofiles
from aiofiles import os
import asyncudp
import json

from time import time

from ui_elements import Dashboard, Slate, Maps, Graphs, Configure
from database import DataBase

class Main:

    def __init__(self):
        self.app = web.Application()
        self.sio = socketio.AsyncServer(async_mode='aiohttp')
        self.sio.attach(self.app)

        self.create_pages()
        self.create_socketio_handlers()

        self.app.router.add_static('/static/', './static/')

        self.app.on_startup.append(self.start_background_tasks)
        self.app.on_cleanup.append(self.cleanup_background_tasks)
         

    def start(self):
        web.run_app(self.app, host="localhost", port=8080)

    def create_pages(self):
        # Don't forget to add your page the the sidebar!
        self.dashboard = Dashboard("Dashboard", self)
        self.messages = Slate("test", self)
        self.maps = Maps("test", self)
        self.graphs = Graphs("test", self)
        self.configure = Configure("test", self)

    def create_socketio_handlers(self):

        try:
            with open('authenticated_cookies.json', mode='r') as f:
                self.authenticated_ids = json.loads(f.read())
        except FileNotFoundError:
            self.authenticated_ids = []
            with open('authenticated_cookies.json', mode='w') as f:
                f.write(json.dumps(self.authenticated_ids))

        @self.sio.on('cmd')
        async def command(sid, data):
            # bad bad bad but temp
            async with aiofiles.open('authenticated_cookies.json', mode='r') as f:
                contents = await f.read()
            self.authenticated_ids = json.loads(contents)

            print(self.authenticated_ids)
            if data.get("auth") not in self.authenticated_ids:
                print("not allow to execute")
                await self.sio.emit("bad-auth", room=sid)
                return
            del data["auth"]

            await self.database.add_log_line("cmd", data)

            if "cmd" in data:
                to_send = {"cmd": self.unflatten_command(data['cmd'])}
                print("executing command", data['cmd'])
            elif "reboot" in data:
                to_send = {"reboot": None}
                print("rebooting quail")
            else:
                raise ValueError("unknown command" + str(data))

            try:
                self.tcp_quail_writer.write(json.dumps(to_send).encode())
                await asyncio.wait_for(self.tcp_quail_writer.drain(), timeout=2.0)
                echo_cmd = await asyncio.wait_for(self.tcp_quail_reader.readline(), timeout=2.0)
                print("echoed command", echo_cmd)
            except (ConnectionResetError, asyncio.TimeoutError):
                print("command timed out reconnecting")
                await self.connect_quail()


        @self.sio.on("get-data")
        async def get_data(sid, data):
            last_n = int(data["last_n"])

            # print(self.history)
            # print(data)
            out = {}
            for id in data["ids"]:
                out[id] = self.history[id][-last_n:]

            # print("getting data")
            # print(out)
            await self.sio.emit("deliver-data", out, room=sid)

        @self.sio.on("de-auth")
        async def de_auth(sid, data):
            self.authenticated_ids.remove(data)

            async with aiofiles.open('authenticated_cookies.json', mode='w') as f:
                await f.write(json.dumps(self.authenticated_ids))

            print("deauthenticated", data)

        # WARNING: This isn't real security as socketio isn't encrypted
        # anyone snooping the connection can find out the super secret passcode
        # this more more to prevent someone accidentaly sending a stupid command 
        # in general the entire network is trusted and not internet conencted 
        @self.sio.on("try-auth")
        async def try_auth(sid, data):
            if data != "MAGIC":
                await self.sio.emit("bad-auth", room=sid)
                return 

            new_id = secrets.token_urlsafe(32)
            print("authenticated", new_id)
            self.authenticated_ids.append(new_id)

            async with aiofiles.open('authenticated_cookies.json', mode='w') as f:
                await f.write(json.dumps(self.authenticated_ids))

            await self.sio.emit("auth", new_id, room=sid)

        @self.sio.on("new_log")
        async def new_log(sid, filename):
            self.database = DataBase(self.metadata, self, filename)
            await self.database.add_log_line("meta", self.metadata)

    def get_meta(self, path, endpoint=None):
        path = path.split(".")
        assert path[0] == "slate"
        path.pop(0)

        if endpoint:
            path.extend(endpoint.split("."))

        node = self.metadata
        for name in path:
            try:
                node = node[name]
            except KeyError:
                print("Not found key", name, "in", path)
                return "null"

        return node

    def flat_meta(self, function, node=None, path=None):
        if node is None:
            node = self.metadata
            path = ["slate"]

        if "valu" in node.keys():
            return [ function(node, path) ]

        if type(node) == dict:
            list_of_lists = [ self.flat_meta(function, node[key], path + [key] ) for key in node.keys() ]
            return [item for sublist in list_of_lists for item in sublist]

        return []

    def transform_meta(self, function, node=None, path=None):
        if node is None:
            node = self.metadata
            path = ["slate"]

        if type(node) == dict:
            if "valu" in node.keys() or "desc" in node.keys():
                return function(node, path)
            return {key: self.transform_meta(function, node[key], path + [key] ) for key in node.keys()}
        else:
            print(type(node), node, path)
            assert False
    
    def update_meta(self, update, node=None):
        if node is None:
            node = self.metadata

        if "valu" in node.keys():
            # TODO enforce types
            node["valu"] = update

        elif type(node) == dict:
            for key in node.keys():
                if key in update:
                    self.update_meta(update[key], node = node[key])
                else:
                    print("missing slate key in update", key)
        else:
            print(node, update)
            assert False

    def unflatten_command(self, flat):
        out = {}
        for path in flat.keys():
            ids = path.split(".")
            if ids[0] == "slate":
                ids.pop(0)
            node = out
            for id in ids[:-1]:
                node = node.setdefault(id, {})
            node[ids[-1]] = flat[path]
        return out

    async def push_serial_data(self):

        while(True):
            message, addr = await self.udp_socket.recvfrom()
            json_object = json.loads(message)

            # print(message)
            # print()
            
            self.update_meta(json_object)
            await self.database.add_log_line("update", json_object)

            for key, value in self.flat_meta( lambda node, path: (".".join(path), node["valu"]) ):
                self.history[key].append(value)

            while len(self.history[key]) > 10000:
                self.history[key].pop()

            await self.sio.emit("new", json_object)


    async def connect_quail(self):
        TCP_IP = "192.168.1.100"
        TCP_PORT = 1002

        while True:
            try:
                print("waiting for quail to connect")
                self.tcp_quail_reader, self.tcp_quail_writer = await asyncio.open_connection(TCP_IP, TCP_PORT)
                print("connected to quail")
                await self.get_metaslate_from_quail()
                print("fetched metaslate")
            except (ConnectionResetError, ConnectionRefusedError):
                print("Connection error")
                await asyncio.sleep(2)
            else:
                return
            

    async def get_metaslate_from_quail(self):

        while 1:
            print("Requested metaslate")
            self.tcp_quail_writer.write(json.dumps({ "meta" : "gimme" }).encode())
            await self.tcp_quail_writer.drain()

            message = await self.tcp_quail_reader.readline() 
            try:
                a = json.loads(message)
            except ValueError:
                pass
            else:
                self.metadata = a
                break

        def add_valu(node, path):
            node["valu"] = 0
            return node

        self.metadata = self.transform_meta(add_valu)

        print(self.metadata)
        print("Got metaslate!")

        self.database = DataBase(self.metadata, self, "init")
        await self.database.add_log_line("meta", self.metadata)

        self.history = {key: [] for key in  self.flat_meta( lambda node, path: ".".join(path) ) }


    async def start_background_tasks(self, app):

        await self.connect_quail()
            

        self.udp_socket = await asyncudp.create_socket(local_addr=("0.0.0.0", 8000))
        self.app.serial_pub = asyncio.create_task(self.push_serial_data())

        #TODO move inside Map Page class
        self.mapdata_session = aiohttp.ClientSession()
        await os.makedirs('cache/', exist_ok=True)

    async def cleanup_background_tasks(self, app):
        self.app.serial_pub.cancel()
        await self.app.serial_pub



def get_app():
    page = Main()
    return page.app
    # page.start()

if __name__ == "__main__":
    page = Main()
    page.start()