"""html2template - A fast, powerful, easy-to-use HTML templating system.

See Manual.txt for documentation.
"""

# TO DO: decoration via node replacement (e.g. to add alternating row colours in a table)

# TO DO: 'val' -> 'text', 'raw' -> 'html'

# TO DO: better error reporting on bad node lookups (trap error in current node/top-level Template instance and print structure?)

# TO DO: auto-indent repeaters that don't have a sep (i.e. compiler should get leading indent from start of line, and set that as repeater's default separator string)

# html2template - A fast, powerful, easy-to-use HTML templating system.
#
# Copyright (C) 2004 HAS <hamish.sanderson@virgin.net>
#
# This library is free software; you can redistribute it and/or modify it under 
# the terms of the GNU Lesser General Public License as published by the Free 
# Software Foundation; either version 2.1 of the License, or (at your option) 
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License 
# along with this library; if not, write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


__all__ = ['ParseError', 'Node', 'Template']

from HTMLParser import HTMLParser # TO DO: replace with a better parser (or patch this one)
from keyword import kwlist
import re


# TO DO: 'hunt' method for locating sub-nodes/super-nodes by name (hunt-up would be esp. useful for recursive rendering)
# TO DO: 'rec' node type for easier recursive rendering (searches up node tree for a con/rep node of same name, then clones that)

#################################################
# SUPPORT
#################################################

def renderAtts(atts):
    result = ''
    for name, value in atts:
        if value is None:
            result += ' ' + name
        elif '"' in value:
            result += " %s='%s'" % (name, value)
        else:
            result += ' %s="%s"' % (name, value)
    return result

def defaultEncoder(txt):
    return txt.replace('&', '&amp;').replace(
            '<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def defaultDecoder(txt):
    return txt.replace('&quot;', '"').replace(
            '&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')


#################################################
# TEMPLATE PARSER
#################################################

class ParseError(Exception):
    """A template parsing error."""
    pass


class ElementCollector:

    def __init__(self, *args):
        self.nodeType, self.nodeName, self.tagName, self.atts, \
                self.isEmpty, self.omitTags, self.shouldDelete = args
        self.content = ['']
        self.elementNames = {}
        self.__depth = 1
    
    def incDepth(self):
        self.__depth += 1
        
    def decDepth(self):
        self.__depth -= 1
        
    def isComplete(self):
        return self.__depth < 1
        
    def addText(self, txt):
        self.content[-1] += txt
        
    def addElement(self, node, nodeType, nodeName):
        self.content.extend([node, ''])
        self.elementNames[nodeName] = nodeType


class Parser(HTMLParser):

    __specialAttValuePattern = re.compile('(-)?(con|rep|sep|del):(.*)')
    __validNodeNamePattern = re.compile('[a-zA-Z][_a-zA-Z0-9]*')
    
    # List of words already used as property and method names,
    # so cannot be used as template node names as well:
    __invalidNodeNames = kwlist + [
            'nodetype', 'nodename',
            'text', 'html', 'atts', 
            'omittags', 'omit', 
            'add', 'repeat', 
            'copy']
    
    def __init__(self, attribute, encoder, decoder):
        HTMLParser.__init__(self)
        self.__specialAttributeName = attribute
        self.__encoder = encoder
        self.__decoder = decoder
        self.__outputStack = [
                ElementCollector('tem', '', None, None, False, False, False)]
    
    def __isSpecialTag(self, atts, specialAttName):
        for name, value in atts:
            if name == specialAttName:
                value = self.__specialAttValuePattern.match(value)
                if value:
                    atts = dict(atts)
                    del atts[specialAttName]
                    omitTags, nodeType, nodeName = value.groups()
                    return True, nodeType, nodeName, omitTags, atts
        return False, '', '', False, renderAtts(atts)
    
    def __startTag(self, tagName, atts, isEmpty):
        node = self.__outputStack[-1]
        if node.shouldDelete:
            isSpecial = 0
        else:
            isSpecial, nodeType, nodeName, omitTags, atts = \
                    self.__isSpecialTag(atts, self. __specialAttributeName)
        if isSpecial:
            if nodeType != 'del' and (
                    not self.__validNodeNamePattern.match(nodeName) 
                    or nodeName in self.__invalidNodeNames):
                raise ParseError, "Invalid node name: %r" % nodeName
            shouldDelete = nodeType == 'del'
            if node.elementNames.has_key(nodeName):
                if node.elementNames[nodeName] == nodeType:
                    shouldDelete = True
                elif nodeType != 'sep':
                    raise ParseError, ("Invalid node name: %s:%s " 
                            "(node %s:%s already found).") % (nodeType,  
                            nodeName, node.elementNames[nodeName], nodeName)
            self.__outputStack.append(ElementCollector(nodeType, nodeName, 
                    tagName, atts, isEmpty, omitTags, shouldDelete))
        else:
            if node.tagName == tagName:
                node.incDepth()
            if not node.shouldDelete:
                if isEmpty:
                    endOfOpenTag = ' />'
                else:
                    endOfOpenTag = '>'
                node.addText('<' + tagName + atts + endOfOpenTag)
    
    def __hasCompletedElement(self, element, parent):
        if element.isEmpty:
            content = []
        else:
            content = element.content
        if element.nodeType in ['con', 'rep']:
            node = makeNode(
                    element.nodeType, element.nodeName, element.tagName, 
                    element.atts, content, self.__encoder, self.__decoder)
            if element.omitTags:
                node.omittags()
            parent.addElement(node, element.nodeType, element.nodeName)
        else: # element.nodeType == 'sep'
            # Add this separator to its repeater
            for node in parent.content[1::2]:
                if node._nodeName == element.nodeName:
                    if node._nodeType != 'rep':
                        raise ParseError, ("Can't process separator node "
                                "'sep:%s': repeater node 'rep:%s' wasn't "
                                "found. Found node '%s:%s' instead.") % (
                                element.nodeName, element.nodeName, 
                                element.nodeType, element.nodeName)
                    if element.omitTags:
                        if content:
                            node._sep = content[0]
                        else:
                            node._sep = ''
                    else:
                        if content:
                            node._sep = '<%s%s>%s</%s>' % (element.tagName, 
                                    renderAtts(element.atts.items()), 
                                    content[0], element.tagName)
                        else:
                            node._sep = '<%s%s />' % (element.tagName, 
                                    renderAtts(element.atts.items()))
                    return
            raise ParseError, ("Can't process separator node 'sep:%s' in node " 
                    "'%s:%s': repeater node 'rep:%s' wasn't found.") % (
                    element.nodeName, parent.nodeType, parent.nodeName, 
                    element.nodeName)
    
    def __endTag(self, tagName, isEmpty):
        node = self.__outputStack[-1]
        if node.tagName == tagName:
            node.decDepth()
        if node.isComplete():
            self.__outputStack.pop()
            if not node.shouldDelete:
                parent = self.__outputStack[-1]
                self.__hasCompletedElement(node, parent)
        elif not isEmpty:
            node.addText('</%s>' % tagName)

    def __addText(self, txt):
        self.__outputStack[-1].addText(txt)
    
    # event handlers

    def handle_startendtag(self, tagName, atts):
        self.__startTag(tagName, atts, True)
        self.__endTag(tagName, True)

    def handle_starttag(self, tagName, atts):
        self.__startTag(tagName, atts, False)

    def handle_endtag(self, tagName):
        self.__endTag(tagName, False)

    def handle_charref(self, txt):
        self.__addText('&#%s;' % txt)

    def handle_entityref(self, txt):
        self.__addText('&%s;' % txt)

    def handle_data(self, txt):
        self.__addText(txt)

    def handle_comment(self, txt):
        self.__addText('<!--%s-->' % txt)

    def handle_decl(self, txt):
        self.__addText('<!%s>' % txt)

    def handle_pi(self, txt):
        self.__addText('<?%s?>' % txt)
    
    def result(self):
        element = self.__outputStack.pop()
        if element.nodeType != 'tem':
            raise ParseError, "Can't compile template: node '%s:%s' is not " \
                    "correctly closed." % (element.nodeType, element.nodeName)
        return element.content


#################################################
# OBJECT MODEL CLASSES
#################################################

class CloneNode(object): # performance optimisation
    """Makes cloned nodes."""
    def __init__(self, node):
        self.__dict__ = node.__dict__.copy()
        self.__class__ = node.__class__


class Node(object):
    """Abstract base class for template nodes; used for type checking when 
       user replaces an existing template node with a new one.
    """
    
    nodetype = property(lambda self:self._nodeType)
    nodename = property(lambda self:self._nodeName)
    
    def structure(self):
        """Render the template's structure for diagnostic use."""
        out = []
        def walk(node, indent, out):
            out.append(indent + node.nodetype + ':' + node.nodename)
            for subnode in node:
                walk(subnode, '\t' + indent, out)
        walk(self, '',out)
        return '\n'.join(out)
    
    def render(self, *args):
        """Render this node as text."""
        if args:
            self = self.copy()
            args[0](self, *args[1:])
        collector = []
        self._render(collector)
        try: # quick-n-dirty error reporting; not a real substitute for type-
            # checking for bad value assignments at point of origin, but cheap
            return ''.join(collector)
        except TypeError:
            raise TypeError, "Can't render template: some node's content " \
                    "was set to a non-text value."


class Container(Node):
    """A Container node has a one-to-one relationship with the node that 
       contains it.
    """
    
    _nodeType = 'con'
    
    def __init__(self, nodeName, tagName, atts):
        self._nodeName = nodeName
        self._atts = dict(atts) # On cloning, shallow copy this dict.
        if isinstance(self, NullContent):
            self.__startTag = '<%s%%s />' % tagName
            self.__endTag = ''
        else:
            self.__startTag = '<%s%%s>' % tagName
            self.__endTag = '</%s>' % tagName
        self.__omitTags = False
        self._omit = False
    
    def __len__(self):
        return int(not self._omit)
    
    def copy(self):
        clone = CloneNode(self) # performance optimisation
        clone._atts = self._atts.copy()
        return clone
    
    def _renderNode(self, collector):
        if self.__omitTags:
            self._renderContent(collector)
        else:
            collector.append(self.__startTag % renderAtts(self._atts.items()))
            self._renderContent(collector)
            collector.append(self.__endTag)

    def _render(self, collector):
        if not self._omit:
            self._renderNode(collector)
    
    def __attsGet(self):
        return Attributes(self._atts)
    
    def __attsSet(self, val):
        self._atts = {}
        atts = Attributes(self._atts)
        for name, value in val.items():
            atts[name] = value
    
    atts = property(__attsGet, __attsSet, 
            doc="Get this element's tag attributes.")
    
    def omittags(self):
        """Don't render this element's tag(s)."""
        self.__omitTags = True
    
    def omit(self):
        """Don't render this element."""
        self._omit = True


class Repeater(Container):
    """A Repeater node has a one-to-many relationship with the node that
       contains it.
    """
    
    _nodeType = 'rep'
    
    def __init__(self, nodeName, tagName, atts):
        self._sep = '\n'
        self.__renderedContent = [] # On cloning, shallow-copy this list.
        Container.__init__(self, nodeName, tagName, atts)
        
    _fastClone = Container.copy # performance optimisation
    
    def __len__(self):
        return len(self.__renderedContent) / 2
    
    def copy(self):
        clone = Container.copy(self)
        clone.__renderedContent = self.__renderedContent[:]
        return clone
    
    def _render(self, collector):
        if not self._omit:
            collector.extend(self.__renderedContent[1:])
    
    def add(self, fn, *args):
        """Render an instance of this node."""
        clone = self._fastClone() # performance optimisation
        fn(clone, *args)
        if not clone._omit:
            self.__renderedContent.append(clone._sep)
            clone._renderNode(self.__renderedContent)

    def repeat(self, fn, list, *args):
        """Render an instance of this node for each item in list."""
        for item in list:
            self.add(fn, item, *args)

##

class Attributes:
    """Public facade for modifying a node's tag attributes."""
    
    __attNamePattern = re.compile('^[a-zA-Z_][-.:a-zA-Z_0-9]*$')
    
    def __init__(self, atts):
        self.__atts = atts
    
    def __getitem__(self, name):
        return self.__atts[name]
        
    def __setitem__(self, name, val):
        try:
            if not self.__attNamePattern.match(name): # Note: this 
            # will throw a TypeError if 'name' is not string/unicode.
                raise KeyError, "bad name."
            if val != None:
                if not isinstance(val, basestring):
                    raise TypeError, "bad value: %r" % val
                if '"' in val and "'" in val:
                    raise ValueError, "value %r contains " \
                            "both single and double quotes." % val
            self.__atts[name] = val
        except Exception, e:
            msg = str(e)
            if not isinstance(name, basestring):
                msg = "bad name."
            raise e.__class__, "Can't set tag attribute %r: %s" % (name, msg)
        
    def __delitem__(self, name):
        del self.__atts[name]
    
    def __repr__(self):
        return '<Attributes [%s]>' % renderAtts(self.__atts.items())[1:]
    
    # TO DO: keys(), values(), items() methods


#######

class Content:
    def __init__(self, encoder, decoder):
        self._encode = encoder
        self._decode = decoder
    
    def __iter__(self):
        def makeGen():
            raise StopIteration
            yield None
        return makeGen()


##

class NullContent(Content):
    """Represents an empty HTML element's non-existent content."""
    
    def _renderContent(self, collector):
        pass


class PlainContent(Content):
    """Represents a non-empty HTML element's content where it contains plain 
       text/markup only.
    """
    
    def __init__(self, content, encoder, decoder):
        Content.__init__(self, encoder, decoder)
        self.html = content # Get/Set this element's content as raw markup;
        # use with care.
        
    def _renderContent(self, collector):
        # Called by Node classes to add HTML element's content.
        collector.append(self.html)
    
    def __contentGet(self): 
        return self._decode(self.html)
    
    def __contentSet(self, txt): 
        self.html = self._encode(txt)
    
    text = content = property(__contentGet, __contentSet, 
            doc="Get/Set this element's content as escaped text.")


class RichContent(Content):
    """Represents a non-empty HTML element's content where it contains other 
       Container/Repeater nodes.
    """
    
    __validIdentifierPattern = re.compile('^[a-zA-Z_][a-zA-Z_0-9]*$')
    
    # KLUDGE: The following line keeps Python 2.3 sweet while it instantiates 
    # instances of this class; without it, the process crashes hard as 
    # __init__ conflicts with __setattr__.
    __nodesDict = {}
    
    def __init__(self, content, encoder, decoder):
        Content.__init__(self, encoder, decoder)
        self.__nodesList = content # On cloning, shallow copy this list
        # then clone and replace each node in the list.
        self.__nodesDict = dict(
                [(node._nodeName, node) for node in content[1::2]]) # (On clon-
        # ing: replace with a new dict built from cloned self.__nodesList.)
        
    def __iter__(self):
        def makeGen():
            for i in range(1, len(self.__nodesList), 2):
                yield self.__nodesList[i]
            raise StopIteration
        return makeGen()

    def _initRichClone(self, clone):
        D = clone.__nodesDict = {}
        L = clone.__nodesList = self.__nodesList[:]
        for i in range(1, len(L), 2):
            D[L[i]._nodeName] = L[i] = L[i].copy()
        return clone
    
    def _renderContent(self, collector):
        L = self.__nodesList
        collector.append(L[0])
        for i in range(1, len(L), 2):
            L[i]._render(collector)
            collector.append(L[i + 1])
    
    def __getattr__(self, name):
        try:
            return self.__nodesDict[name]
        except KeyError:
            raise AttributeError , "%s instance has no attribute %r." % (
                    self.__class__.__name__, name)
    
    def __setattr__(self, name, value):
        # Replace a sub-node, or replace node's content.
        if self.__nodesDict.has_key(name):
            if not isinstance(value, Node):
                # Note: This type check is to catch careless user mistakes like
                # 'node.foo = "text"' instead of  'node.foo.val = "text"'
                raise TypeError, ("Can't replace node '%s:%s': value isn't a "
                        "Node object.") % (self.__nodesDict[name]._nodeName,
                         self.__nodesDict[name]._nodeName)
            value = value.copy() 
            value._nodeName = name
            idx = self.__nodesList.index(self.__nodesDict[name])
            self.__nodesDict[name] = self.__nodesList[idx] = value
        elif name == 'text':
            self.__nodesList = [self._encode(value)]
            self.__nodesDict = {}
        elif name == 'html':
            self.__nodesList = [value]
            self.__nodesDict = {}
        else:
            self.__dict__[name] = value
    
    # Allow user to reference elements as node['elementName'] instead of 
    # node.elementName for convenience:
    __getitem__ = __getattr__
    __setitem__ = __setattr__


#######
# Note: Container and Repeater objects are instantiated via the makeNode()
# constructor function. This returns the appropriate class for the content 
# supplied ('abstract factory').
# (The documentation glosses over these differences for simplicity.)

class EmptyContainer(NullContent, Container):
    def __init__(self, nodeName, tagName, atts, content, encoder, decoder):
        NullContent.__init__(self, encoder, decoder)
        Container.__init__(self, nodeName, tagName, atts)


class PlainContainer(PlainContent, Container):
    def __init__(self, nodeName, tagName, atts, content, encoder, decoder):
        PlainContent.__init__(self, content[0], encoder, decoder)
        Container.__init__(self, nodeName, tagName, atts)


class RichContainer(RichContent, Container):
    def __init__(self, nodeName, tagName, atts, content, encoder, decoder):
        RichContent.__init__(self, content, encoder, decoder)
        Container.__init__(self, nodeName, tagName, atts)
        
    def copy(self):
        return self._initRichClone(Container.copy(self))

##

class EmptyRepeater(NullContent, Repeater):
    def __init__(self, nodeName, tagName, atts, content, encoder, decoder):
        NullContent.__init__(self, encoder, decoder)
        Repeater.__init__(self, nodeName, tagName, atts)


class PlainRepeater(PlainContent, Repeater):
    def __init__(self, nodeName, tagName, atts, content, encoder, decoder):
        PlainContent.__init__(self, content[0], encoder, decoder)
        Repeater.__init__(self, nodeName, tagName, atts)


class RichRepeater(RichContent, Repeater):
    def __init__(self, nodeName, tagName, atts, content, encoder, decoder):
        RichContent.__init__(self, content, encoder, decoder)
        Repeater.__init__(self, nodeName, tagName, atts)
        
    def copy(self):
        return self._initRichClone(Repeater.copy(self))
        
    def _fastClone(self): # performance optimisation
        return self._initRichClone(Repeater._fastClone(self))

##

__nodeClasses = {
        'con': {'empty': EmptyContainer, 
                'plain': PlainContainer, 
                'rich': RichContainer},
        'rep': {'empty': EmptyRepeater, 
                'plain': PlainRepeater, 
                'rich': RichRepeater}}

def makeNode(nodeType, nodeName, tagName, atts, content, encoder, decoder):
    return __nodeClasses[nodeType][{0: 'empty', 1: 'plain'}.get(len(content), 
            'rich')](nodeName, tagName, atts, content, encoder, decoder)


#################################################
# MAIN
#################################################

class Template(RichContent, Node):
    """An HTML template object model."""
    
    _nodeType = 'tem'
    _nodeName = ''
    
    def __init__(self, html, attribute='node', 
            codecs=(defaultEncoder, defaultDecoder)):
        """
            html : string or unicode -- the template HTML
            [attribute : string or unicode] -- name of the tag attribute used
                    to hold compiler directives
            [codecs : tuple] -- a tuple containing two functions used by the 
                    content property to encode/decode HTML entities
        """
        parser = Parser(attribute, codecs[0], codecs[1])
        parser.feed(html)
        parser.close()
        RichContent.__init__(self, parser.result(), *codecs)
    
    # Allow Template nodes to replace Container/Repeater nodes
    _render = RichContent._renderContent
    
    def copy(self):
        """Returns a copy of this template."""
        return self._initRichClone(CloneNode(self)) # performance optimisation

