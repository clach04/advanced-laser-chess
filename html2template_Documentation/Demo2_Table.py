#!/usr/bin/env python

# Demonstrates how to:
# - duplicate the original Template object, preserving the original for future reuse
# - generate multiple table rows
# - assign strings as HTML elements' content
# - assign strings to tag attributes
# - render the template.

from html2template import Template

#################################################
# TEMPLATE
#################################################


html = '''<html>
	<head>
		<title node="con:title">TITLE</title>
	</head>
	<body>
	
		<table>
			<tr node="rep:client">
				<td node="con:name">Surname, Firstname</td>
				<td><a node="con:email" href="mailto:client@email.com">client@email.com</a></td>
			</tr>
		</table>
	
	</body>
</html>'''

template = Template(html)

def render(title, clients):
	node = template.copy()
	node.title.val = title
	node.client.repeat(renderClient, clients)
	return node.render()

def renderClient(node, client):
	node.name.val = client.surname + ', ' + client.firstname
	node.email.atts['href'] = 'mailto:' + client.email
	node.email.val =  client.email


#################################################
# MAIN
#################################################

class Client:
	def __init__(self, *args):
		self.surname, self.firstname, self.email = args

title = 'FooCo'
clients = [Client('Smith', 'K', 'ks@foo.com'), Client('Jones', 'T', 'tj@bar.org')]

print render(title, clients)