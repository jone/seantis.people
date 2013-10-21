from collections import namedtuple
from plone.supermodel import loadString
from plone.namedfile.file import NamedImage

from seantis.people.browser.renderer import Renderer
from seantis.people import tests


class TestRenderer(tests.IntegrationTestCase):

    model = """<?xml version='1.0' encoding='utf8'?>
    <model xmlns="http://namespaces.plone.org/supermodel/schema">
        <schema>
            <field name="textline"
                   type="zope.schema.TextLine">
                <title>Textline</title>
            </field>
            <field name="email"
                   type="seantis.plonetools.schemafields.Email">
                <title>Email</title>
            </field>
            <field name="website"
                   type="seantis.plonetools.schemafields.Website">
                <title>Website</title>
            </field>
            <field name="blobimage"
                   type="plone.namedfile.field.NamedBlobImage">
                <title>Blobimage</title>
            </field>
            <field name="image"
                   type="plone.namedfile.field.NamedImage">
                <title>Image</title>
            </field>
        </schema>
    </model>"""

    @property
    def schema(self):
        return loadString(self.model).schema

    def render_value(self, field, value):
        renderer = Renderer(self.schema)
        context = namedtuple('MockContext', [field])(value)
        return renderer.render(context, field)

    def test_textline(self):
        self.assertEqual(self.render_value('textline', u'test'), u'test')

    def test_email(self):
        self.assertEqual(
            self.render_value('email', u'test@example.com'),
            u'<a href="mailto:test@example.com">test@example.com</a>'
        )

    def test_website(self):
        self.assertEqual(
            self.render_value('website', u'http://example.com'),
            (
                u'<a href="http://example.com" '
                u'target="_blank">http://example.com</a>'
            )
        )

    def test_image(self):

        renderer = Renderer(self.schema)

        # currently, only brains are supported
        class MockBrain(object):
            def getURL(self):
                return u'http://nohost/mock'

        context = MockBrain()
        context.image = None

        self.assertEqual(
            renderer.render(context, 'image'),
            ''
        )

        context.image = NamedImage()
        self.assertEqual(
            renderer.render(context, 'image'),
            u'<img src="http://nohost/mock/@@images/image/thumb" />'
        )