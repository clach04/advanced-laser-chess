#!/usr/bin/env python

from html2template import Template


# 1. Define HTML template:

html = """
<html>
	<head>
		<title node="con:title">TITLE</title>
<style type="text/css">
body.red {
	background-color:rgb(180, 72, 72);
	}
body.green {
	background-color:rgb(72, 180, 72);
	}
</style>
</head>
	<body class="" node="con:body">
		<ul>
			<li node="rep:item">
				<a href="" node="con:link">LINK</a>
			</li>
		</ul>
	</body>
</html>
"""


# 2. Compile the template:

template = Template(html)


# 3. Define functions to control template rendering:

def render_example1(pageTitle, linksInfo, bodyClass):
	"""Renders the template.
		pageTitle : string -- the page title
		linksInfo : list of tuple -- a list of form [(URI, name),...]
		bodyClass: string -- body class name
		Result : string -- the finished HTML
	"""
	node = template.copy()
	topnode = node
	node.title.val = pageTitle
	node.body.atts['class'] = bodyClass
	node = node.body
	node.item.repeat(renderItem, linksInfo)
	return topnode.render()
def render_example2(pageTitle, linksInfo, bodyClass):
	"""Renders the template.
		pageTitle : string -- the page title
		linksInfo : list of tuple -- a list of form [(URI, name),...]
		bodyClass: string -- body class name
		Result : string -- the finished HTML
	"""
	node = template.copy()
	node.title.val = pageTitle
	node.body.atts['class'] = bodyClass
	node.body.item.repeat(renderItem, linksInfo)
	return node.render()

render=render_example2
render=render_example1

def renderItem(node, linkInfo):
	"""Callback function used by render().
		node : Repeater -- the copy of the rep:item node to manipulate
		linkInfo : tuple of string -- a tuple of form: (URI, name)
	"""
	URI, name = linkInfo
	node.link.atts['href'] = URI
	node.link.val = name


# 4. Render template:

title = "Site Map"
links = [('index.html', 'Home'), ('products/index.html', 'Products'), ('about.html', 'About')]
print render(title, links, 'red')