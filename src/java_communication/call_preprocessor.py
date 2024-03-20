"""
This module offers the implementation of the functions called by Java. References to other scripts or modules are possible.
 This is due to allow every kind of processing that is implemented in this project. At the end of each function the response_creator will save the response under the
 corresponding message id to the file system so that the response can be read by Java.
"""

import sys
import message_manager
from mlm_doc_parser import *

def process_string(messageId):
    """
    Reads a string from Java adds "from Python" and returns it
    """
    arg = message_manager.readMessageContent(messageId)
    string = arg[0]
    string += ' from Python'
    message_manager.postResponse(messageId,string)
    return

def perform_promotion_process_from_java(messageId):
    print('func is called')
    arg = message_manager.readMessageContent(messageId)
    path = arg[0]
    mlm = MlmDoc(path)
    message_manager.postResponse(messageId,mlm)
    return

def simulate_lost_file(messageId):
    """
        Defined for testing purposes. Simulates the loss of a message from Java
    """
    message_manager.readMessageContent('deadbeef')
    return

def illegal_arguments(messageId):
    """
        Defined for presentation purposes. Shows the developer how to deal with Java arguments, that do not match
        the expectation of Python. If a ValueError is raised on the Java side a catch strategy could be defined.
    """
    args = message_manager.readMessageContent(messageId)
    expected_args = "Baa"
    if args != expected_args:
        print('wrong input')
        raise ValueError("Input args do not match expected args")
    return

