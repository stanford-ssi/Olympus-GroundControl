
import re

import aiofiles
from aiofiles import os

from aiohttp import web
import json

import jinja2

class Element:
    """ base class for a node in the widget tree """
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.parent = None

    def render(self):
        """ returns a str of the html that encodes this element (and child elements).
            Put the elements javascript inline with the html
        """
        pass

    def add_child(self, child):
        """ adds a child element in the element tree """
        self.nodes.append(child)
        child.parent = self

    @property
    def top(self):
        node = self

        while True:
            try:
                node = node.parent
            except AttributeError:
                break

        return node

    @staticmethod
    def load_template(filename):
        with open(filename, 'r') as file:
            return file.read()

    @staticmethod
    def format(pre_format, **kwargs):
        """ poor mans html template system. {{var}} in the template can be over written with kwargs[var]"""

        # swaps double and single curly braces allowing us to use python str.format() method
        curly = { "{{":"{", "}}":"}", "{":"{{", "}":"}}" }
        substrings = sorted(curly, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        to_formant = regex.sub(lambda match: curly[match.group(0)], pre_format)

        return to_formant.format(**kwargs) 


class Graph(Element):
    pass

    def render(self):
        with open("templates/graphs.template.html") as file:
            graphs = jinja2.Template(file.read())

        def get_id_and_desc(node, path):
            return {"id": ".".join(path[1:]), "desc": node["desc"] }

        return graphs.render( list_ids =  self.top.flat_meta(get_id_and_desc), title = self.name )


class SquibTable(Element):
    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        with open("templates/table.squibs.template.html") as file:
            box = jinja2.Template(file.read())

        items = [ {"id":id,
            "qpin":self.top.get_meta(id, "qpin"),
            "desc":self.top.get_meta(id, "desc"), } for id in self.line_ids]

        return box.render( {"list_ids": items, "title": self.name} )

class ValveTable(Element):
    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        with open("templates/table.valves.template.html") as file:
            box = jinja2.Template(file.read())

        items = [ {"id":id,
            "qpin":self.top.get_meta(id, "qpin"),
            "desc":self.top.get_meta(id, "desc"), } for id in self.line_ids]

        test = box.render( {"list_ids": items, "title": self.name} )
        return test

class RawSensorTable(Element):
    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        with open("templates/table.sensors.template.html") as file:
            box = jinja2.Template(file.read())

        items = [ {"id":id,
            "qpin":self.top.get_meta(id, "qpin"),
            "unit":self.top.get_meta(id, "unit"),
            "desc":self.top.get_meta(id, "desc"), } for id in self.line_ids]

        test = box.render( {"list_ids": items, "title": self.name} )
        return test

class DataTable(Element):
    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        with open("templates/table.data.template.html") as file:
            box = jinja2.Template(file.read())

        items = [ {"id":id,
            "unit":self.top.get_meta(id, "unit"),
            "desc":self.top.get_meta(id, "desc"), } for id in self.line_ids]

        test = box.render( {"list_ids": items, "title": self.name} )
        return test

class Page(Element):

    def __init__(self, name, parent):
        super().__init__(name)
        self.parent = parent
        self.add_routes()

    def render(self):
        pass

    def add_routes(self):
        pass

    async def get_page(self, request):
        return web.Response(text=self.render(), content_type='text/html')


class Dashboard(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)


        self.add_child(
            RawSensorTable("Sensors", ["slate.press.ox_fill",
                                       "slate.press.ox_vent"]
            )
        )

        self.add_child(
            ValveTable("Solenoids", ["slate.valves.ox_fill",
                                       "slate.valves.ox_vent"]
            )
        )

        self.add_child(
            SquibTable("Squibs", ["slate.squibs.engine"]
            )
        )

        self.add_child(
            DataTable("Health", ["slate.health.v_bus",
                                "slate.health.current"]
            )
        )

        self.add_child(
            RawSensorTable("ADC", ["slate.quail.adc_in.ADC1",
                                       "slate.quail.adc_in.ADC2",
                                       "slate.quail.adc_in.ADC3",
                                       "slate.quail.adc_in.ADC4"]
            )
        )

        self.add_child(
            DataTable("Battery", ["slate.quail.board.error", 
                                "slate.quail.board.tick",
                                "slate.quail.battery.Voltage.raw", 
                                "slate.quail.battery.Current.raw"]
            )
        )

        # self.add_child(
        #     Graph("TEST")
        # )

    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content = "\n\n".join(child.render() for child in self.nodes))
        return self.format(template, page = dashboard_done, meta= json.dumps(self.top.metadata))


    def add_routes(self):
        self.top.app.router.add_get('/', self.get_page)
        self.top.app.router.add_get('/dashboard', self.get_page)


class Slate(Page):
    def render(self):
        messages = self.load_template("templates/slate.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = messages, meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/slate', self.get_page)

class Maps(Page):
    def render(self):
        map = self.load_template("templates/map.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = map, meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/maps', self.get_page)
        self.top.app.router.add_get('/mapdata/{url:.*}', self.get_mapdata)

    async def get_mapdata(self, request):
        url = request.match_info['url']
        filename = 'cache/' + url.replace('/', "!slash!") + '.png'

        mapbox_api = 'https://api.mapbox.com/{url}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'

        if await os.path.isfile(filename):
            async with aiofiles.open(filename, 'br') as file:
                data = await file.read()
        else:
            async with self.top.mapdata_session.get(mapbox_api.format(url = url)) as resp: 
                data = await resp.read() 
            async with aiofiles.open(filename, 'bw') as file:
                await file.write(data)

        #TODO support jpegs also
        return web.Response(body=data, content_type='image/png')


class Graphs(Page):

    def render(self):
        graphs = self.load_template("templates/graphs.template.html")
        template = self.load_template("templates/main.template.html")

        with open("templates/graphs.template.html") as file:
            graphs = jinja2.Template(file.read())

        def get_id_and_desc(node, path):
            return {"id": ".".join(path[1:]), "desc": node["desc"] }

        return self.format(template, page = graphs.render( list_ids =  self.top.flat_meta(get_id_and_desc), title = self.name ), meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/graphs', self.get_page)

class Configure(Page):

    def render(self):
        configure = self.load_template("templates/configure.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = configure, meta = self.top.metadata)

    def add_routes(self):
        self.top.app.router.add_get('/configure', self.get_page)