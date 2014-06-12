import xml.parsers.expat

class XMLParser:

    def __init__(self, xml_file):
        assert(xml_file != "")
        if type(xml_file) is file:
            self.xml_file = xml_file
        else:
            self.xml_file = open(xml_file, "r")
        self.Parser = xml.parsers.expat.ParserCreate()
        self.Parser.CharacterDataHandler = self.handleCharData
        self.Parser.StartElementHandler = self.handleStartElement
        self.Parser.EndElementHandler = self.handleEndElement

    def parse(self):
        self.Parser.ParseFile(self.xml_file)

    def handleCharData(self, data):
        pass
    def handleStartElement(self, name, attrs):
        pass
    def handleEndElement(self, name):
        pass
