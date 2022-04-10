

from aiohttp import web
import aiohttp
import socketio
import asyncio
import random
import secrets

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
                    "value": 0,
                    "editable": False,
                    "pin": "PT1",
                },
                "ox_vent": {
                    "desc": "Oxidiser Vent",
                    "unit": "psi",
                    "value": 0,
                    "editable": False,
                    "pin": "PT2",
                },
            },
            "squibs": {
                "engine": {
                    "desc": "light this candle",
                    "unit": "bool",
                    "value": 0,
                    "editable": True,
                    "pin": "EM1",
                },
            },
            "valves": {
                "ox_fill": {
                    "desc": "testing",
                    "unit": "bool",
                    "value": 0,
                    "editable": False,
                    "pin": "SV1",
                },
                "ox_vent": {
                    "desc": "testing",
                    "unit": "bool",
                    "value": 0,
                    "editable": False,
                    "pin": "SV2",
                },
            },
            "health": {
                "v_bus": {
                    "desc": "Quail Voltage Bus",
                    "unit": "V",
                    "value": 0,
                    "editable": False,
                },
                "current": {
                    "desc": "Total quail current consumption",
                    "unit": "A",
                    "value": 0,
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

        self.authenticated_ids = []

        @self.sio.on('cmd')
        async def command(sid, data):
            print(self.authenticated_ids)
            if data.get("auth") not in self.authenticated_ids:
                print("not allow to execute")
                return

            print("executing command")
            print(data)

        @self.sio.on("connect")
        async def connect(sid, environ, auth):
            print("connected new client")

        @self.sio.on("de-auth")
        async def de_auth(sid, data):
            self.authenticated_ids.remove(data)
            print("deauthenticated", data)

        # WARNING: This isn't real security as socketio isn't encrypted
        # anyone snooping the connection can find out the super secret passcode
        # this more more to prevent someone accidentaly sending a stupid command 
        # in general the entire network is trusted and not internet conencted 
        @self.sio.on("try-auth")
        async def try_auth(sid, data):
            print("trying to authenticate", data)
            if data != "MAGIC":
                print("Bad pass!", data)
                return 

            new_id = secrets.token_urlsafe(32)
            print("authenticated", new_id)
            self.authenticated_ids.append(new_id)
            await self.sio.emit("auth", new_id)


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

        def update_random_walk(node, path):
            assert "value" in node
            assert "desc" in node
            if node["unit"] != "bool":
                node["value"] += random.random() - 0.5
            return node

        def get_value_only(node, path):
            return node["value"]

        while 1:
            await asyncio.sleep(0.1)
            self.metadata = self.transform_meta(update_random_walk)
            await self.sio.emit("new", self.transform_meta(get_value_only))


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