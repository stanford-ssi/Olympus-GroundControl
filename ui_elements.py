
import re

import aiofiles
from aiofiles import os

import json
import aiohttp

import jinja2

from unit_conversions import unit_factor

def get_uuid(magic = [0]):
    # very ugy hack but we need something unique
    # idealy should be seperate counter for each request etc
    magic[0] += 1
    return "UUDI_" + str(magic[0])

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
            "qpin":self.top.get_meta(id, "fir.qpin"),
            "desc":self.top.get_meta(id, "fir.desc"), } for id in self.line_ids]

        return box.render( {"list_ids": items, "title": self.name} )

class ValveTable(Element):
    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        with open("templates/table.valves.template.html") as file:
            box = jinja2.Template(file.read())

        items = [ {"id":id,
            "qpin":self.top.get_meta(id, "stt.qpin"),
            "desc":self.top.get_meta(id, "stt.desc"), } for id in self.line_ids]

        test = box.render( {"list_ids": items, "title": self.name, "uuid": get_uuid() } )
        return test

class RawSensorTable(Element):
    def __init__(self, name, line_ids, units = None):
        super().__init__(name)
        self.line_ids = line_ids

        if units == None:
            self.units = {id: None for id in line_ids }
        else:
            self.units = {id: s for id,s in zip(line_ids, units) }

    def render(self):
        with open("templates/table.sensors.template.html") as file:
            box = jinja2.Template(file.read())

        items = []
        for id in self.line_ids:

            if self.units[id] is None:
                unit = self.top.get_meta(id, "raw.unit")
            else:
                source, target = self.units[id].split("->")
                assert source == self.top.get_meta(id, "raw.unit")
                unit = target

            items.append( {"id":id,
                            "conv": unit_factor( self.units[id] ),
                            "qpin":self.top.get_meta(id, "raw.qpin"),
                            "unit": unit,
                            "desc":self.top.get_meta(id, "raw.desc"), })

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

class MiniGraph(Element):
    def __init__(self, name, line_ids, time_seconds = 60, units = None):
        super().__init__(name)
        self.line_ids = line_ids

        self.colors = ["#348ABD", "#A60628", "#7A68A6", "#467821", "#CF4457", "#188487", "#E24A33" ]
        self.time_seconds = time_seconds

        if units == None:
            self.units = {id: None for id in line_ids }
        else:
            self.units = {id: s for id,s in zip(line_ids, units) }

    def render(self):
        with open("templates/mini_graph.template.html") as file:
            box = jinja2.Template(file.read())

        items = [ {"id":id,
            "conv": unit_factor( self.units[id] ),
            # "unit":self.top.get_meta(id, "unit"),
            "unit": self.top.get_meta(id, "unit") if self.units[id] is None else self.units[id].split("->")[1],
            "desc":self.top.get_meta(id, "desc"), 
            "color":self.colors[i] } for i, id in enumerate(self.line_ids)]

        test = box.render( {"list_ids": items, "title": self.name, "total_points": self.time_seconds * 20, "uuid": get_uuid()  } )
        return test

class Sequence(Element):
    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        with open("templates/sequencing.template.html") as file:
            box = jinja2.Template(file.read())


        state_machines = []
        writable_values = []
        for id, unit in self.line_ids.items():   
            if type(unit) == type([]):
                state_machines.append( {"id":id, "unit": unit, "desc": self.top.get_meta(id, "desc"), "len": len(unit) } )
            else:
                writable_values.append( {"id":id, "unit": unit, "desc": self.top.get_meta(id, "desc"), } )

        test = box.render( {"state_machines": state_machines,
                            "writable_values": writable_values,
                            "title": self.name} )
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
        return aiohttp.web.Response(text=self.render(), content_type='text/html')


class Dashboard(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)

        # Note the keys that are added to the tables need to be unique

        # self.add_child(MiniGraph("Testing", [ "slate.quail.battery.Voltage.cal",
        #                                     "slate.quail.battery.Current.cal"], 
        #                                     time_seconds = 60))

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal", 
            "slate.quail.sensors.PT4.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal", 
            "slate.quail.sensors.PT2.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"], 
                time_seconds = 60, units = ["N->kg"] ))

        self.add_child(
            RawSensorTable("Pressure Sensors", [ "slate.quail.sensors.PT1",
                                       "slate.quail.sensors.PT2",
                                       "slate.quail.sensors.PT3",
                                       "slate.quail.sensors.PT4",
                                       "slate.quail.sensors.PT5",
                                       "slate.quail.sensors.PT6",
                                       "slate.quail.sensors.PT7",
                                       "slate.quail.sensors.PT8"], units = ["Pa->psi"] * 8
            )
        )

        self.add_child(
            RawSensorTable("Other Sensors", ["slate.quail.sensors.LCSum",
                                        "slate.quail.sensors.LC1",
                                       "slate.quail.sensors.LC2",
                                       "slate.quail.sensors.TC1",
                                       "slate.quail.sensors.TC2"], units = ["N->kg"] * 3 + [None] * 2
            )
        )

        self.add_child(
            ValveTable("Solenoids", ["slate.quail.valves.S1",
                                       "slate.quail.valves.S2",
                                       "slate.quail.valves.S3",
                                       "slate.quail.valves.S4",
                                       "slate.quail.valves.S5",
                                       "slate.quail.valves.S6",
                                       "slate.quail.valves.S7",
                                       "slate.quail.valves.S8",
                                       "slate.quail.valves.S9",
                                       "slate.quail.valves.S10",
                                       "slate.quail.valves.S11",
                                       "slate.quail.valves.S12"]

            )
        )

        self.add_child(
            SquibTable("Squibs", ["slate.quail.squib.E1", "slate.quail.squib.E2"]
            )
        )

        self.add_child(
            RawSensorTable("MAGIC", ["slate.quail.battery.Voltage",
                                       "slate.quail.battery.Current"]
            )
        )

        self.add_child(
            DataTable("Health", ["slate.quail.board.error", 
                                "slate.quail.board.tick",
                                "slate.quail.battery.Voltage.cal", 
                                "slate.quail.battery.Current.cal"]
            )
        )

    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content = "\n\n".join(child.render() for child in self.nodes))
        return self.format(template, page = dashboard_done, meta= json.dumps(self.top.metadata))


    def add_routes(self):
        self.top.app.router.add_get('/', self.get_page)
        self.top.app.router.add_get('/dashboard', self.get_page)


class FillPage(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal", 
            "slate.quail.sensors.PT4.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"], 
                time_seconds = 60, units = ["N->kg"] ))

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal", 
            "slate.quail.sensors.PT2.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))


        self.add_child(
            RawSensorTable("Ox Sensors", [
                                       "slate.quail.sensors.PT3",
                                       "slate.quail.sensors.PT4",
                                       ], units = ["Pa->psi"] * 2
            )
        )

        self.add_child(
            ValveTable("Ox Valves", [ "slate.quail.valves.S5",
                                       "slate.quail.valves.S6",
                                       "slate.quail.valves.S8"]
            )
        )

        self.add_child(
            RawSensorTable("Other Sensors", ["slate.quail.sensors.LCSum",
                                       "slate.quail.sensors.TC1",
                                       "slate.quail.sensors.TC2"], units = ["N->kg"] * 1 + [None] * 2
            )
        )


        self.add_child(
            RawSensorTable("Fuel Sensors", [
                                       "slate.quail.sensors.PT1",
                                       "slate.quail.sensors.PT2",
                                       ], units = ["Pa->psi"] * 2
            )
        )

        self.add_child(
            ValveTable("Fuel Valves", [ "slate.quail.valves.S3", 
                                        "slate.quail.valves.S4"]
            )
        )



    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content = "\n\n".join(child.render() for child in self.nodes))
        return self.format(template, page = dashboard_done, meta= json.dumps(self.top.metadata))


    def add_routes(self):
        self.top.app.router.add_get('/fillpage', self.get_page)


class LaunchPage(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal", 
            "slate.quail.sensors.PT4.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"], 
                time_seconds = 60, units = ["N->kg"] ))

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal", 
            "slate.quail.sensors.PT2.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))


        self.add_child(
            RawSensorTable("Sensors", [
                                       "slate.quail.sensors.LCSum",
                                       "slate.quail.sensors.PT2",
                                       "slate.quail.sensors.PT4",
                                       ], units = ["N->kg"] + ["Pa->psi"] * 2
            )
        )

        self.add_child(
            ValveTable("Valves", [ "slate.quail.valves.S4",
                                    "slate.quail.valves.S6"]
            )
        )

        self.add_child(
            SquibTable("Squibs", ["slate.quail.squib.E1", "slate.quail.squib.E2"]
            )
        )

        self.add_child(
            ValveTable("Launch Valves", [ "slate.quail.valves.S1", 
                                        "slate.quail.valves.S2"]
            )
        )


    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content = "\n\n".join(child.render() for child in self.nodes))
        return self.format(template, page = dashboard_done, meta= json.dumps(self.top.metadata))


    def add_routes(self):
        self.top.app.router.add_get('/launchpage', self.get_page)

class Sequencing(Dashboard):

    def __init__(self, name, parent):
        Page.__init__(self,name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal", 
            "slate.quail.sensors.PT4.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

        self.add_child(Sequence("My Sequencing", {
            "slate.quail.sequence.engine_state" : ["ENGINE_ABORT", "ENGINE_IDLE", "ENGINE_FILL", "ENGINE_FULL", "ENGINE_FIRE", "MAIN_ACTUATION"],
            "slate.quail.sequence.ox_tank_state" : ["TANK_IDLE_EMPTY", "TANK_IDLE_PRESS", "TANK_EMPTY", "TANK_DRAIN", "TANK_FILL", "TANK_FULL", "TANK_BLEED", "TANK_READY"],
            "slate.quail.sequence.fuel_tank_state" : ["TANK_IDLE_EMPTY", "TANK_IDLE_PRESS", "TANK_EMPTY", "TANK_DRAIN", "TANK_FILL", "TANK_FULL", "TANK_BLEED", "TANK_READY"],
            "slate.quail.sequence.ox_op_mass" : "N",
            "slate.quail.sequence.fuel_op_press" : "Pa",
        }
        ))
    

    # def render(self):
    #     page = self.load_template("templates/sequencing.template.html")
    #     template = self.load_template("templates/main.template.html")

    #     return self.format(template, page = page, meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/sequencing', self.get_page)

class Slate(Page):
    def render(self):
        messages = self.load_template("templates/slate.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = messages, meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/slate', self.get_page)

class Maps(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.mapdata_session = aiohttp.ClientSession()

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
            await os.makedirs('cache/', exist_ok=True)
            async with self.mapdata_session.get(mapbox_api.format(url = url)) as resp: 
                data = await resp.read() 
            async with aiofiles.open(filename, 'bw') as file:
                await file.write(data)

        #TODO support jpegs also
        return aiohttp.web.Response(body=data, content_type='image/png')


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