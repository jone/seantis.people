from datetime import date, MAXYEAR

from plone import api
from zope.interface import implements

from seantis.plonetools import tools
from seantis.people.interfaces import IPerson
from seantis.people.behaviors.memberships import get_memberships
from seantis.people.utils import UUIDList

class Person(object):
    implements(IPerson)

    def __init__(self, context):
        self.context = context

    def memberships(self):
        return get_memberships(self.context)

    def organizations(self):
        """ Returns a list of organizations this person is active in. The list
        is sorted by uca collation. This is mainly used for the organizations
        metadata field of all person objects (to show in the list).

        """

        organizations = self.organization_uuids()

        catalog = api.portal.get_tool('portal_catalog')
        titles = (catalog(UID=uid)[0].Title for uid in organizations)

        return sorted(titles, key=tools.unicode_collate_sortkey())

    def organization_uuids(self):
        """ Returns the organizations as uuid references which are be rendered
        as links in the list view.

        """
        organizations = UUIDList()

        for uuid, memberships in self.memberships().items():
            if not self.active_memberships(memberships):
                continue

            organizations.append(uuid)

        return organizations

    def active_memberships(self, memberships):
        """ Goes through the given memberships and returns the active ones.
        The active memberships are the ones without end date. Or with an end
        date in the future.

        The result is sorted by date. Memberships without end come before
        memberships with end.
        """

        def sortkey(membership):
            if membership.end is not None:
                return membership.end
            else:
                return date(MAXYEAR, 12, 31)

        today = date.today()
        active = [m for m in memberships if m.end is None or m.end >= today]
        return sorted(active, key=sortkey)

    def current_role(self, memberships):
        """ Goes through the given memberships and returns the current role.
        The current role is the latest active membership's role.

        """
        active = self.active_memberships(memberships)
        if active:
            return active[0].role
        else:
            return u''
