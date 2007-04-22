#!/usr/bin/env python

from html2template import Template


# 1. Define HTML template:

html = """
<html>
	<head>
		<title node="con:title">TITLE</title>
	</head>
	<body>
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

def render(pageTitle, linksInfo):
	"""Renders the template.
		pageTitle : string -- the page title
		linksInfo : list of tuple -- a list of form [(URI, name),...]
		Result : string -- the finished HTML
	"""
	node = template.copy()
	node.title.val = pageTitle
	node.item.repeat(renderItem, linksInfo)
	return node.render()


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
print render(title, links)