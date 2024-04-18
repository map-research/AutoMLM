import xml.etree.ElementTree as ET
import mlm_classes
import datetime

# TODO add associations
# TODO add implementation into GUI -> automatically open this newly created file ...
# TODO add layout functionn (possibly layouter, java)
# TODO add variable name of project


def preamble(project_name):

    # TODO change to var
    project_name = 'Root::Model'

    root = ET.Element('XModelerPackage', path=project_name, version='4')

    imports = ET.SubElement(root, 'Imports')
    model = ET.SubElement(root, 'Model', name=project_name)
    
    diagrams = ET.SubElement(root, 'Diagrams')
     # TODO change to var
    diagram = ET.SubElement(diagrams, 'Diagram', name='Model')

    instances = ET.SubElement(diagram, 'Instances')
    edges = ET.SubElement(diagram, 'Edges')
    diagramDisProp = ET.SubElement(diagram, 'DiagramDisplayProperties', SHOWCONCRETESYNTAX='true', SHOWCONSTRAINTREPORTS='true', SHOWCONSTRAINTS='true', SHOWDERIVEDATTRIBUTES='true', SHOWDERIVEDOPERATIONS='true', SHOWGETTERSANDSETTERS='false', SHOWISSUETABLEVISIBLE='false', SHOWMETACLASSNAME='false', SHOWOPERATIONS='true', SHOWOPERATIONVALUES='true', SHOWSLOTS='true')
    view = ET.SubElement(diagram, 'View', name='Main View', tx='0.0', ty='0.0', xx='1.0')
    
    return root

def writeXML(root):
    tree = ET.ElementTree(root)
    tree.write('test.xml')

def addClass(mlmObject, root):
    # TODO get project name
    projectName = 'Root::Model::'

    diagrams = root.find('Diagrams')
    diagram = diagrams.find('Diagram')
    instances = diagram.find('Instances')
    # TODO good placement
    instance = ET.SubElement(instances, 'Instance', hidden='false', path=projectName+"::"+mlmObject.name, xCoordinate='0', yCoordinate='0')

    model = root.find('Model')
    
    if mlmObject.super_object == None:
        metaClass = ET.SubElement(model, 'addMetaClass', abstract='false', level=str(mlmObject.level), maxLevel=str(mlmObject.level), name=mlmObject.name, package=projectName, singleton='false')
    else:
        instance = ET.SubElement(model, 'addInstance', abstract='false', level=str(mlmObject.level), maxLevel=str(mlmObject.level), name=mlmObject.name, of=mlmObject.super_object.full_name, package=projectName, singleton='false')

    for attr in mlmObject.attr_list:
        attribute = ET.SubElement(model, 'addAttribute',level=str(attr.inst_level), multiplicity='Seq{1,1,true,false}',name=attr.attr_name, package=projectName, type=attr.attr_type )
        # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
        attribute.set('class', projectName+mlmObject.name)

    for slot in mlmObject.slot_list:
        slot = ET.SubElement(model, 'changeSlotValue', package = projectName, slotName = slot.attr.attr_name ,valueToBeParsed=slot.value)
         # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
        slot.set('class', projectName+mlmObject.name)           

# parser for string values
def convertStringToXModeler(stringInput):
    list = []
    for char in stringInput:
        list.append(ord(char))

    out = str(list) + '.asString()'
    return out

# parser for datetime values
def convertDateToXmodeler(dateInput: datetime):
    out = 'Auxiliary::Date::createDate(' + str(dateInput.year) + ',' + str(dateInput.month) + ',' + str(dateInput.day) +')'
    return out


def main():

    # demo beispiel eines dokuments was im XModeler geöffnet werden kann
    projectName = 'Root::Model::'
    root = preamble(' ')

    attr = mlm_classes.MlmAttr('lastUpdate','Root::XCore::String',0)
    slot = mlm_classes.MlmSlot(attr,convertStringToXModeler('test'))
    slot3 = mlm_classes.MlmSlot(attr, convertStringToXModeler('pierreIstDoof'))

    attr1 = mlm_classes.MlmAttr('alter', 'Root::XCore::Integer', 0)
    slot1 = mlm_classes.MlmSlot(attr1, '1')

    attr2 = mlm_classes.MlmAttr('dautm', 'Root::Auxiliary::Date',0)
    slot2 = mlm_classes.MlmSlot(attr2, convertDateToXmodeler(datetime.datetime(2020,5,17)))

    obj = mlm_classes.MlmObject(projectName+'Monograph', 'Monograph', 1, [attr, attr1, attr2],[],None)
    obj1 = mlm_classes.MlmObject(projectName+'Mono1', 'Mono1',0,[],[slot, slot1, slot2],obj)
    obj2 = mlm_classes.MlmObject(projectName+'Mono2', 'Mono2',0,[],[slot3, slot1, slot2],obj)

    addClass(obj,root)
    addClass(obj1, root)
    addClass(obj2,root)
    writeXML(root)

if __name__ == "__main__":
    main()