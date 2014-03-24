from datetime import date, time, datetime

import isodate
import tablib

from zope.i18nmessageid.message import Message

from plone import api
from plone.namedfile.file import NamedImage, NamedBlobImage

from seantis.plonetools import tools
from seantis.people import _
from seantis.people.errors import ContentExportError


supported_formats = [
    'csv',
    'json',
    'xls',
    'xlsx'
]


def export_people(request, container, portal_type, fields):

    people = get_people(container, portal_type)

    if not people:
        raise ContentExportError(_(u"No people to export"))

    records = (get_record(request, person, fields) for person in people)

    dataset = tablib.Dataset(headers=[f[1] for f in fields])
    map(dataset.append, records)

    return dataset


def get_people(container, portal_type):
    catalog = api.portal.get_tool('portal_catalog')
    path = '/'.join(container.getPhysicalPath())

    brains = catalog({
        'path': path,
        'portal_type': portal_type
    })

    return [b.getObject() for b in brains]


def get_record(request, person, fields):
    record = []

    translate = tools.translator(request, 'seantis.people')

    for field in (get_field(person, f[0]) for f in fields):
        if isinstance(field, Message):
            record.append(translate(field))
        else:
            record.append(field)

    return record


def get_field(person, field):

    if not hasattr(person, field):
        raise ContentExportError(_(u"Field '${name}' does not exist", mapping={
            'name': field
        }))

    value = getattr(person, field)

    if value is None:
        return u''

    if isinstance(value, bool):
        return _(u'Yes') if value is True else _(u'No')

    if isinstance(value, basestring):
        return unicode(value)

    if isinstance(value, (list, tuple, set)):
        return u', '.join(value)

    if isinstance(value, dict):
        parts = []
        for key in sorted(value):
            parts.append(u'{}: {}'.format(key, value[key]))
        return u', '.join(parts)

    if isinstance(value, date):
        return unicode(isodate.date_isoformat(value))

    if isinstance(value, datetime):
        return unicode(isodate.datetime_isoformat(value))

    if isinstance(value, time):
        return unicode(isodate.time_isoformat(value))

    if isinstance(value, (NamedImage, NamedBlobImage)):
        base = person.absolute_url()

        if value.filename:
            return u'{}/@@download/{}/{}'.format(base, field, value.filename)
        else:
            return u'{}/@@download/{}'.format(base, field)

    return value
