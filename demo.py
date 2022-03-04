

from aiohttp import web
import socketio
import asyncio

from ui_elements import Dashboard, Messages, Maps

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
        # self.messages = Dashboard("test")

    async def get_dashboard(self, request):
        return web.Response(text=self.dashboard.render(), content_type='text/html')

    async def get_messages(self, request):
        return web.Response(text=self.messages.render(), content_type='text/html')

    async def get_maps(self, request):
        return web.Response(text=self.maps.render(), content_type='text/html')

    async def get_style(self, request):
        return web.FileResponse('./static/style.css')

    async def get_normalize(self, request):
        return web.FileResponse('./static/normalize.min.css')

    async def get_socketio(self, request):
        return web.FileResponse('./static/socket.io.min.js')

    def setup_routes(self):
        self.app.router.add_get('/', self.get_dashboard)
        self.app.router.add_get('/dashboard', self.get_dashboard)
        self.app.router.add_get('/messages', self.get_messages)
        self.app.router.add_get('/maps', self.get_maps)
        self.app.router.add_get('/style.css', self.get_style)
        self.app.router.add_get('/normalize.min.css', self.get_normalize)
        self.app.router.add_get('/socket.io.min.js', self.get_socketio)


    async def push_serial_data(self):
        while 1:
            await asyncio.sleep(1)
            await self.sio.emit("new", {"magic": [1,2,3]})

    async def start_background_tasks(self, app):
        self.app.serial_pub = asyncio.create_task(self.push_serial_data())

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