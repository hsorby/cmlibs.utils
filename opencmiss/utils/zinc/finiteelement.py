"""
Utilities for creating and working with Zinc Finite Elements.
"""
from opencmiss.utils.maths import vectorops
from opencmiss.utils.zinc.general import ZincCacheChanges
from opencmiss.zinc.element import Element, Elementbasis, Mesh
from opencmiss.zinc.field import Field, FieldFiniteElement
from opencmiss.zinc.fieldmodule import Fieldmodule
from opencmiss.zinc.node import Node, Nodeset
from opencmiss.zinc.result import RESULT_OK


def createNodes(nodeset : Nodeset, finite_element_field : Field, node_coordinate_set):
    """
    Create a node for every coordinate in the node_coordinate_set.

    :param nodeset: The Zinc Nodeset to create nodes in.
    :param finite_element_field: Zinc FieldFiniteElement to define node coordinates for.
    :param node_coordinate_set: Sequence containing list of coordinates with
    same number as number of components in finite_element_field.
    :return: None
    """
    assert finite_element_field.castFiniteElement().isValid()
    fieldmodule = finite_element_field.getFieldmodule()
    node_template = nodeset.createNodetemplate()
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()
    with ZincCacheChanges(fieldmodule):
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            # Set the node coordinates, first set the field cache to use the current node
            field_cache.setNode(node)
            # Pass in floats as an array
            finite_element_field.assignReal(field_cache, node_coordinate)


def createTriangleElements(mesh : Mesh, finite_element_field : Field, element_node_set):
    """
    Create a linear triangular element for every set of 3 local nodes in element_node_set.

    :param mesh: The Zinc Mesh to create elements in.
    :param finite_element_field: Zinc FieldFiniteElement to interpolate from nodes.
    :param element_node_set: Sequence of 3 node identifiers for each element.
    :return: None
    """
    assert mesh.getDimension() == 2
    assert finite_element_field.castFiniteElement().isValid()
    fieldmodule = finite_element_field.getFieldmodule()
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_TRIANGLE)
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_SIMPLEX)
    eft = mesh.createElementfieldtemplate(linear_basis);
    element_template.defineField(finite_element_field, -1, eft)
    with ZincCacheChanges(fieldmodule):
        for element_nodes in element_node_set:
            element = mesh.createElement(-1, element_template)
            element.setNodesByIdentifier(eft, element_nodes)
    fieldmodule.defineAllFaces()


def createCubeElement(mesh : Mesh, finite_element_field : Field, node_coordinate_set):
    """
    Create a single finite element using the supplied
    finite element field and sequence of 8 n-D node coordinates.

    :param mesh: The Zinc Mesh to create elements in.
    :param fieldmodule: Owning fieldmodule for new elements and nodes.
    :param finite_element_field:  Zinc FieldFiniteElement to interpolate on element.
    :param node_coordinate_set: Sequence of 8 coordinates each with as many components as finite element field.
    :return: None
    """
    assert mesh.getDimension() == 3
    assert finite_element_field.castFiniteElement().isValid()
    assert len(node_coordinate_set) == 8
    fieldmodule = finite_element_field.getFieldmodule()
    nodeset = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_template = nodeset.createNodetemplate()
    node_template.defineField(finite_element_field)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    linear_basis = fieldmodule.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    eft = mesh.createElementfieldtemplate(linear_basis);
    element_template.defineField(finite_element_field, -1, eft)
    field_cache = fieldmodule.createFieldcache()
    with ZincCacheChanges(fieldmodule):
        node_identifiers = []
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, node_coordinate)
        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, node_identifiers)
    fieldmodule.defineAllFaces()


def createSquareElement(mesh : Mesh, finite_element_field : Field, node_coordinate_set):
    """
    Create a single square 2-D finite element using the supplied
    finite element field and sequence of 4 n-D node coordinates.

    :param mesh: The Zinc Mesh to create elements in.
    :param fieldmodule: Owning fieldmodule for new elements and nodes.
    :param finite_element_field:  Zinc FieldFiniteElement to interpolate on element.
    :param node_coordinate_set: Sequence of 4 coordinates each with as many components as finite element field.
    :return: None
    """
    assert mesh.getDimension() == 2
    assert finite_element_field.castFiniteElement().isValid()
    assert len(node_coordinate_set) == 4
    fieldmodule = finite_element_field.getFieldmodule()
    nodeset = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_template = nodeset.createNodetemplate()
    node_template.defineField(finite_element_field)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    eft = mesh.createElementfieldtemplate(linear_basis);
    element_template.defineField(finite_element_field, -1, eft)
    field_cache = fieldmodule.createFieldcache()
    with ZincCacheChanges(fieldmodule):
        node_identifiers = []
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, node_coordinate)
        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, node_identifiers)
    fieldmodule.defineAllFaces()


def findNodeWithName(nodeset : Nodeset, nameField : Field, name):
    """
    Get single node in nodeset with supplied name.
    :param nodeset: Zinc Nodeset or NodesetGroup to search.
    :param nameField: The name field to match.
    :param name: The name to match in nameField.
    :return: Node with name, or None if 0 or multiple nodes with name.
    """
    fieldmodule = nodeset.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    nodeiter = nodeset.createNodeiterator()
    nodeWithName = None
    node = nodeiter.next()
    while node.isValid():
        fieldcache.setNode(node)
        tempName = nameField.evaluateString(fieldcache)
        if tempName == name:
            if nodeWithName:
                return None
            nodeWithName = node
        node = nodeiter.next()
    return nodeWithName


def getNodeNameCentres(nodeset : Nodeset, coordinatesField : Field, nameField : Field):
    """
    Find mean locations of node coordinate with the same names.
    :param nodeset: Zinc Nodeset or NodesetGroup to search.
    :param coordinatesField: The coordinate field to evaluate.
    :param nameField: The name field to match.
    :return: Dict of names -> coordinates.
    """
    componentsCount = coordinatesField.getNumberOfComponents()
    fieldmodule = nodeset.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    nameRecords = {}  # name -> (coordinates, count)
    nodeiter = nodeset.createNodeiterator()
    node = nodeiter.next()
    while node.isValid():
        fieldcache.setNode(node)
        name = nameField.evaluateString(fieldcache)
        coordinatesResult, coordinates = coordinatesField.evaluateReal(fieldcache, componentsCount)
        if name and (coordinatesResult == RESULT_OK):
            nameRecord = nameRecords.get(name)
            if nameRecord:
                nameCentre = nameRecord[0]
                for c in range(componentsCount):
                    nameCentre[c] += coordinates[c]
                nameRecord[1] += 1
            else:
                nameRecords[name] = (coordinates, 1)
        node = nodeiter.next()
    # divide centre coordinates by count
    nameCentres = {}
    for name in nameRecords:
        nameRecord = nameRecords[name]
        nameCount = nameRecord[1]
        nameCentre = nameRecord[0]
        if nameCount > 1:
            scale = 1.0/nameCount
            for c in range(componentsCount):
                nameCentre[c] *= scale
        nameCentres[name] = nameCentre
    return nameCentres


def evaluateNodesetCoordinatesRange(coordinates : Field, nodeset : Nodeset):
    """
    :return: min, max range of coordinates field over nodes.
    """
    fieldmodule = nodeset.getFieldmodule()
    componentsCount = coordinates.getNumberOfComponents()
    with ZincCacheChanges(fieldmodule):
        minCoordinates = fieldmodule.createFieldNodesetMinimum(coordinates, nodeset)
        maxCoordinates = fieldmodule.createFieldNodesetMaximum(coordinates, nodeset)
        fieldcache = fieldmodule.createFieldcache()
        result, minX = minCoordinates.evaluateReal(fieldcache, componentsCount)
        assert result == RESULT_OK
        result, maxX = maxCoordinates.evaluateReal(fieldcache, componentsCount)
        assert result == RESULT_OK
        del minCoordinates
        del maxCoordinates
        del fieldcache
    return minX, maxX


def evaluateNodesetMeanCoordinates(coordinates : Field, nodeset : Nodeset):
    """
    :return: Mean of coordinates over nodeset.
    """
    fieldmodule = nodeset.getFieldmodule()
    componentsCount = coordinates.getNumberOfComponents()
    with ZincCacheChanges(fieldmodule):
        meanCoordinatesField = fieldmodule.createFieldNodesetMean(coordinates, nodeset)
        fieldcache = fieldmodule.createFieldcache()
        result, meanCoordinates = meanCoordinatesField.evaluateReal(fieldcache, componentsCount)
        assert result == RESULT_OK
        del meanCoordinatesField
        del fieldcache
    assert result == RESULT_OK
    return meanCoordinates


def transformCoordinates(field : Field, rotationScale, offset, time = 0.0) -> bool:
    '''
    Transform finite element field coordinates by matrix and offset, handling nodal derivatives and versions.
    Limited to nodal parameters, rectangular cartesian coordinates
    :param field: the coordinate field to transform
    :param rotationScale: square transformation matrix 2-D array with as many rows and columns as field components.
    :param offset: coordinates offset
    :return: True on success, otherwise false
    '''
    ncomp = field.getNumberOfComponents()
    if ((ncomp != 2) and (ncomp != 3)):
        print('zinc.transformCoordinates: field has invalid number of components')
        return False
    if (len(rotationScale) != ncomp) or (len(offset) != ncomp):
        print('zinc.transformCoordinates: invalid matrix number of columns or offset size')
        return False
    for matRow in rotationScale:
        if len(matRow) != ncomp:
            print('zinc.transformCoordinates: invalid matrix number of columns')
            return False
    if (field.getCoordinateSystemType() != Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN):
        print('zinc.transformCoordinates: field is not rectangular cartesian')
        return False
    feField = field.castFiniteElement()
    if not feField.isValid():
        print('zinc.transformCoordinates: field is not finite element field type')
        return False
    success = True
    fm = field.getFieldmodule()
    fm.beginChange()
    cache = fm.createFieldcache()
    cache.setTime(time)
    nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    nodetemplate = nodes.createNodetemplate()
    nodeIter = nodes.createNodeiterator()
    node = nodeIter.next()
    while node.isValid():
        nodetemplate.defineFieldFromNode(feField, node)
        cache.setNode(node)
        for derivative in [Node.VALUE_LABEL_VALUE, Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D2_DS1DS2,
                           Node.VALUE_LABEL_D_DS3, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3, Node.VALUE_LABEL_D3_DS1DS2DS3]:
            versions = nodetemplate.getValueNumberOfVersions(feField, -1, derivative)
            for v in range(versions):
                result, values = feField.getNodeParameters(cache, -1, derivative, v + 1, ncomp)
                if result != RESULT_OK:
                    success = False
                else:
                    newValues = vectorops.matrixvectormult(rotationScale, values)
                    if derivative == Node.VALUE_LABEL_VALUE:
                        newValues = vectorops.add(newValues, offset)
                    result = feField.setNodeParameters(cache, -1, derivative, v + 1, newValues)
                    if result != RESULT_OK:
                        success = False
        node = nodeIter.next()
    fm.endChange()
    if not success:
        print('zinc.transformCoordinates: failed to get/set some values')
    return success
