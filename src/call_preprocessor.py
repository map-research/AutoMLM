"""
This module offers the implementation of the functions called by Java. References to other scripts or modules are possible.
 This is due to allow every kind of processing that is implemented in this project. At the end of each function the response_creator will save the response under the
 corresponding message id to the file system so that the response can be read by Java.
"""

#import sys
from lexical_analysis import LexicalAnalysis
import message_manager
from mlm_class import *
#from xml.dom.minidom import parse
import xml.etree.ElementTree as ET
from datetime import datetime


def perform_promotion_process_from_java(messageId):
    """
    Receives a messageId from Java and performs MLM promotion
    """
    print('func is called')
    arg = message_manager.readMessageContent(messageId)
    # arg[0] is path of XML/MLM document
    path = arg[0]
    mlm = MultilevelModel(path)
    message_manager.postResponse(messageId, mlm)
    return


def import_XML(messageId):
    """
    transmitted path is send to Java and opened as Multi-Level Model
    """
    path = "C:\Programme\XModeler-AutoMLM-v1\XModeler\AutoMLM\src\java_communication\dummy.xml"
    message_manager.postResponse(messageId, path)
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

def getProjectName(messageId):
    # get project name  of path
    args = message_manager.readMessageContent(messageId)
    path = args[0]

    # works only for models version 4

    # parse xml
    tree = ET.parse(path)
    root = tree.getroot()

    # get project name
    model = root.find('Model')
    projectName = model.attrib['name']
    projectName = projectName.split('::')[1]

    # return project name
    message_manager.postResponse(messageId, projectName)
    return

def getDiagramName(messageId):
    # get project name  of path
    args = message_manager.readMessageContent(messageId)
    path = args[0]

    # works for models version 4

    # parse xml
    tree = ET.parse(path)
    root = tree.getroot()

    # get diagram name
    diagrams = root.find('Diagrams')
    diagram = diagrams.find('Diagram')
    diagramName = diagram.attrib['name']

    message_manager.postResponse(messageId, diagramName)
    return

def process_string(messageId):
    """
    Reads a string from Java adds "from Python" and returns it
    """
    arg = message_manager.readMessageContent(messageId)
    string = arg[0]
    string += ' from Python'
    message_manager.postResponse(messageId, string)
    return

def promoteDiagram(messageId):

    print(datetime.now)

    arg = message_manager.readMessageContent(messageId)
    input_file_path = arg[1]
    model = MultilevelModel(input_file_path)


    analyser = LexicalAnalysis(model, promotionCategory=arg[0], maxWordSenses=arg[2], depthTopLevel=arg[3], acceptingValueSim=arg[4], rejectingValueSim=arg[5])

    pathNew = analyser.perform_Analysis()

    message_manager.postResponse(messageId, pathNew)

    print(datetime.now)
    return

    """
    helper = LexicalAnalysisHelper()
    
    arg = message_manager.readMessageContent(messageId)
    input_file_path = arg[1]
    promotion_category = arg[0]

    maxWordSenses = arg[2]
    depthTopLevel = arg[3]
    acceptingValueSim = arg[4]
    rejectingValueSim = arg[5]

    # TODO based on the diagram and the category the promotion process can happen
    # at the moment only the path of a dummy diagram is returned

    #if promotion_category == 'GA':
    model = MultilevelModel(input_file_path)
        #pathNew = helper.performAnalysis_GA(model, arg)


    new_Model = xml_export.preamble('Root::Modell')
    projectName = new_Model.attrib['path']

    parentName = ""
        
    objs = model.mlm_objects
    
    for o1 in objs:
        for o2 in objs:
            if o1 is o2:
                continue
            c = helper.getCommonHypernyms(o1, o2)
            c = helper._reduceSetOfHypernyms(c)
            cstr = f'{o1.name} and {o2.name}'
            print(cstr.ljust(50,' '), [a[0] for a in c])
            print(c[0][0])
            parentName = c[0][0].name().split(".")[0]
        

    parent = MlmObject(projectName+"::"+parentName, parentName, 1, None, False)
    parent.export(new_Model)
    for o in objs:
        cl = MlmObject(projectName+"::"+o.name, o.name, 1, None, False)
        cl.add_parent_class(parent)
        for attr in o.attr_list:
            a = MlmAttr(attr.attr_name, attr.attr_type, 0)
            cl.add_attr(a)
        cl.export(new_Model)

    pathNew = 'AutoMLM\\mlm_files\\deepModel.xml'

    xml_export.writeXML(new_Model, pathNew)

    
    

    message_manager.postResponse(messageId,pathNew)
    return
    """