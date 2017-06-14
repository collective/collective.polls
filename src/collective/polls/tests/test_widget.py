# -*- coding: utf-8 -*-
from collective.polls.testing import INTEGRATION_TESTING
from collective.polls.widgets.enhancedtextlines import EnhancedTextLinesWidget
from plone import api
from z3c.form.interfaces import DISPLAY_MODE

import unittest


class WidgetTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.obj = api.content.create(self.portal, 'Document', 'foo')

    def test_js(self):
        widget = EnhancedTextLinesWidget(self.request)
        widget.context = self.obj
        widget.id = 'test'

        result = widget.js()

        expected = """\
(function($) {
  $().ready(function() {
    tp_i18n = {
      add:'Add',
      add_task:'Add Option',
      delete_task:'Delete Option',
      edit_task:'Edit Option'
    }
    $('#test').tasksplease();
  });
})(jQuery);
""".split()

        self.assertEqual(result.split(), expected)  # ignore whitespaces

        expected = """\
<script>(function($) {
  $().ready(function() {
    tp_i18n = {
      add:'Add',
      add_task:'Add Option',
      delete_task:'Delete Option',
      edit_task:'Edit Option'
    }
    $('#test').tasksplease();
  });
})(jQuery);
</script>
<textarea id="test" class="keyword-widget"></textarea>
""".split()

        result = widget.render()
        self.assertEqual(result.split(), expected)  # ignore whitespaces

        widget.mode = DISPLAY_MODE
        result = widget.render()
        expected = '<span id="test" class="keyword-widget"> </span>'.split()

        self.assertEqual(result.split(), expected)  # ignore whitespaces
