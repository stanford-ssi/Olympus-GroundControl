from io import BytesIO

import re

class Element:
    """ base class for a node in the widget tree """
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.parent = None
        self.identifier = None

    def render(self):
        """ returns a str of the html that encodes this element (and child elements).
            Put the elements javascript inline with the html
        """
        pass

    def add_child(self, child):
        """ adds a child element in the element tree """
        self.nodes.append(child)
        child.parent = self

    # def startup_state(self):
    #     """ function that gets run when a new client connects """
    #     for child in self.nodes:
    #         child.startup_state()

    # def register_callbacks(self, socketio):
    #     """ allows for elements to register any socketio callbacks they need """
    #     self.socketio = socketio
    #     for child in self.nodes:
    #         child.register_callbacks(socketio)

    def get_identifier(self):
        """ generates a unique (but consistent) id that can be used in client - server communication """
        if self.identifier is not None:
            return self.identifier
        if self.parent is None:
            self.identifier = self.name
        else:
            self.identifier = self.parent.get_identifier() + "." + self.name
            # we assume an element's name is unique among siblings

        return self.identifier

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




class Dashboard(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = dashboard)


class Messages(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        messages = self.load_template("templates/messages.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = messages)

class Maps(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        map = self.load_template("templates/map.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = map)

class Graphs(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        graphs = self.load_template("templates/graphs.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = graphs)

class Configure(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        configure = self.load_template("templates/configure.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = configure)