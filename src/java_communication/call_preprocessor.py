"""
This module offers the implementation of the functions called by Java. References to other scripts or modules are possible.
 This is due to allow every kind of processing that is implemented in this project. At the end of each function the response_creator will save the response under the
 corresponding message id to the file system so that the response can be read by Java.
"""

import sys
import message_manager
from mlm_doc_parser import *
from xml.dom.minidom import parse

# performs the promotion process when called from java
def perform_promotion_process_from_java(messageId):
    arg = message_manager.readMessageContent(messageId)
    path = arg[0]
    mlm = MlmDoc(path)
    message_manager.postResponse(messageId,mlm)
    return

def import_XML(messageId):

    path = "C:\\Users\\fhend\\Documents\\GitHub_Repos\\MosaicFX\\AutoMLM\\src\\Java_communication\\dummy.xml"
    message_manager.postResponse(messageId, path)
    return