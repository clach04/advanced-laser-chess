#!/usr/bin/python

"""
Example usage of render functions.

This text is loosely modeled on Tutorial_1.py
"""

# Version 2 of HTMLTemplate - from http://freespace.virgin.net/hamish.sanderson/htmltemplate.html
import html2template
import render_helpers

# 1. Define HTML template:

nested_repeat_html = """
<html>
    <head>
        <title node="con:title">TITLE</title>
    </head>
    <body>
        <ul>
            <li node="rep:item">
            <span node="rep:bogus_item">
                <p node="-con:list_item">list item</p>
            </span>
            </li>
        </ul>
    </body>
</html>
"""


html = """
<html>
    <head>
        <title node="con:title">TITLE</title>
    </head>
    <body>
        <p node="con:unused_text">this is unused and will not be updated</p>
        
        <ul>
            <li node="rep:item">
                <p node="-con:list_item">list item</p>
            </li>
        </ul>
    </body>
</html>
"""

table_html = """
<html> 
    <head>
        <title node="con:title">TITLE</title>
    </head>

    <body> 
    
    <table>
        <thead>
            <tr>
                <span node="-rep:table_header"><th node="con:col_title">title of column</th></span>
            </tr>
        </thead>
        <tbody>
            <tr node="rep:table_rows">
                <span node="-rep:table_cols"><td node="con:table_col">cell info</td></span>
            </tr>
        </tbody>
    </table>
    
    </body> 
</html> 
"""

# 2. Define functions to control template rendering:

# Step 2. in Tutorial_1.py is not required when using auto-render functions
# .. skip and import :-)


# 3. Compile template:

template = html2template.Template(html) ## render_helpers.renderTemplateFromKeywords
test_error_template1 = html2template.Template(html) ## render_helpers.renderTemplateFromKeywordsRequireAll
test_error_template2 = html2template.Template(nested_repeat_html) ## render_helpers.renderTemplateFromKeywordsRequireAll

table_template = html2template.Template(table_html) # render_helpers.renderTemplateFromKeywords

# 4. Render template:

title = "Ingredients"
mylist = ['Fish', 'Peas', 'Slime']
mylist_bad = [('index.html', 'Home'), ('products/index.html', 'Products'), ('about.html', 'About')] ## check repeating error handler

print 'First Test - do not pass in repating list (do not require all nodes to be populated)'
print '--------------------------------------'
print render_helpers.renderTemplateFromKeywords(template, title=title)
print '--------------------------------------'
print 'Second Test - pass in repating list (do not require all nodes to be populated)'
print '--------------------------------------'
print render_helpers.renderTemplateFromKeywords(template, title=title, item=mylist)
print '--------------------------------------'
print 'Third Test - pass in dictionary'
print '--------------------------------------'
temp_dict = {'title':title, 'item':mylist}
print render_helpers.renderTemplateFromKeywords(template, **temp_dict)
print '--------------------------------------'

try:
    print ''
    print 'pass in variable that does not exist in template'
    print render_helpers.renderTemplateFromKeywords(template, title=title, item=mylist, does_not_exist='pants')
except AttributeError, info:
    print AttributeError, info

try:
    print ''
    print 'pass in tuples/list/container instead of strings'
    print render_helpers.renderTemplateFromKeywords(template, title=title, item=mylist_bad)
except AssertionError, info:
    print AssertionError, info

try:
    print ''
    print 'enforce template must be filled in'
    print render_helpers.renderTemplateFromKeywordsRequireAll(test_error_template1, title=title, item=mylist)
except AttributeError, info:
    print AttributeError, info

#~ try:
#~      print ''
#~      print test_error_template2.render(title=title, item=mylist)
#~ except NotImplementedError, info:
#~      print NotImplementedError, info


table_header = ['Quantity', 'Ingredient']
table_rows = [('1 Kilogram', 'Fish'), ('half a cup', 'Peas')]
print ''
print render_helpers.renderTemplateFromKeywords(table_template, title=title, table_header=table_header, table_rows = table_rows)

