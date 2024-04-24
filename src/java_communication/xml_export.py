import xml.etree.ElementTree as ET
import mlm_helper_classes
import datetime

# TODO implement export functions into mlm_class.py
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
    diagramDisProp = ET.SubElement(diagram, 'DiagramDisplayProperties', SHOWCONCRETESYNTAX='true', SHOWCONSTRAINTREPORTS='true',
                                   SHOWCONSTRAINTS='true', SHOWDERIVEDATTRIBUTES='true', SHOWDERIVEDOPERATIONS='true', SHOWGETTERSANDSETTERS='false',
                                   SHOWISSUETABLEVISIBLE='false', SHOWMETACLASSNAME='false', SHOWOPERATIONS='true', SHOWOPERATIONVALUES='true', SHOWSLOTS='true')
    view = ET.SubElement(diagram, 'View', name='Main View', tx='0.0', ty='0.0', xx='1.0')
    
    return root

def writeXML(root: ET.Element):
    tree = ET.ElementTree(root)
    tree.write('test.xml')

def addClass(mlmObject : mlm_helper_classes.MlmObject, root):
    # TODO get project name
    projectName = 'Root::Model'

    diagrams = root.find('Diagrams')
    diagram = diagrams.find('Diagram')
    instances = diagram.find('Instances')
    # TODO good placement
    instance = ET.SubElement(instances, 'Instance', hidden='false', path=projectName+"::"+mlmObject.name, xCoordinate='0', yCoordinate='0')

    model = root.find('Model')
    
    if mlmObject.class_of_object == None:
        metaClass = ET.SubElement(model, 'addMetaClass', abstract='false', level=str(mlmObject.level), maxLevel=str(mlmObject.level), name=mlmObject.name, package=projectName, singleton='false')
    else:
        instance = ET.SubElement(model, 'addInstance', abstract='false', level=str(mlmObject.level), maxLevel=str(mlmObject.level), name=mlmObject.name, of=mlmObject.class_of_object.full_name, package=projectName, singleton='false')

    for attr in mlmObject.attr_list:
        attribute = ET.SubElement(model, 'addAttribute',level=str(attr.inst_level), multiplicity='Seq{1,1,true,false}',name=attr.attr_name, package=projectName, type=attr.attr_type )
        # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
        attribute.set('class', projectName+"::"+mlmObject.name)

    for slot in mlmObject.slot_list:
        slot = ET.SubElement(model, 'changeSlotValue', package = projectName, slotName = slot.attribute.attr_name ,valueToBeParsed=slot.value)
         # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
        slot.set('class', projectName+mlmObject.name)           

    for constraint in mlmObject.constraints_list:
        constraint = ET.SubElement(model, 'addConstraint', body='true', constName=constraint.constraint_name, instLevel=str(constraint.inst_level), package=projectName, reason='"This constraint fails"')
        constraint.set('class', projectName+"::"+mlmObject.name)

    for operation in mlmObject.operations_list:
        operation = ET.SubElement(model, 'addOperation', body='@Operation '+operation.operation_name+' [monitor=false,delToClassAllowed=false]():XCore::'+operation.return_type+' null end', 
                                  level=str(operation.inst_level), monitored='false', name=operation.operation_name, package=projectName, paramNames='', paramTypes='', type=operation.return_type)
        operation.set('class', projectName+"::"+mlmObject.name)

def exportAssociation(root, mlmAssoc: mlm_helper_classes.MlmAssociation):
    # TODO get project name
    projectName = 'Root::Model'
    model = root.find('Model') 
    
    # transform of cardinalities needed
    multSourceToTarget = 'Seq{' + str(mlmAssoc.target_multiplicity.min_card) +',' + str(mlmAssoc.target_multiplicity.max_card) + ',true,false}'
    multTargetToSource = 'Seq{' + str(mlmAssoc.source_multiplicity.min_card) +',' + str(mlmAssoc.source_multiplicity.max_card) + ',false,false}'

    addAssoc = ET.SubElement(model, 'addAssociation',accessSourceFromTargetName=mlmAssoc.source_class.name.lower(), 
                             accessTargetFromSourceName=mlmAssoc.target_class.name.lower(), classSource=mlmAssoc.source_class.full_name, 
                             classTarget=mlmAssoc.target_class.full_name, fwName=mlmAssoc.name, instLevelSource=str(mlmAssoc.source_inst_level), 
                             instLevelTarget=str(mlmAssoc.target_inst_level), multSourceToTarget=multSourceToTarget, 
                             multTargetToSource=multTargetToSource, package=projectName,reverseName='-1', sourceVisibleFromTarget='false', 
                             targetVisibleFromSource='true')
    return root

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


def exportEnum(root, enumType: mlm_helper_classes.EnumType):
    model = root.find('Model')
    addEnum = ET.SubElement(model, 'addEnumeration', name=enumType.enum_name)
    for value in enumType.enum_values:
        addEnumValue = ET.SubElement(model, 'addEnumerationValue', enum_name=enumType.enum_name, enum_value_name=str(value))


def main():

    projectName = 'Root::Model::'
    root = preamble(' ')

    enum = mlm_helper_classes.EnumType('Personenanmen')
    enum.add_enum_value('Peter')
    enum.add_enum_value('Hans')

    cl1 = mlm_helper_classes.MlmObject(projectName+'Monograph', 'Monograph', 1, None)
    cl2 = mlm_helper_classes.MlmObject(projectName+'Author','Author',1,None)
    obj1 = mlm_helper_classes.MlmObject(projectName+'mono1', 'mono1',0,cl1)

    attr = mlm_helper_classes.MlmAttr('alter', 'Root::XCore::Integer', 0)
    cons1 = mlm_helper_classes.MlmConstraint('constraint1', 0)
    op1 = mlm_helper_classes.MlmOperation('operation',0,'Float')

    
    cl1.add_attr(attr)
    cl1.add_constraint(cons1)
    cl1.add_operation(op1)

    assoc1 = mlm_helper_classes.MlmAssociation('writtenBy', 0,0)
    assoc1.set_source_class(cl1)
    assoc1.set_target_class(cl2)
    assoc1.set_source_multiplicity(0,1)
    assoc1.set_target_multiplicity(0,1)

    addClass(cl1,root)
    addClass(cl2, root)
    addClass(obj1, root)
    exportAssociation(root, assoc1)
    exportEnum(root,enum)




    #addClass(obj3, root)
    #addClass(obj1, root)
    #addClass(obj2,root)
    ##exportAssociation(root, assoc1)
    writeXML(root)

if __name__ == "__main__":
    main()