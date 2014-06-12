import math
import struct
import re
import sys

from rootpy.tree.cut import Cut
from rootpy.tree.categories import Categories


class Node(Categories):

    ENDOFTREE = -1
    LEAF = -2
    POINTERLEAF = -3
    GRAPH = -4
    FUNC = -5
    TRANSFORM = -6

    @classmethod
    def from_string(cls, string):

        tree = super(Node, cls).from_string(string)
        for node in Node.walk_nodes(tree):
            node.__class__ = cls
        return tree

    @classmethod
    def walk_nodes(cls, node):

        yield node
        if node.leftchild != None:
            for child in Node.walk_nodes(node.leftchild):
                yield child
        if node.rightchild != None:
            for child in Node.walk_nodes(node.rightchild):
                yield child

    def __init__(self,
                 feature,
                 data,
                 variables,
                 leftchild=None,
                 rightchild=None,
                 parent=None,
                 forbidleft=False,
                 forbidright=False,
                 cutType=-1):

        super(Node, self).__init__(
                feature,
                data,
                variables,
                leftchild,
                rightchild,
                parent,
                forbidleft,
                forbidright)
        self.cutType = cutType

    def add_pointer_leaves(self):

        for node in list(Node.walk_nodes(self)):
            if node.leftchild == None:
                pointer_node = Node(
                    feature=Node.POINTERLEAF,
                    data=0,variables=None)
                node.set_left(pointer_node)
            if node.rightchild == None:
                pointer_node = Node(
                    feature=Node.POINTERLEAF,
                    data=0,variables=None)
                node.set_right(pointer_node)
        return self

    def clone(self):

        leftclone = None
        if self.leftchild != None:
            leftclone = self.leftchild.clone()
        rightclone = None
        if self.rightchild != None:
            rightclone = self.rightchild.clone()
        return Node(self.feature,
                self.data,
                self.variables,
                leftclone,
                rightclone,
                self.parent,
                self.forbidleft,
                self.forbidright,
                self.cutType)

    def write(self, stream=None, format='txt', translator=None, depth=0):

        if stream is None:
            stream = sys.stdout
        feature = self.feature
        variables = self.variables
        data = self.data
        if isinstance(self, GraphNode):
            variable = self.variable
            if translator:
                feature = translator[feature]
                variable = translator[variable]
            if format == "txt":
                stream.write("%i\t%i\n" % (Node.GRAPH, len(data)))
                stream.write("%i\t%i\n" % (variable, feature))
                for X, Y in data:
                    stream.write("%f\t%f\n" % (X, Y))
            else:
                stream.write(struct.pack('i', Node.GRAPH))
                stream.write(struct.pack('i', len(data)))
                stream.write(struct.pack('i', variable))
                stream.write(struct.pack('i', feature))
                for X, Y in data:
                    stream.write(struct.pack('f', X))
                    stream.write(struct.pack('f', Y))
        elif isinstance(self, FuncNode):
            variable = self.variable
            if translator:
                feature = translator[feature]
                variable = translator[variable]
            if format == "txt":
                stream.write("%i\t%s\n" % (Node.FUNC, data))
                stream.write("%i\t%i\n" % (variable, feature))
            else:
                stream.write(struct.pack('i', Node.FUNC))
                stream.write(data + '\n')
                stream.write(struct.pack('i', variable))
                stream.write(struct.pack('i', feature))
        elif feature == Node.LEAF:
            if float(data) > 1.:
                print "WARNING: leaf node has purity %f" % float(data)
            if self.leftchild != None or self.rightchild != None:
                print "WARNING: leaf node has children!"
            if format == "txt":
                stream.write("%i\t%.6E\n" % (feature, float(data)))
            else:
                stream.write(struct.pack('i', feature))
                stream.write(struct.pack('f', float(data)))
        elif feature == Node.POINTERLEAF:
            if format == "txt":
                stream.write("%i\n" % feature)
            else:
                stream.write(struct.pack('i', feature))
        else:
            vtype = variables[feature][1]
            if translator:
                if feature < 0:
                    raise RuntimeError(
                            "node feature (%i) not valid "
                            "for internal node!" % feature)
                feature = translator[feature]
            if vtype == 'I':
                if format == "txt":
                    stream.write("%i\t%i\n" %
                            (feature, int(math.floor(float(data)))))
                else:
                    stream.write(struct.pack('i', feature))
                    stream.write(struct.pack('i', int(math.floor(float(data)))))
            else:
                if format == "txt":
                    stream.write("%i\t%.6E\n" % (feature, float(data)))
                else:
                    stream.write(struct.pack('i', feature))
                    stream.write(struct.pack('f', float(data)))
        if self.leftchild != None:
            self.leftchild.write(stream, format, translator, depth + 1)
        if self.rightchild != None:
            self.rightchild.write(stream, format, translator, depth + 1)
        if depth == 0:
            if format == "txt":
                stream.write("%i\n" % Node.ENDOFTREE)
            else:
                stream.write(struct.pack('i', Node.ENDOFTREE))


class GraphNode(Node):

    def __init__(self,
                 variable,
                 feature,
                 graph,
                 variables,
                 leftchild=None,
                 rightchild=None,
                 parent=None,
                 forbidleft=False,
                 forbidright=False,
                 cutType=-1):

        super(GraphNode, self).__init__(
                feature,
                graph,
                variables,
                leftchild,
                rightchild,
                parent,
                forbidleft,
                forbidright,
                cutType)
        self.variable = variable


class FuncNode(Node):

    def __init__(self,
                 variable,
                 feature,
                 func,
                 variables,
                 leftchild=None,
                 rightchild=None,
                 parent=None,
                 forbidleft=False,
                 forbidright=False,
                 cutType=-1):

        super(FuncNode, self).__init__(
                feature,
                func,
                variables,
                leftchild,
                rightchild,
                parent,
                forbidleft,
                forbidright,
                cutType)
        self.variable = variable



class BDT:

    def __init__(self,variables):

        self.weights = []
        self.trees = []
        self.variables = variables

    def add_tree(self,tree,weight):

        self.weights.append(weight)
        self.trees.append(tree)

    def add_variable(self,name,type):

        if (name,type) in self.variables:
            return self.variables.index((name,type))
        else:
            self.variables.append((name,type))
            return len(self.variables)-1

    def write(self,stream,format,translator = None):

        if format=="txt":
            stream.write(str(len(self.trees))+'\n')
        else:
            stream.write(struct.pack('i',len(self.trees)))
        for i in range(len(self.trees)):
            if format=="txt":
                stream.write("%.6E\n"%float(self.weights[i]))
            else:
                stream.write(struct.pack('f',float(self.weights[i])))
            node = self.trees[i]
            if node.is_leaf():
                print "Found a tree with only a root node! Are you pruning too much?"
                return
            node.write(stream,format,translator)
