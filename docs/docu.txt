NAME
    docu

DESCRIPTION
    .. module: docu
    .. moduleauthor: Julien Spronck
    .. created: Feb 5, 2015
    
    This module is similar to python's pydoc with added flexibility. For example,
    the parse function returns a tuple with all dependent modules, variables,
    functions, classes and their docstrings. This allows for a complete
    customization of the output. Also, the save_as_html() function returns a more
    modern html version compared to pydoc, which allows for complete CSS styling.


VERSION
    1.1


MODULES
    operator
    pkgutil
    re
    sys


VARIABLES
    LEFT_PAR
    RIGHT_PAR
    VALID_VAR


FUNCTIONS

    add_missing_docstring(module_file_name)
     |  Args:
     |      module_file_name (): .
     |  
     |  Returns:
     |  
     |  Raises:

    get_class(lines, jline, indent=0)
     |  Returns the class definition if there is one at line lines[jline].
     |  
     |  Args:
     |      lines (list of str): the list of lines representing the file to
     |          document. lines should be the result of file.readlines().
     |      jline (int): the index at which you wish to start the search
     |      indent (int, optional): the indentation at which you are looking for the
     |          docstring (typically 0, 4, 8, ...). Defaults to 0.
     |  Returns:
     |      {'name': str, 'inheritance': str, 'modules':list of str, 'variables':
     |          list of str, 'functions':list of function dictionaries (see
     |          get_function()), 'docstring':str}: dictionary with the name of the
     |          class, its inheritance, its modules, variables, methods and the
     |          class's docstring.
     |      int: new jline index.

    get_docstring(lines, jline, indent=0, skip_first=True)
     |  Gets the next docstring, defined between two sets of three quotes (
     |  single or double).
     |  Args:
     |      lines (list of str): the list of lines representing the file to
     |          document. lines should be the result of file.readlines().
     |      jline (int): the index at which you wish to start the search
     |      indent (int, optional): the indentation at which you are looking for the
     |          docstring (typically 0, 4, 8, ...). Defaults to 0.
     |      skip_first (bool, optional): If True, the first line to look is
     |          lines[jline]. Otherwise, it is lines[jline - 1]. Defaults to True.
     |  Returns:
     |      (str, int): a tuple containing the found docstring and the index of the
     |          line after.

    get_exception(line)
     |  Args:
     |      line (): .
     |  
     |  Returns:
     |  
     |  Raises:

    get_function(lines, jline, indent=0)
     |  Returns the function definition if there is one at line lines[jline].
     |  Args:
     |      lines (list of str): the list of lines representing the file to
     |          document. lines should be the result of file.readlines().
     |      jline (int): the index at which you wish to start the search
     |      indent (int, optional): the indentation at which you are looking for the
     |          docstring (typically 0, 4, 8, ...). Defaults to 0.
     |  Returns:
     |      {'name': str, 'args': list of str, 'keywords': list of str, 'defaults':
     |          list of str, 'docstring':str}: dictionary with the name of the
     |          function, its arguments, keywords with default values and the
     |          function's docstring.
     |      int: new jline index.

    get_help(module_file_name, output=False)
     |  Builds the documentation for the module module_file_name, formats it and
     |  either displays it to screen (output= False) or returns it into a variable
     |  (output= True)
     |  Args:
     |      module_file_name (str): string containing the file or module name
     |          for which you want to see/get the documentation
     |      output (bool, optional): if False, prints to screen. If True, returns
     |          results into variable. Defaults to False.
     |  Returns:
     |      If output= True:
     |          modulename: str with module name,
     |          str: the string containing the formatted documentation.
     |  
     |  Raises:

    get_indent(line)
     |  Gets the indentation of a given line (number of spaces).
     |  Args:
     |      line (str): the line
     |  Returns:
     |      int: length of indentation

    get_module(line, indent=0)
     |  Gets the names of an imported module from a line if the line is of the
     |  'import' type
     |  Args:
     |      line (str): the line
     |      indent (int, optional): the indentation at which you are looking for the
     |          docstring (typically 0, 4, 8, ...). Defaults to 0.
     |  Returns:
     |      str: name of imported module

    get_variable(line, indent=0)
     |  Gets the names of a global module variable from a line if the line is of
     |  the 'variable declaration' type
     |  Args:
     |      line (str): the line
     |      indent (int, optional): the indentation at which you are looking for the
     |          docstring (typically 0, 4, 8, ...). Defaults to 0.
     |  Returns:
     |      {'name': str, 'value': obj}: dictionary with the name of the variable
     |          and its value when originally set.

    get_version(line, indent=0)
     |  Gets the version number
     |  Args:
     |      line (str): the line
     |      indent (int, optional): the indentation at which you are looking for the
     |          docstring (typically 0, 4, 8, ...). Defaults to 0.
     |  Returns:
     |      str: version number

    make_function_docstring(func, indent=0, verbose=True)
     |  Args:
     |      func (): .
     |      indent (, optional): . Defaults to 0.
     |      verbose (, optional): . Defaults to True.
     |  
     |  Returns:
     |  
     |  Raises:

    next_line(lines, jline)
     |  Finds the next non-empty line in the file ans strip the comments out.
     |  Args:
     |      lines (list of str): the list of lines representing the file to
     |          document. lines should be the result of file.readlines().
     |      jline (int): the index at which you wish to start the search
     |  Returns:
     |      (str, int): a tuple containing the non-empty line and the index of the
     |          line after.

    parse(module_file_name)
     |  Reads the module module_file_name and parses it to figure out the
     |  modulename, the module description, the module version, the dependent
     |  modules, the global variables, the functions and the class.
     |  
     |  Args:
     |      module_file_name (str): string containing the file name for which you
     |          want to see/get the documentation
     |  Returns:
     |      modulename (str), description (str), version (str), modules (list of
     |          str), variables (list of variable dictionnaries), functions
     |          (list of function dictionnaries) and classes (list of class
     |          dictionnaries)
     |  
     |  Raises:
     |      FileTypeError: wrong file type.
     |      IOError: Module could not be loaded
     |      TypeError: Argument must be a string.

    prepare_docstring(module_file_name, function_name)
     |  Helps preparing a function/method's docstring
     |  Args:
     |      module_file_name (str): string containing the file name for which you
     |          want to see/get the documentation.
     |      function_name (str): string containing the function/method name.
     |  Returns:
     |  Raises:
     |      ValueError

    save_as_html(module_file_name, outputfile=None, outputdir='')
     |  Builds the documentation for the module module_file_name, formats it and
     |  writes it into an html file.
     |  Args:
     |      module_file_name (str): string containing the file name for which you
     |          want to see/get the documentation. If it is a directory, it will
     |          build the documentation for all .py files in that directory.
     |      outputfile (str, optional): Name of the file to write the output. If not
     |          provided, the module name with a .txt extension will be used.
     |          Defaults to None.
     |      outputdir (str, optional): The directory where to save the text file.
     |          Defaults to ''
     |  Returns:
     |      no output
     |  
     |  Raises:
     |      TypeError: wrong file type.

    save_as_text(module_file_name, outputfile=None, outputdir='')
     |  Builds the documentation for the module module_file_name, formats it and
     |  writes it into a text file.
     |  Args:
     |      module_file_name (str): string containing the file name for which you
     |          want to see/get the documentation
     |      outputfile (str, optional): Name of the file to write the output. If not
     |          provided, the module name with a .txt extension will be used.
     |          Defaults to None.
     |      outputdir (str, optional): The directory where to save the text file.
     |          Defaults to ''
     |  Returns:
     |      no output
     |  
     |  
     |  Raises:
     |      TypeError: wrong file type.



CLASSES

    FileTypeError(Exception)
     |  A custom exception for handling wrong file types
     |  
     |  MODULES
     |      
     |  
     |  VARIABLES
     |  
     |  FUNCTIONS
     |  