from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from opencmiss.zinc.context import Context
from opencmiss.utils.zinc.field import findOrCreateFieldCoordinates
from opencmiss.utils.zinc.general import ChangeManager


class Path(object):

    def __init__(self, options: dict):
        self.__context = Context(options["id"])
        self.__region = self.__context.getDefaultRegion()
        self.__options = options

    def get_context(self):
        return self.__context

    def get_region(self):
        return self.__region

    def get_options(self):
        return self.__options

    def generate(self):
        coordinate_dimensions = 3
        elements_count = self.__options['number of elements']
        node_coordinates = self.__options['node coordinates']

        field_module = self.__region.getFieldmodule()

        with ChangeManager(field_module):
            field_module.beginChange()
            coordinates = findOrCreateFieldCoordinates(field_module, components_count=coordinate_dimensions)
            cache = field_module.createFieldcache()

            # Create nodes

            nodes = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
            node_template = nodes.createNodetemplate()
            node_template.defineField(coordinates)
            node_template.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
            node_template.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)

            node_identifier = 1

            for n in range(len(node_coordinates)):
                node = nodes.createNode(node_identifier, node_template)
                cache.setNode(node)
                x = node_coordinates[n]
                # d = node_derivatives[n]

                coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x)
                # coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, d)
                node_identifier = node_identifier + 1

            # Create elements

            mesh = field_module.findMeshByDimension(1)
            cubic_hermite_basis = field_module.createElementbasis(1, Elementbasis.FUNCTION_TYPE_CUBIC_HERMITE)
            eft = mesh.createElementfieldtemplate(cubic_hermite_basis)
            element_template = mesh.createElementtemplate()
            element_template.setElementShapeType(Element.SHAPE_TYPE_LINE)
            result = element_template.defineField(coordinates, -1, eft)

            element_identifier = 1
            for e in range(elements_count):
                element = mesh.createElement(element_identifier, element_template)
                element.setNodesByIdentifier(eft, [e + 1, e + 2])
                element_identifier = element_identifier + 1

    def write(self, filename: str):
        self.__region.writeFile(filename)
