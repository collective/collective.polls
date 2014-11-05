# -*- coding: utf-8 -*-

from collective.polls.widgets.enhancedtextlines import EnhancedTextLinesWidget
from collective.polls.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from z3c.form.interfaces import DISPLAY_MODE

import unittest2 as unittest


class WidgetTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        types = self.portal['portal_types']
        fti = types.getTypeInfo('Document')
        self.obj = fti.constructInstance(self.portal, 'test1')

    def test_js(self):
        widget = EnhancedTextLinesWidget(self.request)
        widget.context = self.obj
        widget.id = 'test'

        result = widget.js()

        js_template = """\
    (function($) {
        $().ready(function() {
        tp_i18n = {
            add:'%(add)s',
            add_task:'%(add_task)s',
            delete_task:'%(delete_task)s',
            edit_task:'%(edit_task)s'
        }
         $('#%(id)s').tasksplease();
        });
    })(jQuery);
    """

        self.assertEqual(result, js_template % dict(id='test',
                                                    add='Add',
                                                    add_task='Add Option',
                                                    delete_task='Delete Option',
                                                    edit_task='Edit Option'))

        widget_template = """\

<script type="text/javascript">    (function($) {
        $().ready(function() {
        tp_i18n = {
            add:'%(add)s',
            add_task:'%(add_task)s',
            delete_task:'%(delete_task)s',
            edit_task:'%(edit_task)s'
        }
         $('#%(id)s').tasksplease();
        });
    })(jQuery);
    </script>
<textarea id="test" class="keyword-widget"></textarea>

"""

        result = widget.render()
        self.assertEqual(result, widget_template % dict(id='test',
                                                        add='Add',
                                                        add_task='Add Option',
                                                        delete_task='Delete Option',
                                                        edit_task='Edit Option'))

        widget.mode = DISPLAY_MODE
        result = widget.render()
        self.assertEqual(result, u'\n<span id="test" class="keyword-widget"></span>\n\n')
