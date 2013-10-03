from plone.supermodel import loadString, serializeSchema

from seantis.people import tests

from seantis.people.supermodel import (
    get_title_fields,
    set_title_fields,
    get_table_columns,
    set_table_columns
)


class TestSupermodel(tests.IntegrationTestCase):

    title_xml = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <field  name="first"
                        type="zope.schema.TextLine"
                        people:title="true">
                    <description/>
                    <title>Foobar</title>
                </field>
                <field  name="second"
                        type="zope.schema.TextLine"
                        people:title="false">
                    <description/>
                    <title>Foobar</title>
                </field>
                <field  name="third"
                        type="zope.schema.TextLine">
                    <description/>
                    <title>Foobar</title>
                </field>
                <field  name="fourth"
                        type="zope.schema.TextLine"
                        people:title="true">
                    <description/>
                    <title>Foobar</title>
                </field>
            </schema>
        </model>"""

    def test_load_title_schema(self):
        model = loadString(self.title_xml)
        self.assertEqual(
            sorted(get_title_fields(model.schema)),
            ['first', 'fourth']
        )

    def test_write_title_schema(self):
        model = loadString(self.title_xml)

        set_title_fields(model.schema, ['second', 'third'])

        xml = serializeSchema(model.schema)

        # get shorter assertions below
        xml = xml.replace(' type="zope.schema.TextLine"', '')

        self.assertIn('<field name="first">', xml)
        self.assertIn('<field name="second" people:title="true">', xml)
        self.assertIn('<field name="third" people:title="true">', xml)
        self.assertIn('<field name="fourth">', xml)

    column_xml = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <field  name="first"
                        type="zope.schema.TextLine"
                        people:column="1">
                    <description/>
                    <title>Foobar</title>
                </field>
                <field  name="second"
                        type="zope.schema.TextLine"
                        people:column="1">
                    <description/>
                    <title>Foobar</title>
                </field>
                <field  name="third"
                        type="zope.schema.TextLine">
                    <description/>
                    <title>Foobar</title>
                </field>
                <field  name="fourth"
                        type="zope.schema.TextLine"
                        people:column="2">
                    <description/>
                    <title>Foobar</title>
                </field>
            </schema>
        </model>"""

    def test_load_column_schema(self):
        model = loadString(self.column_xml)
        self.assertEqual(get_table_columns(model.schema), {
            'first': '1',
            'second': '1',
            'fourth': '2'
        })

    def test_write_column_schema(self):
        model = loadString(self.column_xml)

        set_table_columns(
            model.schema, {'first': '1', 'third': '2', 'fourth': '2'}
        )

        xml = serializeSchema(model.schema)

        # get shorter assertions below
        xml = xml.replace(' type="zope.schema.TextLine"', '')

        self.assertIn('<field name="first" people:column="1">', xml)
        self.assertIn('<field name="second">', xml)
        self.assertIn('<field name="third" people:column="2">', xml)
        self.assertIn('<field name="fourth" people:column="2">', xml)