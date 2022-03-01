


from aiohttp import web
import socketio
import asyncio

from ui_elements import Dashboard

# class Main:

#     def __init__(self):
#         pass

#     def start(self):

dashboard = Dashboard("test")

async def get_dashboard(request):
    return web.Response(text=dashboard.render(), content_type='text/html')

async def get_style(request):
    return web.FileResponse('./static/style.css')

async def get_normalize(request):
    return web.FileResponse('./static/normalize.min.css')

async def get_socketio(request):
    return web.FileResponse('./static/socket.io.min.js')

def setup_routes(app):
    app.router.add_get('/', get_dashboard)
    app.router.add_get('/style.css', get_style)
    app.router.add_get('/normalize.min.css', get_normalize)
    app.router.add_get('/socket.io.min.js', get_socketio)

async def start_background_tasks(app):
    app['callback'] = asyncio.create_task(listen_to_redis(app))


app = web.Application()
sio = socketio.AsyncServer(async_mode='aiohttp')

sio.attach(app)

setup_routes(app)
web.run_app(app)

# @sio.on('data_request')
# def data_request(sid, data):
#     # send back data
#     pass