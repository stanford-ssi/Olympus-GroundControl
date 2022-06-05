
import re

import aiofiles
from aiofiles import os

import json
import aiohttp

import jinja2

from unit_conversions import unit_factor

from ui_elements import Element, Graph, SquibTable, ValveTable, RawSensorTable, DataTable, MiniGraph, Sequence


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


class Fuel_Graph(Page):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal", 
            "slate.quail.sensors.PT2.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

    def render(self):
        template = self.load_template("templates/embedable.template.html")
        return self.format(template, content = "\n\n".join(child.render() for child in self.nodes), meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/fuel_graph', self.get_page)

class Ox_Graph(Page):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal", 
            "slate.quail.sensors.PT4.cal"], 
                time_seconds = 60, units = ["Pa->psi"] * 2))

    def render(self):
        template = self.load_template("templates/embedable.template.html")
        return self.format(template, content = "\n\n".join(child.render() for child in self.nodes), meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/ox_graph', self.get_page)

class Mass_Graph(Page):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"], 
                time_seconds = 60, units = ["N->kg"] ))

    def render(self):
        template = self.load_template("templates/embedable.template.html")
        return self.format(template, content = "\n\n".join(child.render() for child in self.nodes), meta= json.dumps(self.top.metadata))

    def add_routes(self):
        self.top.app.router.add_get('/mass_graph', self.get_page)



