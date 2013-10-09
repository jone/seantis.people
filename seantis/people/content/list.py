from collections import namedtuple

from five import grok
from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.interfaces.constrains import IConstrainTypes, ENABLED

from seantis.people.interfaces import IPerson, IList

from seantis.people.supermodel import SELECTABLE_PREFIX
from seantis.plonetools import utils


ListFilter = namedtuple('ListFilter', ['key', 'value', 'title'])


class List(Container):

    def people(self, filter=None):
        catalog = api.portal.get_tool('portal_catalog')

        query = {}
        query['path'] = {
            'query': '/'.join(self.getPhysicalPath()), 'depth': 1
        }
        query['sort_on'] = 'sortable_title'
        query['sort_order'] = 'ascending'

        if filter:
            query[SELECTABLE_PREFIX + filter.key] = filter.value

        return catalog(query)

    def possible_types(self):
        return utils.get_type_info_by_behavior(IPerson.__identifier__)

    def available_types(self):
        used_type = self.used_type()

        if used_type:
            return [used_type]
        else:
            return self.possible_types()

    def used_type(self):
        catalog = api.portal.get_tool('portal_catalog')
        path = {'query': '/'.join(self.getPhysicalPath()), 'depth': 1}

        for fti in self.possible_types():
            if catalog(path=path, portal_type=fti.id, sort_limit=1)[:1]:
                return fti

        return None


class ListConstrainTypes(grok.Adapter):
    grok.provides(IConstrainTypes)
    grok.context(IList)

    def getConstrainTypesMode(self):
        return ENABLED

    def allowedContentTypes(self):
        return self.context.available_types()

    def getLocallyAllowedTypes(self):
        return [t.id for t in self.allowedContentTypes()]

    def getImmediatelyAddableTypes(self):
        return self.allowedContentTypes()
