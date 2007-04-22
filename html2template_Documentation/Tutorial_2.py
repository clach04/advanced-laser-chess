#!/usr/bin/env python

from html2template import Template

html = """
<div node="rep:section">
	<h2 node="con:title">section title</h2>
	<p node="con:desc">section description</p>
</div>
"""

template  = Template(html)

def render(sections):
	node = template.copy()
	node.section.repeat(renderSection, sections)
	return node.render()


def renderSection(node, section):
	node.title.val, node.desc.val = section


sections = [('title 1', 'description 1'), ('title 2', 'description 2'), ('title 3', 'description 3')]
print render(sections)