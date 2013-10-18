from five import grok

from Products.CMFPlone.PloneBatch import Batch

from seantis.people.interfaces import IList
from seantis.people.browser import BaseView, Renderer
from seantis.people.content.list import ListFilter
from seantis.people.supermodel import (
    get_schema_columns
)


class ListView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IList)
    grok.name('view')

    template = grok.PageTemplateFile('templates/list.pt')
    filter_prefix = 'filter-'

    def update(self):
        if self.has_people:
            self.renderer = Renderer(self.schema)

    @property
    def has_people(self):
        return bool(self.context.used_type())

    @property
    def schema(self):
        assert self.has_people, """
            Do not use if there are no people in the list.
        """

        return self.context.used_type().lookupSchema()

    @property
    def filter(self):
        for key in self.request.keys():
            if key.startswith(self.filter_prefix):
                val = self.request[key]
                key = key.replace(self.filter_prefix, '')

                field = self.has_people and self.schema.get(key, None) or None
                title = field and field.title or u''

                return ListFilter(key, val, title)

        return None

    @property
    def batch_size(self):
        return int(self.request.get('b_size', self.context.people_per_page))

    @property
    def batch_start(self):
        return int(self.request.get('b_start', 0))

    def render_field(self, person, field):
        return self.renderer.render(field, getattr(person, field))

    def people(self):
        people = self.context.people(
            filter=self.filter,
            batch_start=self.batch_start,
            batch_size=self.batch_size
        )
        return Batch(people, self.batch_size, self.batch_start)

    def columns(self):
        return get_schema_columns(self.schema)

    def combobox_values(self, column):
        return sorted(set(
            getattr(
                brain, column.fields[0]
            ) for brain in self.context.people()
        ))

    def selected_column_value(self, column):
        assert column.selectable

        filter = self.filter

        if not filter or filter.key != column.fields[0]:
            return '__all__'
        else:
            return filter.value
