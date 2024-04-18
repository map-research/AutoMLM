"""
This script is called by Java. The first argument will define the name of the function that should be called in Python.
The second argument is the message id. This id is used to load a file from the file system. The name of the file is the
message id.
The function params for the called function are inside this file.
This script will call functions from the call_preprocessor module. There are functions defined that prepared and
processes the Java data.
"""

import sys
import call_preprocessor

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("This script only expects two params. The first param is the referenced function name and "
                        "the second is the message id")
        sys.exit(1)

    function_name = sys.argv[1]
    message_id = sys.argv[2]

    #String is send via ErrorStream to Java and logged there
    log = ("Python received call for function '{}' with id '{}'".format(function_name, message_id))
    print(log, file=sys.stderr)

    if function_name == "process_string":
        call_preprocessor.process_string(sys.argv[2])

    elif function_name == "simulate_lost_file":
        call_preprocessor.simulate_lost_file(sys.argv[2])

    elif function_name == "illegal_arguments":
        call_preprocessor.illegal_arguments(sys.argv[2])
    
    elif function_name == "perform_promotion_process_from_java":
        call_preprocessor.perform_promotion_process_from_java(sys.argv[2])

    elif function_name == "import_XML":
        call_preprocessor.import_XML(sys.argv[2])

    else:
        raise AttributeError("Called Python function unknown!")
