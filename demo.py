

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

        self.metadata = { "press": { "ox_fill": { "desc": "Oxidiser Fill", "units": "psi", "value": None, "editable": False, "pin": "PT1", }, "ox_vent": { "desc": "Oxidiser Vent", "units": "psi", "value": None, "editable": False, "pin": "PT2", }, }, "health": { "v_bus":{ "desc": "Quail Voltage Bus", "units": "V", "value": None, "editable": False, }, "current":{ "desc": "Total quail current consumption", "units": "A", "value": None, "editable": False, } } }

    def get_meta(self, path, endpoint=None):
        path = path.split(".")
        assert path[0] == "slate"
        path.pop(0)

        if endpoint:
            path.append(endpoint)

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
        @self.sio.on('command')
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

    async def push_serial_data(self):
        i = 0;
        while 1:
            await asyncio.sleep(1)
            i = (i +1)%100
            await self.sio.emit("new", {"magic": [1,2,3],
                                        "press" : {"ox_fill": {"value": random.random()}, "ox_vent": {"value": random.random()}},
                                        "rand": random.random(),
                                        "TC1": 70 + 5*random.random(),
                                        "TC0": i,
                                        "health": {"v": {
                                            "value": random.random(),
                                            "desc": "Bus Voltage",
                                        }}})


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