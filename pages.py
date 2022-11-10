
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
            "quail.telemetry.pt3",
            "quail.telemetry.pt4"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(MiniGraph("Fuel Fill", [
            "quail.telemetry.pt1",
            "quail.telemetry.pt2"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(MiniGraph("Mass", [
            "quail.telemetry.load_mass"],
            time_seconds=60, units=["N->kg"]))

        self.add_child(
            RawSensorTable("Pressure Sensors", ["quail.telemetry.pt1",
                                                "quail.telemetry.pt2",
                                                "quail.telemetry.pt3",
                                                "quail.telemetry.pt4",
                                                "quail.telemetry.pt5",
                                                "quail.telemetry.pt6",
                                                "quail.telemetry.pt7",
                                                "quail.telemetry.pt8"], units=["Pa->psi"] * 8
                           )
        )

        self.add_child(
            RawSensorTable("Other Sensors", ["quail.telemetry.load_mass",
                                             "quail.telemetry.lc1",
                                             "quail.telemetry.lc2",
                                             "quail.telemetry.tc1",
                                             "quail.telemetry.tc2"], units=["N->kg"] * 3 + [None] * 2
                           )
        )

        self.add_child(
            ValveTable("Solenoids", ["quail.telemetry.s1",
                                     "quail.telemetry.s2",
                                     "quail.telemetry.s3",
                                     "quail.telemetry.s4",
                                     "quail.telemetry.s5",
                                     "quail.telemetry.s6",
                                     "quail.telemetry.s7",
                                     "quail.telemetry.s8",
                                     "quail.telemetry.s9",
                                     "quail.telemetry.s10",
                                     "quail.telemetry.s11",
                                     "quail.telemetry.s12"]

                       )
        )

        # self.add_child(
        #     SquibTable("Squibs", ["slate.quail.squib.E1", "slate.quail.squib.E2"]
        #                )
        # )

        self.add_child(
            RawSensorTable("Housekeeping", ["quail.telemetry.v_batt",
                                            "quail.telemetry.i_batt"]
                           )
        )

        self.add_child(
            DataTable("Health", ["quail.telemetry.tick",
                                 "quail.telemetry.comms",
                                 "quail.telemetry.logging",
                                 "quail.telemetry.error",
                                 "quail.telemetry.watchdog_counter",
                                 "quail.telemetry.watchdog_control"]
                      )
        )

    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content="\n\n".join(
            child.render() for child in self.nodes))
        return self.format(template, page=dashboard_done, meta=json.dumps({"test": "hi"}))

    def add_routes(self):
        self.top.app.router.add_get('/', self.get_page)
        self.top.app.router.add_get('/dashboard', self.get_page)


class FillPage(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal",
            "slate.quail.sensors.PT4.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"],
            time_seconds=60, units=["N->kg"]))

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal",
            "slate.quail.sensors.PT2.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(
            RawSensorTable("Ox Sensors", [
                "slate.quail.sensors.PT3",
                "slate.quail.sensors.PT4",
            ], units=["Pa->psi"] * 2
            )
        )

        self.add_child(
            ValveTable("Ox Valves", ["slate.quail.valves.S5",
                                     "slate.quail.valves.S6",
                                     "slate.quail.valves.S8"]
                       )
        )

        self.add_child(
            RawSensorTable("Other Sensors", ["slate.quail.sensors.LCSum",
                                             "slate.quail.sensors.TC1",
                                             "slate.quail.sensors.TC2"], units=["N->kg"] * 1 + [None] * 2
                           )
        )

        self.add_child(
            RawSensorTable("Fuel Sensors", [
                "slate.quail.sensors.PT1",
                "slate.quail.sensors.PT2",
            ], units=["Pa->psi"] * 2
            )
        )

        self.add_child(
            ValveTable("Fuel Valves", ["slate.quail.valves.S3",
                                       "slate.quail.valves.S4"]
                       )
        )

    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content="\n\n".join(
            child.render() for child in self.nodes))
        return self.format(template, page=dashboard_done, meta=json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/fillpage', self.get_page)


class LaunchPage(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal",
            "slate.quail.sensors.PT4.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"],
            time_seconds=60, units=["N->kg"]))

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal",
            "slate.quail.sensors.PT2.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(
            RawSensorTable("Sensors", [
                "slate.quail.sensors.LCSum",
                "slate.quail.sensors.PT2",
                "slate.quail.sensors.PT4",
            ], units=["N->kg"] + ["Pa->psi"] * 2
            )
        )

        self.add_child(
            ValveTable("Valves", ["slate.quail.valves.S4",
                                  "slate.quail.valves.S6"]
                       )
        )

        self.add_child(
            SquibTable("Squibs", ["slate.quail.squib.E1", "slate.quail.squib.E2"]
                       )
        )

        self.add_child(
            ValveTable("Launch Valves", ["slate.quail.valves.S1",
                                         "slate.quail.valves.S2"]
                       )
        )

    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content="\n\n".join(
            child.render() for child in self.nodes))
        return self.format(template, page=dashboard_done, meta=json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/launchpage', self.get_page)


class Sequencing(Dashboard):

    def __init__(self, name, parent):
        Page.__init__(self, name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal",
            "slate.quail.sensors.PT4.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

        self.add_child(Sequence("My Sequencing", {
            "slate.quail.sequence.engine_state": ["ENGINE_ABORT", "ENGINE_IDLE", "ENGINE_FILL", "ENGINE_FULL", "ENGINE_FIRE", "MAIN_ACTUATION"],
            "slate.quail.sequence.ox_tank_state": ["TANK_IDLE_EMPTY", "TANK_IDLE_PRESS", "TANK_EMPTY", "TANK_DRAIN", "TANK_FILL", "TANK_FULL", "TANK_BLEED", "TANK_READY"],
            "slate.quail.sequence.fuel_tank_state": ["TANK_IDLE_EMPTY", "TANK_IDLE_PRESS", "TANK_EMPTY", "TANK_DRAIN", "TANK_FILL", "TANK_FULL", "TANK_BLEED", "TANK_READY"],
            "slate.quail.sequence.ox_op_mass": "N",
            "slate.quail.sequence.fuel_op_press": "Pa",
        }
        ))

    # def render(self):
    #     page = self.load_template("templates/sequencing.template.html")
    #     template = self.load_template("templates/main.template.html")

    #     return self.format(template, page = page, meta= json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/sequencing', self.get_page)


class Slate(Page):
    def render(self):
        messages = self.load_template("templates/slate.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page=messages, meta=json.dumps({"hi": "ho"}))

    def add_routes(self):
        self.top.app.router.add_get('/slate', self.get_page)


class Maps(Page):

    def render(self):
        map = self.load_template("templates/map.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page=map, meta=json.dumps(self.top.metaslate))

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

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(mapbox_api.format(url=url)) as resp:
                    data = await resp.read()

            async with aiofiles.open(filename, 'bw') as file:
                await file.write(data)

        # TODO support jpegs also
        return aiohttp.web.Response(body=data, content_type='image/png')


class Graphs(Page):

    def render(self):
        graphs = self.load_template("templates/graphs.template.html")
        template = self.load_template("templates/main.template.html")

        with open("templates/graphs.template.html") as file:
            graphs = jinja2.Template(file.read())

        flat_key_list = [[{"id": f"quail.{slate_key}.{key}", "desc": f"{meta['desc']}"} for key,
                          meta in slate["channels"].items()] for slate_key, slate in self.top.metaslate["quail"].items()]
        flat_key_list = sum(flat_key_list, [])

        return self.format(template, page=graphs.render(list_ids=flat_key_list, title=self.name), meta=json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/graphs', self.get_page)


class Configure(Page):

    def render(self):
        configure = self.load_template("templates/configure.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page=configure, meta=self.top.metaslate)

    def add_routes(self):
        self.top.app.router.add_get('/configure', self.get_page)


class Fuel_Graph(Page):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Fuel Fill", [
            "slate.quail.sensors.PT1.cal",
            "slate.quail.sensors.PT2.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

    def render(self):
        template = self.load_template("templates/embedable.template.html")
        return self.format(template, content="\n\n".join(child.render() for child in self.nodes), meta=json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/fuel_graph', self.get_page)


class Ox_Graph(Page):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Ox Fill", [
            "slate.quail.sensors.PT3.cal",
            "slate.quail.sensors.PT4.cal"],
            time_seconds=60, units=["Pa->psi"] * 2))

    def render(self):
        template = self.load_template("templates/embedable.template.html")
        return self.format(template, content="\n\n".join(child.render() for child in self.nodes), meta=json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/ox_graph', self.get_page)


class Mass_Graph(Page):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_child(MiniGraph("Mass", [
            "slate.quail.sensors.LCSum.cal"],
            time_seconds=60, units=["N->kg"]))

    def render(self):
        template = self.load_template("templates/embedable.template.html")
        return self.format(template, content="\n\n".join(child.render() for child in self.nodes), meta=json.dumps(self.top.metaslate))

    def add_routes(self):
        self.top.app.router.add_get('/mass_graph', self.get_page)
