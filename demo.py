

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

from SnorkelClient import SnorkelClient

from time import time

from pages import Dashboard, Slate, Maps, Graphs, Configure, Sequencing, FillPage, LaunchPage, Mass_Graph, Ox_Graph, Fuel_Graph
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

        self.TCP_TIMEOUT = 2.0
        self.tx_queue = asyncio.Queue()

        self.tcp_quail_reader = None
        self.tcp_quail_writer = None

        self.history = {}
        self.metaslate = {}

    def start(self):
        web.run_app(self.app, port=8080)

    def create_pages(self):
        # Don't forget to add your page the the sidebar
        # in templates/main.template.html

        self.dashboard = Dashboard("Dashboard", self)
        self.sequencing = Sequencing("Sequencing", self)
        self.fillpage = FillPage("FillPage", self)
        self.launchpage = LaunchPage("LaunchPage", self)
        self.messages = Slate("test", self)
        self.maps = Maps("test", self)
        self.graphs = Graphs("test", self)
        self.configure = Configure("test", self)

        self.mass_graph = Mass_Graph("test", self)
        self.ox_graph = Ox_Graph("test", self)
        self.fuel_graph = Fuel_Graph("test", self)

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

            self.tx_queue.put_nowait(to_send)

        @self.sio.on("get-data")
        async def get_data(sid, data):
            last_n = int(data["last_n"])
            out = {}
            for id in data["ids"]:
                try:
                    line = self.history[id][-last_n:]
                except Exception:
                    line = []

                if len(line) < last_n:
                    line = [None] * (last_n - len(line)) + line

                out[id] = line
            await self.sio.emit("deliver-data", out, room=sid)

        @self.sio.on("de-auth")
        async def de_auth(sid, data):
            self.authenticated_ids.remove(data)
            async with aiofiles.open('authenticated_cookies.json', mode='w') as f:
                await f.write(json.dumps(self.authenticated_ids))
            print("deauthenticated", data)

        # Requests an update of the metaslate
        @self.sio.on("get-meta")
        async def request_meta(sid, data):
            await self.deliver_metaslate()

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
            self.start_database()

    async def deliver_metaslate(self):
        self.metaslate = {}
        nodes = {"quail": self.quail}  # this is a bodge

        for node_key, node in nodes.items():
            self.metaslate[node_key] = {}
            for slate_key, slate in node.slates.items():
                self.metaslate[node_key][slate_key] = slate.metaslate

        # actually delivers to all clients
        await self.sio.emit("deliver-metaslate", self.metaslate)

    def get_meta(self, path, endpoint=None):
        return 1

    def flat_meta(self, function, node=None, path=None):
        return []

    # TODO overhaul this
    async def start_database(self):
        metadata = self.quail.slates['telemetry'].metaslate['channels']
        self.database = DataBase(metadata, self, "init")
        await self.database.add_log_line("meta", metadata)

    async def rx_task(self):
        # This is hacky but it works for now
        while (True):
            slate = await self.quail.slates['telemetry'].recv_slate()
            node = 'quail'
            slate_key = 'telemetry'

            await self.database.add_log_line("update", slate)

            for key, value in slate.items():
                key = f"{node}.{slate_key}.{key}"
                if key not in self.history:
                    self.history[key] = []
                self.history[key].append(value)
                while len(self.history[key]) > 10000:
                    self.history[key].pop()

            slate = {'quail': {'telemetry': slate}}
            await self.sio.emit("new", slate)

    async def send_heartbeat(self):
        while (True):
            await asyncio.sleep(60)
            to_send = {"cmd": "heart"}
            self.tx_queue.put_nowait(to_send)

    async def start_background_tasks(self, app):
        self.quail = SnorkelClient('192.168.2.2', 1002)
        self.quail.connect()

        await self.quail.slates['telemetry'].connect()

        await self.start_database()
        await self.deliver_metaslate()

        self.app.rx_task = asyncio.create_task(self.rx_task())
        # self.app.heartbeat_task = asyncio.create_task(self.send_heartbeat())
        # self.app.tx_task = asyncio.create_task(self.tx_task())

    async def cleanup_background_tasks(self, app):
        self.app.rx_task.cancel()
        await self.app.rx_task
        # self.app.udp_task.cancel()
        # self.app.heartbeat_task.cancel()
        # self.app.tcp_sender_task.cancel()
        # await self.app.udp_task
        # await self.app.heartbeat_task
        # await self.app.tcp_sender_task
        pass


def get_app():
    page = Main()
    return page.app
    # page.start()


if __name__ == "__main__":
    page = Main()
    page.start()
