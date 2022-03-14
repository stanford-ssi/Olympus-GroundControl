

from aiohttp import web
import aiohttp
import socketio
import asyncio
import aiofiles
from aiofiles import os
import random

from ui_elements import Dashboard, Messages, Maps, Graphs, Configure

class Main:

    def __init__(self):
        self.app = web.Application()
        self.sio = socketio.AsyncServer(async_mode='aiohttp')
        self.sio.attach(self.app)

        self.create_pages()
        self.setup_routes()

        self.app.on_startup.append(self.start_background_tasks)
        self.app.on_cleanup.append(self.cleanup_background_tasks)


    def start(self):
        web.run_app(self.app, host="localhost", port=None)


    def create_pages(self):
        self.dashboard = Dashboard("test")
        self.messages = Messages("test")
        self.maps = Maps("test")
        self.graphs = Graphs("test")
        self.configure = Configure("test")
        # self.messages = Dashboard("test")

    async def get_dashboard(self, request):
        return web.Response(text=self.dashboard.render(), content_type='text/html')

    async def get_messages(self, request):
        return web.Response(text=self.messages.render(), content_type='text/html')

    async def get_maps(self, request):
        return web.Response(text=self.maps.render(), content_type='text/html')

    async def get_graphs(self, request):
        return web.Response(text=self.graphs.render(), content_type='text/html')

    async def get_configure(self, request):
        return web.Response(text=self.configure.render(), content_type='text/html')

    async def get_mapdata(self, request):
        url = request.match_info['url']
        filename = 'cache/' + url.replace('/', "!slash!") + '.png'

        mapbox_api = 'https://api.mapbox.com/{url}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'

        if await os.path.isfile(filename):
            async with aiofiles.open(filename, 'br') as file:
                data = await file.read()
        else:
            async with self.mapdata_session.get(mapbox_api.format(url = url)) as resp: 
                data = await resp.read() 
            async with aiofiles.open(filename, 'bw') as file:
                await file.write(data)

        #TODO support jpegs also
        return web.Response(body=data, content_type='image/png')

    def setup_routes(self):
        self.app.router.add_get('/', self.get_dashboard)
        self.app.router.add_get('/dashboard', self.get_dashboard)
        self.app.router.add_get('/messages', self.get_messages)
        self.app.router.add_get('/maps', self.get_maps)
        self.app.router.add_get('/graphs', self.get_graphs)
        self.app.router.add_get('/configure', self.get_configure)
        self.app.router.add_get('/mapdata/{url:.*}', self.get_mapdata)
        self.app.router.add_static('/static/', './static/')


    async def push_serial_data(self):
        while 1:
            await asyncio.sleep(1)
            await self.sio.emit("new", {"magic": [1,2,3], "rand": random.random() })

    async def start_background_tasks(self, app):
        self.app.serial_pub = asyncio.create_task(self.push_serial_data())

        self.mapdata_session = aiohttp.ClientSession()
        await os.makedirs('cache/', exist_ok=True)

    async def cleanup_background_tasks(self, app):
        self.app.serial_pub.cancel()
        await self.app.serial_pub


# @sio.on('data_request')
# def data_request(sid, data):
#     # send back data
#     pass

if __name__ == "__main__":
    page = Main()
    page.start()