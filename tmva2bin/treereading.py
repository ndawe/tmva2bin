import re
import copy

from rootpy.io import root_open

from .utils import readlines
from .decisiontree import BDT, Node, GraphNode, FuncNode
from .xmlparsing import XMLParser


class BDTXMLParser(XMLParser):

    def __init__(self,file,onlyVariables=False):

        XMLParser.__init__(self,file)
        self.BDT = None
        self.numVars = 0
        self.variables = []
        self.numTrees = 0
        self.currNode = None
        self.currBoostWeight = 0.
        self.onlyVariables = onlyVariables

    def getBDT(self):

        return self.BDT

    def handleStartElement(self, name, attrs):

        if name == "Variables":
            self.numVars = attrs["NVar"]
        elif name == "Variable":
            self.variables.append((attrs["Label"],attrs["Type"]))
        if not self.onlyVariables:
            if name == "Weights":
                self.numTrees = attrs["NTrees"]
            elif name == "BinaryTree":
                self.currBoostWeight = attrs["boostWeight"]
            elif name == "Node":
                if int(attrs["nType"]) in [-1,1]:
                    if attrs.has_key("purity"):
                        node = Node(Node.LEAF,
                                str(float(attrs["purity"])),
                                self.variables)
                    else:
                        node = Node(Node.LEAF,
                                str(float(attrs["nS"])/(float(attrs["nS"])+float(attrs["nB"]))),
                                self.variables)
                else:
                    node = Node(int(attrs["IVar"]),attrs["Cut"],self.variables)
                    node.cutType = int(attrs["cType"])
                if self.currNode:
                    if ((attrs["pos"] == "l" and self.currNode.cutType == 1) or
                        (attrs["pos"] == "r" and self.currNode.cutType == 0)):
                        self.currNode.leftchild = node
                    elif ((attrs["pos"] == "r" and self.currNode.cutType == 1) or
                          (attrs["pos"] == "l" and self.currNode.cutType == 0)):
                        self.currNode.rightchild = node
                    node.parent = self.currNode
                else:
                    self.BDT.add_tree(node,self.currBoostWeight)
                self.currNode = node

    def handleEndElement(self, name):

        if name == "Variables":
            self.BDT = BDT(self.variables)
        if not self.onlyVariables:
            if name == "BinaryTree":
                self.currNode = None
                self.currBoostWeight = 0.
            if name == "Node":
                self.currNode = self.currNode.parent

variable_regex = "[^:->\s]+(?::[IFif])?"
variable_pattern = re.compile("^%s$"% variable_regex)

graph_cut = re.compile("^(?P<filename>.+\.txt)$")
func_cut = re.compile("^(?P<variables>%s(?:,%s)*)(?:->)(?P<function>.+)$" %
        (variable_regex, variable_regex))

def getVariableList(filename,format="TD"):

    assert(format in ["TD","TDROOT","TMVA","D0"])

    if format == "TDROOT":
        import StringIO
        file = root_open(filename)
        input = file.Get("TreeInfo").GetTitle()
        input = StringIO.StringIO(input)
    else:
        input = open(filename,'r')
    binningVars = []
    if format in ("TD", "TDROOT"):
        binningVars,bdt = readTauDiscriminant(input,onlyVariables=True)
    elif format == "TMVA":
        bdt = readTMVA(input,onlyVariables=True)
    else:
        bdt = readD0(input,onlyVariables=True)

    return bdt.variables,binningVars

def readCuts(stream):
    """
    Parse the txt file and read the cuts
    """
    varList = []
    cutsList = []
    lines = readlines(stream,'\\')
    nlevels = -1
    for i,line in enumerate(lines):
        tokens = line.split()
        if not re.match(variable_pattern,tokens[0]):
            raise SyntaxError("%s is not valid syntax for defining a variable"% tokens[0])
        if ':' in tokens[0]:
            var,type = tokens[0].split(':')
        else:
            var,type = tokens[0],'F'
        varList.append((var,type.upper()))
        cuts = tokens[1:]
        if i==0:
            nlevels = len(cuts)
        elif len(cuts) != nlevels:
            print "mismatching number of cut levels:  %s"% cuts
            return None
        cutsList.append(cuts)

    variables = copy.copy(varList)

    treeVector = BDT(variables)
    parentNode = None
    parentCutType = None
    for treeIndex in range(nlevels):
        for i,((var,type),cuts) in enumerate(zip(varList,cutsList)):
            cut = cuts[treeIndex]
            if cut.startswith("<="):
                cutType = "PASSES_LEFT"
                cut = cut[2:]
            elif cut.startswith(">"):
                cutType = "PASSES_RIGHT"
                cut = cut[1:]
            else:
                raise SyntaxError("cut %s must begin with <= or >"% cut)

            graph_match = re.match(graph_cut,cut)
            func_match = re.match(func_cut,cut)

            try:
                cut = float(cut)
                node = Node(i,cut,variables)
            except ValueError:
                # Read as filename for file containing two columns of number for
                # X,Y of SlidingCut node
                if graph_match:
                    filename = cut
                    graph = []
                    file = open(filename,"r")
                    line = file.readline().strip()
                    if not re.match(variable_pattern,line):
                        raise SyntaxError(
                                ("%s is not valid syntax for defining "
                                "a variable") % line)
                    if ':' in line:
                        var,vartype = line.split(':')
                    else:
                        var,vartype = line,'F'
                    var_index = treeVector.add_variable(var,vartype.upper())
                    line = file.readline()
                    while line != "":
                        X,Y = line.split()
                        X = float(X.strip())
                        Y = float(Y.strip())
                        graph.append((X,Y))
                        line = file.readline()
                    file.close()
                    node = GraphNode(var_index,i,graph,variables)
                elif func_match:
                    var_strings = func_match.group('variables').split(',')
                    if len(var_strings) > 1:
                        raise NotImplementedError(
                                "handling functions of more than one "
                                "variable is not yet implemented")
                    var_string = var_strings[0]
                    if ':' in var_string:
                        var,vartype = var_string.split(':')
                    else:
                        var,vartype = var_string,'F'
                    var_index = treeVector.add_variable(var,vartype.upper())
                    function = func_match.group('function')
                    node = FuncNode(var_index,i,function,variables)
                else:
                    raise SyntaxError("cuts %s is not understood"% cut)

            if i==0:
                treeVector.add_tree(node,1.)
            elif parentCutType == "PASSES_LEFT":
                parentNode.set_left(node)
            elif parentCutType == "PASSES_RIGHT":
                parentNode.set_right(node)
            else:
                return None

            if cutType == "PASSES_LEFT":
                node.set_right(Node(Node.LEAF,0.,variables))
                if i == len(varList) - 1:
                    node.set_left(Node(Node.LEAF,1.,variables))
            elif cutType == "PASSES_RIGHT":
                node.set_left(Node(Node.LEAF,0.,variables))
                if i == len(varList) - 1:
                    node.set_right(Node(Node.LEAF,1.,variables))
            else:
                return None

            parentNode = node
            parentCutType = cutType
    return treeVector

def readD0(stream,onlyVariables=False):

    nvar = 0
    ntrees = 0
    varList = []

    line = stream.readline()
    while line.startswith('#') or line == '\n':
        line = stream.readline()

    ntrees = int(line)

    line = stream.readline()
    while line == '\n':
        line = stream.readline()

    nvar = int(line)

    for i in range(nvar):
        line = stream.readline().strip('\n').upper()
        varList.append(line)

    bdt = BDT(varList)
    if onlyVariables:
        return bdt

    tokens = stream.readline().split()
    while len(tokens) == 3:
        if tokens[1] == "-10":
            weight = tokens[2]
            tokens = stream.readline().split()
            node = Node(int(tokens[1]),tokens[2])
            bdt.addTree(node, weight)
            nodeStack = [(node,1)]
        else:
            index = int(tokens[0])
            node = Node(int(tokens[1]),tokens[2])

            while index/2 != nodeStack[-1][1]:
                nodeStack.pop()

            if index == 2 * nodeStack[-1][1]:
                nodeStack[-1][0].setLeftChild(node)
            elif index == 2 * nodeStack[-1][1] + 1:
                nodeStack[-1][0].setRightChild(node)

            nodeStack.append((node,index))
        tokens = stream.readline().split()

    return bdt

def readTauDiscriminant(stream,onlyVariables=True):
    """
    Read TauDiscriminant format (currently only extracts variables)
    """
    binningVariableNames = []
    numBinningVariables = int(stream.readline())
    if numBinningVariables > 0:
        for i in range(numBinningVariables):
            binningVariableNames.append(stream.readline().split())
        node = stream.readline()
        while int(node.split()[0]) != Node.ENDOFTREE:
            node = stream.readline()

    variableList = []
    numVariables = int(stream.readline())
    for i in range(numVariables):
        variableList.append(stream.readline().split())

    return binningVariableNames,BDT(variableList)

def readTMVA(stream,onlyVariables=False):

    parser = BDTXMLParser(stream,onlyVariables=onlyVariables)
    parser.parse()
    return parser.getBDT()
