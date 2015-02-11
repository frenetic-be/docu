#!/usr/bin/env python
'''
.. module: docu
.. moduleauthor: Julien Spronck
.. created: Feb 5, 2015

This module is similar to python's pydoc with added flexibility. For example,
the parse function returns a tuple with all dependent modules, variables,
functions, classes and their docstrings. This allows for a complete
customization of the output. Also, the save_as_html() function returns a more
modern html version compared to pydoc, which allows for complete CSS styling.
'''

import re
import sys
from operator import itemgetter
import pkgutil

__version__ = '1.1'

VALID_VAR = "([_A-Za-z][_a-zA-Z0-9]*)"
LEFT_PAR = '\('
RIGHT_PAR = '\)'

class FileTypeError(Exception):
    '''
    A custom exception for handling wrong file types
    '''
    pass

def next_line(lines, jline):
    '''
    Finds the next non-empty line in the file ans strip the comments out.
    Args:
        lines (list of str): the list of lines representing the file to
            document. lines should be the result of file.readlines().
        jline (int): the index at which you wish to start the search
    Returns:
        (str, int): a tuple containing the non-empty line and the index of the
            line after.
    '''
    nlines = len(lines)
    if jline < nlines:
        line = lines[jline]
        jline += 1
    else:
        return '', jline
    ## strip comments
    line = line.split('#')[0].rstrip()
    ## Skip empty lines
    res = re.search('^$', line)
    while res:
        if jline < nlines:
            line = lines[jline]
            jline += 1
        else:
            break
        ## strip comments
        line = line.split('#')[0].rstrip()
        res = re.search('^$', line)
    return line, jline

def get_indent(line):
    '''
    Gets the indentation of a given line (number of spaces).
    Args:
        line (str): the line
    Returns:
        int: length of indentation
    '''
    res = re.search('^( +)[^ ](.*)$', line)
    if res:
        return len(res.group(1))
    return 0

def get_docstring(lines, jline, indent=0, skip_first=True):
    '''
    Gets the next docstring, defined between two sets of three quotes (
    single or double).
    Args:
        lines (list of str): the list of lines representing the file to
            document. lines should be the result of file.readlines().
        jline (int): the index at which you wish to start the search
        indent (int, optional): the indentation at which you are looking for the
            docstring (typically 0, 4, 8, ...). Defaults to 0.
        skip_first (bool, optional): If True, the first line to look is
            lines[jline]. Otherwise, it is lines[jline - 1]. Defaults to True.
    Returns:
        (str, int): a tuple containing the found docstring and the index of the
            line after.
    '''
    out = ''
    nlines = len(lines)
    if not skip_first:
        jline = jline - 1 if jline > 0 else 0
    if jline < nlines:
        line = lines[jline]
        jline += 1
    else:
        return out, jline
    line = line.rstrip()
    res = re.search('^ {'+str(indent)+'}(\'\'\'|\"\"\")(.*?)(\'\'\'|\"\"\")?$',
                    line)
    if res:
        out = res.group(2)
        if res.group(3):
            return out, jline
        if jline < nlines:
            line = lines[jline]
            jline += 1
        else:
            return out, jline
        while 1:
            line = line.rstrip()
            res = re.search('(\'\'\'|\"\"\")$', line)
            if res:
                if line[indent:-3] != '':
                    out += '\n' + line[indent:-3]
                break
            else:
                out += '\n' + line[indent:]
            if jline < nlines:
                line = lines[jline]
                jline += 1
            else:
                break
    return out.strip(), jline

def get_module(line, indent=0):
    '''
    Gets the names of an imported module from a line if the line is of the
    'import' type
    Args:
        line (str): the line
        indent (int, optional): the indentation at which you are looking for the
            docstring (typically 0, 4, 8, ...). Defaults to 0.
    Returns:
        str: name of imported module
    '''
    res = re.search('^ {'+str(indent)+'}import '+
                    '{0} *(as  *{1})?$'.format(VALID_VAR, VALID_VAR), line)
    if res:
        return res.group(1)
    res = re.search('^ {'+str(indent)+'}from '+
                    '{0} *import *.*$'.format(VALID_VAR), line)
    if res:
        return res.group(1)
    return

def get_version(line, indent=0):
    '''
    Gets the version number
    Args:
        line (str): the line
        indent (int, optional): the indentation at which you are looking for the
            docstring (typically 0, 4, 8, ...). Defaults to 0.
    Returns:
        str: version number
    '''
    res = re.search(('^ {'+str(indent)+'}__version__ *= *(\'|\")(.*)'
                     '(\'|\") *$'), line)
    if res:
        return res.group(2)
    return ''

def get_variable(line, indent=0):
    '''
    Gets the names of a global module variable from a line if the line is of
    the 'variable declaration' type
    Args:
        line (str): the line
        indent (int, optional): the indentation at which you are looking for the
            docstring (typically 0, 4, 8, ...). Defaults to 0.
    Returns:
        {'name': str, 'value': obj}: dictionary with the name of the variable
            and its value when originally set.
    '''
    res = re.search('^ {'+str(indent)+'}}{0} *= *(.*)$'.format(VALID_VAR),
                    line)
    if res:
        return {'name':res.group(1),
                'value': res.group(2)}
    return

def get_exception(line):
    '''


    Args:
        line (): .

    Returns:

    Raises:
    '''
    res = re.search('^ *raise (.*)'+LEFT_PAR+'.*'+RIGHT_PAR+'$', line)
    if res:
        return res.group(1)
    return ''

def get_function(lines, jline, indent=0):
    '''
    Returns the function definition if there is one at line lines[jline].
    Args:
        lines (list of str): the list of lines representing the file to
            document. lines should be the result of file.readlines().
        jline (int): the index at which you wish to start the search
        indent (int, optional): the indentation at which you are looking for the
            docstring (typically 0, 4, 8, ...). Defaults to 0.
    Returns:
        {'name': str, 'args': list of str, 'keywords': list of str, 'defaults':
            list of str, 'docstring':str}: dictionary with the name of the
            function, its arguments, keywords with default values and the
            function's docstring.
        int: new jline index.
    '''
    jline = jline - 1 if jline > 0 else 0
    if jline < len(lines):
        line = lines[jline]
        jline += 1
    else:
        return None, jline
    line = line.split('#')[0].rstrip()
    res = re.search('^ {'+str(indent)+'}def '+VALID_VAR+LEFT_PAR+'(.*?)('+RIGHT_PAR+
                    ':)?$', line)
    if res:
        allargs = res.group(2)
        endpar = res.group(3)
        while not endpar:
            if jline < len(lines):
                line = lines[jline]
                jline += 1
            else:
                return None, jline
            line = line.split('#')[0].rstrip()
            res2 = re.search('^ *(.*?)('+RIGHT_PAR+':)?$', line)
            if res2:
                allargs += res2.group(1)
                endpar = res2.group(2)
        ## Function name
        name = res.group(1)
        args = []
        keywords = []
        defaults = []
        exceptions = []
        allargs = allargs.split(',')
        for arg in allargs:
            ## Arguments
            res2 = re.search('^{0}$'.format(VALID_VAR), arg.strip())
            if res2:
                args.append(res2.group(1))
            ## Optional arguments
            res2 = re.search('^{0} *= *(.*)$'.format(VALID_VAR), arg.strip())
            if res2:
                keywords.append(res2.group(1))
                defaults.append(res2.group(2))
        ## Docstring
        line, jline = next_line(lines, jline)
        indent0 = get_indent(line)
        docstring, jline = get_docstring(lines, jline, indent=indent0,
                                         skip_first=False)
        while get_indent(line) >= indent0 and jline < len(lines):
            line, jline = next_line(lines, jline)
            exc = get_exception(line)
            if exc:
                exceptions.append(exc)
        jline -= 1
        return ({'name':name,
                 'args':args,
                 'keywords':keywords,
                 'defaults':defaults,
                 'docstring':docstring,
                 'exceptions':exceptions}, jline)
    return None, jline

def get_class(lines, jline, indent=0):
    '''
    Returns the class definition if there is one at line lines[jline].

    Args:
        lines (list of str): the list of lines representing the file to
            document. lines should be the result of file.readlines().
        jline (int): the index at which you wish to start the search
        indent (int, optional): the indentation at which you are looking for the
            docstring (typically 0, 4, 8, ...). Defaults to 0.
    Returns:
        {'name': str, 'inheritance': str, 'modules':list of str, 'variables':
            list of str, 'functions':list of function dictionaries (see
            get_function()), 'docstring':str}: dictionary with the name of the
            class, its inheritance, its modules, variables, methods and the
            class's docstring.
        int: new jline index.
    '''
    jline = jline - 1 if jline > 0 else 0
    if jline < len(lines):
        line = lines[jline]
        jline += 1
    else:
        return None, jline
    line = line.split('#')[0].rstrip()
    res = re.search('^ {'+str(indent)+'}class ' +
                    VALID_VAR+LEFT_PAR+'(.*)'+RIGHT_PAR+':$', line)
    if res:
        ## Class name and inheritance
        name = res.group(1)
        inheritance = res.group(2)
        modules = []
        variables = []
        functions = []
        ## Docstring
        line, jline = next_line(lines, jline)
        indent = get_indent(line)
        indent0 = indent
        docstring, jline = get_docstring(lines, jline, indent=indent,
                                         skip_first=False)
        while indent >= indent0 and jline < len(lines):
            line, jline = next_line(lines, jline)
            indent = get_indent(line)
            ## Look for imported modules
            module = get_module(line, indent=indent0)
            if module:
                modules.append(module)
                continue
            ## Look for variables
            variable = get_variable(line, indent=indent0)
            if variable:
                variables.append(variable)
                continue
            ## Look for functions
            function, jline = get_function(lines, jline, indent=indent0)
            if function:
                functions.append(function)
                continue
        jline -= 1
        modules = sorted(modules)
        variables = sorted(variables, key=itemgetter('name'))
        functions = sorted(functions, key=itemgetter('name'))
        return ({'name':name,
                 'inheritance':inheritance,
                 'modules':modules,
                 'functions':functions,
                 'variables':variables,
                 'docstring':docstring}, jline)
    return None, jline

def get_help(module_file_name, output=False):
    '''
    Builds the documentation for the module module_file_name, formats it and
    either displays it to screen (output= False) or returns it into a variable
    (output= True)
    Args:
        module_file_name (str): string containing the file or module name
            for which you want to see/get the documentation
        output (bool, optional): if False, prints to screen. If True, returns
            results into variable. Defaults to False.
    Returns:
        If output= True:
            modulename: str with module name,
            str: the string containing the formatted documentation.

    Raises:
    '''

    (modulename, description, version, modules, variables,
     functions, classes) = parse(module_file_name)
    astr = 'NAME'
    astr += '\n' + '    '+modulename+'\n'
    if description != '':
        astr += '\n' + 'DESCRIPTION'
        for line in description.split('\n'):
            astr += '\n' + '    '+line
        astr += '\n' + '\n'
    if version != '':
        astr += '\n' + 'VERSION'
        astr += '\n' + '    '+version
        astr += '\n' + '\n'
    if len(modules) > 0:
        astr += '\n' + 'MODULES'
        astr += '\n' + '    '+'\n    '.join(modules)
        astr += '\n' + '\n'
    if len(variables) > 0:
        astr += '\n' + 'VARIABLES'
        astr += '\n' + '    '+'\n    '.join(val['name'] for val in variables)
        astr += '\n' + '\n'
    if len(functions) > 0:
        astr += '\n' + 'FUNCTIONS\n'
        for fun in functions:
            strarg = ', '.join(fun['args'])
            strkey = ', '.join('{0}={1}'.format(kwd, fun['defaults'][j])
                               for j, kwd in enumerate(fun['keywords']))
            if strarg == '':
                strargs = strkey
            elif strkey == '':
                strargs = strarg
            else:
                strargs = strarg+', '+strkey
            astr += '\n' + '    {0}({1})'.format(fun['name'], strargs)
            for line in fun['docstring'].split('\n'):
                astr += '\n' + '     |  '+line
            astr += '\n'
        astr += '\n' + '\n'
    if len(classes) > 0:
        astr += '\n' + 'CLASSES\n'
        for cla in classes:
            astr += '\n' + '    {0}({1})'.format(cla['name'], cla['inheritance'])
            for line in cla['docstring'].split('\n'):
                astr += '\n' + '     |  '+line
            astr += '\n' + '     |  '
            astr += '\n' + '     |  ' + 'MODULES'
            astr += '\n' + '     |      ' + '\n     |      '.join(cla['modules'])
            astr += '\n' + '     |  '
            astr += '\n' + '     |  ' + 'VARIABLES'
            astr += ('\n' + '     |      ' + '\n     |'
                     '      ').join(val['name'] for val in cla['variables'])
            astr += '\n' + '     |  '
            astr += '\n' + '     |  ' + 'FUNCTIONS'
            astr += '\n' + '     |  '
            for fun in cla['functions']:
                strarg = ', '.join(fun['args'])
                strkey = ', '.join('{0}={1}'.format(kwd, fun['defaults'][j])
                                   for j, kwd in enumerate(fun['keywords']))
                if strarg == '':
                    strargs = strkey
                elif strkey == '':
                    strargs = strarg
                else:
                    strargs = strarg+', '+strkey
                astr += '\n' + '     |      {0}({1})'.format(fun['name'], strargs)
                for line in fun['docstring'].split('\n'):
                    astr += '\n' + '     |       |  '+line
                astr += '\n' + '     |  '
    if output:
        return modulename, astr
    else:
        print astr

def save_as_text(module_file_name, outputfile=None, outputdir=''):
    '''

    Builds the documentation for the module module_file_name, formats it and
    writes it into a text file.
    Args:
        module_file_name (str): string containing the file name for which you
            want to see/get the documentation
        outputfile (str, optional): Name of the file to write the output. If not
            provided, the module name with a .txt extension will be used.
            Defaults to None.
        outputdir (str, optional): The directory where to save the text file.
            Defaults to ''
    Returns:
        no output


    Raises:
        TypeError: wrong file type.
    '''
    import os

    if not isinstance(module_file_name, str):
        raise TypeError("Argument must be a string")

    elif os.path.isdir(module_file_name):
        if module_file_name.endswith(os.path.sep):
            module_file_name = os.path.split(module_file_name)[0]
        pkg = pkgutil.get_loader(module_file_name)
        if not pkg:
            ## If directory, create html files for all python files in the directory
            import glob
            files = glob.glob(os.path.join(module_file_name, '*.py'))
            print ('Not a python module. Making documentation for all .py files'
                   ' in directory ({0} files).').format(len(files))
            for fil in files:
                save_as_text(fil, outputdir=outputdir)
            return

    modulename, astr = get_help(module_file_name, output=True)
    if not outputfile:
        outputfile = modulename + '.txt'
    outputfile = os.path.join(outputdir, outputfile)
    print 'Created text file: '+outputfile
    with open(outputfile, 'w') as the_file:
        the_file.write(astr)

def save_as_html(module_file_name, outputfile=None, outputdir=''):
    '''
    Builds the documentation for the module module_file_name, formats it and
    writes it into an html file.
    Args:
        module_file_name (str): string containing the file name for which you
            want to see/get the documentation. If it is a directory, it will
            build the documentation for all .py files in that directory.
        outputfile (str, optional): Name of the file to write the output. If not
            provided, the module name with a .txt extension will be used.
            Defaults to None.
        outputdir (str, optional): The directory where to save the text file.
            Defaults to ''
    Returns:
        no output

    Raises:
        TypeError: wrong file type.
    '''
    import os

    if not isinstance(module_file_name, str):
        raise TypeError("Argument must be a string")

    elif os.path.isdir(module_file_name):
        if module_file_name.endswith(os.path.sep):
            module_file_name = os.path.split(module_file_name)[0]
        pkg = pkgutil.get_loader(module_file_name)
        if not pkg:
            ## If directory, create html files for all python files in the directory
            import glob
            files = glob.glob(os.path.join(module_file_name, '*.py'))
            print ('Not a python module. Making documentation for all .py files'
                   ' in directory ({0} files).').format(len(files))
            for fil in files:
                save_as_html(fil, outputdir=outputdir)
            return

    (modulename, description, version, modules, variables, functions,
     classes) = parse(module_file_name)
    astr = '<!doctype html>'
    astr += '\n<html>'
    astr += '\n<head>'
    astr += ('\n <link href="http://fonts.googleapis.com/css?family=Open+Sans:300,'
             '400,300italic" rel="stylesheet" type="text/css">')
    astr += '\n <title>Python Documentation: {0}</title>'.format(modulename)
    astr += '\n <link href="docu.css" rel="stylesheet" type="text/css">'
    astr += '\n</head>'
    astr += '\n<body>'
    astr += '\n <div class="back-title">'
    astr += ('\n  <h1 class="title">Python Documentation: '
             '{0}</h1>').format(modulename)
    astr += '\n </div>'
    astr += '\n <div class="back-main">'
    astr += '\n <div class="main">'
    astr += '\n <div class="frame" id="nameframe">'
    astr += '\n  <h4 class="frame-title">module name</h4>'
    astr += '\n  <div class="frame-content">{0}</div>'.format(modulename)
    astr += '\n </div>'
    if version != '':
        astr += '\n <div class="frame" id="nameframe">'
        astr += '\n  <h4 class="frame-title">version</h4>'
        astr += '\n  <div class="frame-content">{0}</div>'.format(version)
        astr += '\n </div>'
    if description != '':
        astr += '\n <div class="frame" id="descriptionframe">'
        astr += '\n  <h4 class="frame-title">DESCRIPTION</h4>'
        astr += ('\n  <pre class="frame-content">'
                 '{0}</pre>').format('</br>'.join(description.split('\n')))
        astr += '\n </div>'
    if len(modules):
        astr += '\n <div class="frame" id="modulesframe">'
        astr += '\n  <h4 class="frame-title">dependent modules</h4>'
        astr += '\n  <div class="frame-content">'
        astr += '\n   <ul class="modules">'
        for module in modules:
            if os.path.exists(os.path.join(outputdir, module+'.html')):
                astr += ('\n    <li class="modules"><a href="{0}" '
                         'class="module">{1}</a></li>').format(module+'.html', module)
            else:
                astr += '\n    <li class="modules">{0}</li>'.format(module)
        astr += '\n   </ul>'
        astr += '\n  </div>'
        astr += '\n </div>'
    if len(variables):
        astr += '\n <div class="frame" id="variablesframe">'
        astr += '\n  <h4 class="frame-title">variables</h4>'
        astr += '\n  <div class="frame-content">'
        astr += '\n   <ul class="variables">'
        for val in variables:
            astr += '\n    <li class="variables">{0}</li>'.format(val['name'])
        astr += '\n   </ul>'
        astr += '\n  </div>'
        astr += '\n </div>'
    if len(functions):
        astr += '\n <div class="frame" id="functionsframe">'
        astr += '\n  <h4 class="frame-title">functions</h4>'
        astr += '\n  <div class="frame-content">'
        astr += '\n   <ul class="functions">'
        for function in functions:
            strarg = ', '.join('<span class="function-args">{0}</span>'.format(val)
                               for val in function['args'])
            strkey = ', '.join(('<span class="function-kw">{0}</span>=<span '
                                'class="function-kwdef">{1}'
                                '</span>').format(kwd, function['defaults'][j])
                               for j, kwd in enumerate(function['keywords']))
            if strarg == '':
                strargs = strkey
            elif strkey == '':
                strargs = strarg
            else:
                strargs = strarg+', '+strkey
            astr += '\n    <li class="functions">'
            astr += '\n     <div class="function">'
            astr += ('\n      <div class="function-name"><span class="function-'
                     'name">{0}</span>({1})</div>').format(function['name'], strargs)
            astr += ('\n      <pre class="function-docstring">'
                     '{0}</pre>').format('</br>'.join(function['docstring'].split('\n')))
            astr += '\n     </div>'
            astr += '\n    </li>'
        astr += '\n   </ul>'
        astr += '\n  </div>'
        astr += '\n </div> '
    if len(classes):
        astr += '\n <div class="frame" id="classesframe">'
        astr += '\n  <h4 class="frame-title">classes</h4>'
        astr += '\n  <div class="frame-content">'
        astr += '\n   <ul class="classes">'
        for cla in classes:
            astr += '\n    <li class="classes">'
            astr += '\n     <div class="class">'
            astr += ('\n      <div class="class-name"><span class="class-name">{0}'
                     '</span>(<span class="class-arg">{1}</span>)'
                     '</div>').format(cla['name'], cla['inheritance'])
            astr += '\n       <div class="class-main">'
            astr += '\n      <pre class="class-docstring">{0}</pre>'.format(
                cla['docstring'])
            if len(cla['modules']):
                astr += '\n      <div class="class-modules">'
                astr += '\n       <h5 class="class-title">modules</h5>'
                astr += '\n       <div class="class-content">'
                astr += '\n        <ul class="class-modules">'
                for module in cla['modules']:
                    astr += '\n         <li class="class-modules">{0}</li>'.format(module)
                astr += '\n        </ul>'
                astr += '\n       </div>'
                astr += '\n      </div>'
            if len(cla['variables']):
                astr += '\n      <div class="class-variables">'
                astr += '\n       <h5 class="class-title">variables</h5>'
                astr += '\n       <div class="class-content">'
                astr += '\n        <ul class="class-variables">'
                for val in cla['variables']:
                    astr += ('\n         <li class="class-variables">'
                             '{0}</li>').format(val['name'])
                astr += '\n        </ul>'
                astr += '\n       </div>'
                astr += '\n      </div>'
            if len(cla['functions']):
                astr += '\n      <div class="class-functions">'
                astr += '\n       <h5 class="class-title">methods</h5>'
                astr += '\n       <div class="class-content">'
                astr += '\n        <ul class="class-functions">'
                for function in cla['functions']:
                    strarg = ', '.join('<span class="function-args">' + val +
                                       '</span>' for val in function['args'] if val != 'self')
                    strkey = ', '.join(('<span class="function-kw">{0}</span>='
                                        '<span class="function-kwdef">{1}'
                                        '</span>').format(kwd, function['defaults'][j])
                                       for j, kwd in enumerate(function['keywords']))
                    if strarg == '':
                        strargs = strkey
                    elif strkey == '':
                        strargs = strarg
                    else:
                        strargs = strarg+', '+strkey
                    astr += '\n    <li class="class-functions">'
                    astr += '\n     <div class="class-function">'
                    astr += ('\n      <div class="class-function-name"><span '
                             'class="class-function-name">{0}</span>({1})'
                             '</div>').format(function['name'], strargs)
                    the_docstr = '</br>'.join(function['docstring'].split('\n'))
                    astr += ('\n      <pre class="class-function-docstring">{0}'
                             '</pre>').format(the_docstr)
                    astr += '\n     </div>'
                    astr += '\n    </li>'
                astr += '\n        </ul>'
                astr += '\n       </div> '
                astr += '\n      </div>'
            astr += '\n     </div>'
            astr += '\n     </div>'
            astr += '\n    </li>'
        astr += '\n   </ul>'
        astr += '\n  </div>'
        astr += '\n </div>'
        astr += '\n <div class="credits">This page was made with '
        astr += '<a href="">docu {0}</a>'.format(__version__)
        astr += '\n </div>'
        astr += '\n </div>'
        astr += '\n </div>'

    astr += '\n</body>'
    astr += '\n</html>'
    if not outputfile:
        outputfile = modulename + '.html'
    outputfile = os.path.join(outputdir, outputfile)
    print 'Created html file: '+outputfile
    with open(outputfile, 'w') as the_file:
        the_file.write(astr)

def parse(module_file_name):
    '''
    Reads the module module_file_name and parses it to figure out the
    modulename, the module description, the module version, the dependent
    modules, the global variables, the functions and the class.

    Args:
        module_file_name (str): string containing the file name for which you
            want to see/get the documentation
    Returns:
        modulename (str), description (str), version (str), modules (list of
            str), variables (list of variable dictionnaries), functions
            (list of function dictionnaries) and classes (list of class
            dictionnaries)

    Raises:
        FileTypeError: wrong file type.
        IOError: Module could not be loaded
        TypeError: Argument must be a string.
    '''
    import os

    if not isinstance(module_file_name, str):
        raise TypeError("Argument must be a string")

    mname, extension = os.path.splitext(os.path.basename(module_file_name))

    if extension == '':
        if module_file_name.endswith(os.path.sep):
            module_file_name = os.path.split(module_file_name)[0]
        pkg = pkgutil.get_loader(module_file_name)
        if not pkg:
            raise IOError('Module '+module_file_name+' could not be loaded')
        modulename = pkg.fullname
        module_file_name = pkg.filename
        if not module_file_name.endswith('.py'):
            module_file_name = os.path.join(pkg.filename, '__init__.py')

    elif extension == '.pyc':
        module_file_name = module_file_name[:-1]
        modulename = mname
    elif extension != '.py':
        raise FileTypeError("Wrong file type. This function can only handle "
                            "python files ('.py') or python modules.")
    else:
        modulename = mname

    modules = []
    variables = []
    functions = []
    classes = []
    version = ''
    with open(module_file_name, 'r') as the_file:
        lines = the_file.readlines()
    nlines = len(lines)
    jline = 0
    line, jline = next_line(lines, jline)
    description, jline = get_docstring(lines, jline, skip_first=False)
    while jline < nlines:
        line, jline = next_line(lines, jline)
        ## Look for imported modules
        module = get_module(line)
        if module:
            modules.append(module)
            continue
        ## Look for version number
        vers = get_version(line)
        if vers:
            version = vers
            continue
        ## Look for variables
        variable = get_variable(line)
        if variable:
            variables.append(variable)
            continue
        ## Look for functions
        function, jline = get_function(lines, jline)
        if function:
            functions.append(function)
            continue
        ## Look for classes
        cla, jline = get_class(lines, jline)
        if cla:
            classes.append(cla)
            continue
    modules = sorted(modules)
    variables = sorted(variables, key=itemgetter('name'))
    functions = sorted(functions, key=itemgetter('name'))
    classes = sorted(classes, key=itemgetter('name'))
    return (modulename, description, version, modules, variables, functions,
            classes)

def add_missing_docstring(module_file_name):
    '''


    Args:
        module_file_name (): .

    Returns:

    Raises:
    '''
    with open(module_file_name, 'r') as the_file:
        lines = the_file.readlines()
    nlines = len(lines)
    jline = 0
    while jline < nlines:
        line, jline = next_line(lines, jline)
        indent = get_indent(line)
        ## Look for functions
        current_jl = jline
        # bug here with multiple lines => current_jl is wrong => docstring insert at wrong position
        function, jline = get_function(lines, jline, indent=indent)
        if function:
            someline = lines[current_jl - 1]
            someline = someline.split('#')[0].rstrip()
            res = re.search('^.*?'+RIGHT_PAR+':$', someline)
            while not res:
                current_jl += 1
                someline = lines[current_jl - 1]
                someline = someline.split('#')[0].rstrip()
                res = re.search('^.*?'+RIGHT_PAR+':$', someline)
            docstring = make_function_docstring(function, indent=indent,
                                                verbose=False)
            if docstring:
                docstrarr = [val+'\n' for val in docstring.split('\n')]
                lines = lines[:current_jl] + docstrarr + lines[current_jl:]
                jline += len(docstrarr)-1
                nlines += len(docstrarr)
    with open(module_file_name, 'w') as the_file:
        the_file.writelines(lines)

def make_function_docstring(func, indent=0, verbose=True):
    '''


    Args:
        func (): .
        indent (, optional): . Defaults to 0.
        verbose (, optional): . Defaults to True.

    Returns:

    Raises:
    '''
    if func['docstring'] != '':
        if verbose:
            print ('Warning: the function "'+func['name']+
                   '" already has a docstring')
        return ''
    wspace = ''.join([' ']*(indent+4))
    astr = wspace+"'''"
    astr += '\n\n'
    astr += '\n'+wspace+'Args:'
    for arg in func['args']:
        if arg != 'self':
            astr += '\n'+wspace+'    {0} (): .'.format(arg)
    for kwd, default in zip(func['keywords'], func['defaults']):
        astr += '\n'+wspace+('    {0} (, optional): . '
                             'Defaults to {1}.').format(kwd, default)
    astr += '\n'
    astr += '\n'+wspace+'Returns:'
    astr += '\n'
    astr += '\n'+wspace+'Raises:'
    for exc in func['exceptions']:
        astr += '\n'+wspace+'    {0}'.format(exc)
    astr += '\n'+wspace+"'''"
    return astr

def prepare_docstring(module_file_name, function_name):
    '''
    Helps preparing a function/method's docstring
    Args:
        module_file_name (str): string containing the file name for which you
            want to see/get the documentation.
        function_name (str): string containing the function/method name.
    Returns:
    Raises:
        ValueError
    '''
    (_, _, _, _, _, functions, classes) = parse(module_file_name)
    for function in functions:
        if function_name == function['name']:
            print make_function_docstring(function)
            return
    for cla in classes:
        for function in cla['functions']:
            if function_name == function['name']:
                print make_function_docstring(function)
                return
    raise ValueError('Function "'+function_name+'" not found in '+module_file_name)
##########################
if __name__ == '__main__':

    def usage(exit_status):
        '''


        Args:
            exit_status (): .

        Returns:

        Raises:
        '''
        msg = "Usage: mypydoc.py module_file_name [OPTIONS]\n"
        msg += "Creates documentation for a python module.\n"
        print msg
        sys.exit(exit_status)

    import getopt
   # parse command line options/arguments
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "htd:", ["html", "text",
                                                          "directory="])
    except getopt.GetoptError:
        usage(2)
    OUTPUT = 'screen'
    DIR = ''
    for o, argument in OPTS:
        if o in ("-d", "--directory"):
            DIR = argument
        if o in ("-t", "--text"):
            OUTPUT = 'text'
        if o in ("-h", "--html"):
            OUTPUT = 'html'
    MODULE = ARGS[0]
    if OUTPUT == 'screen':
        get_help(MODULE)
    elif OUTPUT == 'html':
        save_as_html(MODULE, outputdir=DIR)
    elif OUTPUT == 'text':
        save_as_text(MODULE, outputdir=DIR)
