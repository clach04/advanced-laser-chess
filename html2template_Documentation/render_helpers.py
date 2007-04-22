#!/usr/bin/python
"""Helper render functions for HTMLTemplate.
Very limited in what they can do BUT they can save writting lots of
boiler plate code for basic/simple templates

Future ideas:
   *    Add support for dictionaries as input
   *    Add support for classes (or any object with attributes)
   *    Nested repeating items
"""

from types import StringType, UnicodeType

# Version 2 of HTMLTemplate - from http://freespace.virgin.net/hamish.sanderson/htmltemplate.html
import html2template

'''
Note render functions below are generic, they canhandle general cases without
the need for specific code to handle each and every template. This easy of use
comes at the price of flexibility. There is no support for:

    *   attributes
    *   complex repeating container (i.e. comple Repeaters)
    *   classes/objects with attributes (I have one in the works)
    *   dictionaries as variables (use **kwargs as workaround)
    *   nested nodes, i.e. all nodes must be in top level of DOM (support could be added though)
   
But what you do get is:

    *   no need to write any render code :-)
    *   support for keywords. ala Genshi/Kid
    *   optional - enforce all fields in template get filled in
    *   dictionary support via **kwargs, e.g.:
            renderTemplateFromKeywords(template, **temp_dict)
            TODO add renderDict() function that performs "**" re-write?

'''


## NOTE all render functions take in "*args" but they are never used
## only there for future proofing, good style for call back functions
def renderTemplateFromKeywordsMain(template, require_all=False, *args, **kwargs):
    """Simple render function that takes in keywords, e.g.: 
            ...render(title='one', username='fred',...)
            
    Finds/updates the template variables with the same name.
    I.e. based in keyword parameters that come in, 
    update those values in the template.
    
    if require_all is False:
        The keywords drive the template, not the variables in the template.
        If keywords are ommitted, the template is rendered with original
        content in template
    if require_all is False:
        The variables in the template drive the template, not the keywords
        If keywords are ommitted; exception AttributeError is raised
    
    """
    assert len(args) == 0, 'Only keyword parameters allowed'
    tem = template.copy()
    #print tem.structure()
    template_markers = tem._RichContent__nodesDict
    if require_all:
        driving_dictionary = template_markers
    else:
        driving_dictionary = kwargs
    for template_variable_name in driving_dictionary:
        template_variable = getattr(tem, template_variable_name)
        # is template_variable a normal (singleton) value?
        if isinstance(template_variable, html2template.Repeater):
            # we have a Repeater node (repeating item)
            repeating_value = kwargs[template_variable_name]
            render_repeating_item = renderSingleSimpleRepeatingItem
            render_repeating_item = renderSingleNestedSimpleRepeatingItem
            if isinstance(repeating_value, StringType) or isinstance(repeating_value, UnicodeType):
                raise NotImplementedError, 'Repeating Item %r found in %r, but strings passed in not sequence/list/tuples/etc.' % (template_variable_name, tem._nodeName)
            else:
                template_variable.repeat(render_repeating_item, \
                                            repeating_value)
        else:
            # we (hopefully) have a Container node (simple string value)
            try:
                # TODO use "new" .text attribute
                ##setattr(template_variable, 'content', kwargs[template_variable_name])
                #template_variable.content = kwargs[template_variable_name]
                template_variable.text = kwargs[template_variable_name]
            except KeyError, info:
                if require_all:
                    raise AttributeError, \
                        "%s has attribute %r but no variable passed in." % \
                        (tem.__class__.__name__, template_variable_name)
                else:
                    # raise original
                    raise KeyError, info
    return tem.render()

def renderTemplateFromKeywords(tem, *args, **kwargs):
    """Default simple renderer - requires keywords be passed in 
    to indentify variable names in template. E.g.:
        xyz.render(title='one', username='fred',...)
    """
    return renderTemplateFromKeywordsMain(tem, require_all=False, *args, **kwargs)
    
def renderTemplateFromKeywordsRequireAll(tem, *args, **kwargs):
    """Simple renderer - requires keywords be passed in 
    to indentify variable names in template. E.g.:
        xyz.render(title='one', username='fred',...)
    If a template has a variable name that is not passed in via keywords,
    AttributeError exception is raised
    """
    return renderTemplateFromKeywordsMain(tem, True, *args, **kwargs)


def renderSingleSimpleRepeatingItem(item, repeating_value):
    """Default render repeating items, only works for string values
    (single byte or Unicode).
    """
    template_markers = item._RichContent__nodesDict
    assert isinstance(repeating_value, StringType) \
        or isinstance(repeating_value, UnicodeType), \
        'Only support (unicode) strings, not %s' % type(repeating_value)
    assert len(template_markers) == 1, 'Only supports SINGLE repeating values'
    
    # dumb get first (and only!) key - must be a better way
    template_variable_name = template_markers.keys()[0]
    
    template_variable = getattr(item, template_variable_name)
    if isinstance(template_variable, html2template.Repeater):
        raise NotImplementedError, \
        '(Nested) Repeating Items are not supported. Repeating Item %r not allowed in Repeating Item %r' % (template_variable_name, item._nodeName)
        # wip idea.... repeat if repeating_value is not a string of some kind
        #    template_variable.repeat(renderSingleSimpleRepeatingItem, kwargs[template_variable_name])
    else:
        #template_variable.content = repeating_value
        template_variable.text = repeating_value

def renderSingleNestedSimpleRepeatingItem(item, repeating_value):
    """Default render repeating items, only works for string values
    (single byte or Unicode).
    """
    template_markers = item._RichContent__nodesDict
    assert len(template_markers) == 1, 'Only supports SINGLE repeating values'
    
    # dumb get first (and only!) key - must be a better way
    template_variable_name = template_markers.keys()[0]
    
    template_variable = getattr(item, template_variable_name)
    if isinstance(template_variable, html2template.Repeater):
        template_variable.repeat(renderSingleSimpleRepeatingItem, repeating_value)
    else:
        assert isinstance(repeating_value, StringType) \
            or isinstance(repeating_value, UnicodeType), \
            'Only support (unicode) strings, not %s' % type(repeating_value)
        template_variable.content = repeating_value
