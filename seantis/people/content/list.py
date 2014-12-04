from collections import namedtuple

from five import grok
from zope.security import checkPermission as has_permission

from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.interfaces.constrains import IConstrainTypes, ENABLED

from seantis.people import catalog_id
from seantis.people.interfaces import IPerson, IList
from seantis.people.supermodel import get_selectable_field_ix
from seantis.plonetools import tools


ListFilter = namedtuple('ListFilter', ['key', 'value', 'title'])
LetterFilter = namedtuple('LetterFilter', ['value', 'title'])


class List(Container):

    def getTypeInfo(self):
        fti = super(List, self).getTypeInfo()

        if fti is None:
            return None
        else:
            # Update the list of available types if it's not correct.
            # This will lead to a write, but I've tried all possible hacks
            # to get around that and I want to do this here where it's
            # convenient.

            # This kind of clones the ListConstrainTypes logic below, but
            # Plone sometimes uses this (CMFPlone) and sometimes the other
            # (plone.api) - FUN!

            # only do this if the request is given, meaning that the people's
            # list view was opened (it doesn't matter anywhere else)
            if hasattr(self, 'request') or hasattr(self, 'REQUEST'):
                types = tuple(t.id for t in self.available_types())

                if fti.aq_base.allowed_content_types != types:
                    fti.aq_base.allowed_content_types = types

            return fti

    def invokeFactory(self, type, content_id, **kwargs):
        # fixes plone.api.create as a side-effect because that one uses a
        # cached fti which is not up to date during testing
        self.getTypeInfo()
        return super(List, self).invokeFactory(type, content_id, **kwargs)

    def people(
        self,
        filter=None,
        batch_start=None,
        batch_size=None,
        include_inactive=False,
        unrestricted_search=False
    ):
        catalog = api.portal.get_tool(catalog_id)

        query = {}
        query['path'] = {
            'query': '/'.join(self.getPhysicalPath()), 'depth': 1
        }

        if not include_inactive:
            if not has_permission('cmf.ModifyPortalContent', self):
                query['is_active_person'] = True

        query['sort_on'] = 'sortable_title'
        query['sort_order'] = 'ascending'

        if batch_start is not None and batch_size is not None:
            query['b_start'] = batch_start
            query['b_size'] = batch_size

        if filter:
            used_type = self.used_type()

            if used_type:

                if isinstance(filter, ListFilter):
                    keyword_index = get_selectable_field_ix(
                        used_type.id, filter.key
                    )

                if isinstance(filter, LetterFilter):
                    keyword_index = 'first_letter'

                query[keyword_index] = {'query': filter.value}

        if unrestricted_search:
            return catalog.unrestrictedSearchResults(query)
        else:
            return catalog(query)

    def letters(self):
        catalog = api.portal.get_tool(catalog_id)
        index = catalog._catalog.getIndex('first_letter')

        letters = set()

        for person in self.people():
            letter = index.getEntryForObject(person.getRID())

            if letter:
                letters.add(letter)

        return sorted(letters, key=tools.unicode_collate_sortkey())

    def possible_types(self):
        return tools.get_type_info_by_behavior(IPerson.__identifier__)

    def available_types(self):
        used_type = self.used_type()

        if used_type:
            return [used_type]
        else:
            return self.possible_types()

    def used_type(self):
        catalog = api.portal.get_tool(catalog_id)
        path = {'query': '/'.join(self.getPhysicalPath()), 'depth': 1}

        for fti in self.possible_types():
            if catalog(path=path, portal_type=fti.id, sort_limit=1)[:1]:
                return fti

        return None

    def reindex_organisations(self):
        for brain in self.people(unrestricted_search=True):
            brain.getObject().reindexObject(idxs=['membership_person'])


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
        return self.getLocallyAllowedTypes()
