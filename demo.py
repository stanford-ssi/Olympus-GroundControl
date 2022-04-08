

from aiohttp import web
import aiohttp
import socketio
import asyncio
import random

import aiofiles
from aiofiles import os

from ui_elements import Dashboard, Messages, Maps, Graphs, Configure

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

        self.metadata = {
            "press": {
                "ox_fill": {
                    "desc": "Oxidiser Fill",
                    "unit": "psi",
                    "value": None,
                    "editable": False,
                    "pin": "PT1",
                },
                "ox_vent": {
                    "desc": "Oxidiser Vent",
                    "unit": "psi",
                    "value": None,
                    "editable": False,
                    "pin": "PT2",
                },
            },
            "valves": {
                "ox_fill": {
                    "desc": "testing",
                    "unit": "bool",
                    "value": None,
                    "editable": False,
                    "pin": "SV1",
                },
                "ox_vent": {
                    "desc": "testing",
                    "unit": "bool",
                    "value": None,
                    "editable": False,
                    "pin": "SV2",
                },
            },
            "health": {
                "v_bus": {
                    "desc": "Quail Voltage Bus",
                    "unit": "V",
                    "value": None,
                    "editable": False,
                },
                "current": {
                    "desc": "Total quail current consumption",
                    "unit": "A",
                    "value": None,
                    "editable": False,
                }
            }
        }

    def get_meta(self, path, endpoint=None):
        path = path.split(".")
        assert path[0] == "slate"
        path.pop(0)

        if endpoint:
            path.append(endpoint)
        print(path)

        node = self.metadata
        for name in path:
            try:
                node = node[name]
            except KeyError:
                return "null"

        print(node)
        return node

    def start(self):
        web.run_app(self.app, host="localhost", port=8080)

    def create_pages(self):
        self.dashboard = Dashboard("Dashboard", self)
        self.messages = Messages("test", self)
        self.maps = Maps("test", self)
        self.graphs = Graphs("test", self)
        self.configure = Configure("test", self)

    def create_socketio_handlers(self):

        self.command_sids = []
        @self.sio.on('cmd')
        async def command(sid, data):
            print(data)

        @self.sio.event
        async def connect(sid, environ, auth):
            print("connected new client")
            if sid in self.command_sids:
                await self.sio.emit("auth")

        @self.sio.on("try-auth")
        async def try_auth(sid, data):
            print("got message", data)
            if sid in self.command_sids:
                await self.sio.emit("auth")
            if data == "MAGIC":
                print("authenticated")
                self.command_sids.append(sid)
                await self.sio.emit("auth")


    def meta_endpoints(self, node=None):
        if node is None:
            node = self.metadata

        if "value" in node.keys():
            yield node

        for key in node.keys():
            if node[key] is dict:
                yield from self.meta_endpoints(node)

    def transform_meta(self, function, node=None, path=None):
        if node is None:
            node = self.metadata
            path = ["slate"]

        if "value" in node.keys():
            return function(node, path)

        if type(node) == dict:
            return {key: self.transform_meta(function, node[key], path + [key] ) for key in node.keys()}
    

    async def push_serial_data(self):

        def get_random_value(node, path):
            assert "value" in node
            assert "desc" in node
            return random.random()
        while 1:
            await asyncio.sleep(0.01)
            new_slate = self.transform_meta(get_random_value)
            await self.sio.emit("new", new_slate)


    async def start_background_tasks(self, app):
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