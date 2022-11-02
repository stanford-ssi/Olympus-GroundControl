
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
                # assert source == self.top.get_meta(id, "raw.unit")
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

