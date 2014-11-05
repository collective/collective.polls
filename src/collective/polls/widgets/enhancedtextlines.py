# -*- coding: utf-8 -*-

import zope.component
import zope.interface
import zope.schema

from z3c.form import interfaces
from z3c.form import widget
from z3c.form.browser import textarea

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from collective.polls.widgets.interfaces import IEnhancedTextLinesWidget
from collective.polls import MessageFactory as _


class EnhancedTextLinesWidget(textarea.TextAreaWidget):
    """ Widget for adding new keywords and autocomplete with the ones in the
    system.
    """
    zope.interface.implementsOnly(IEnhancedTextLinesWidget)
    klass = u"keyword-widget"
    display_template = ViewPageTemplateFile('enhancedtextlines_display.pt')
    input_template = ViewPageTemplateFile('enhancedtextlines_input.pt')

    # JavaScript template
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

    def js(self):
        add = _(u"Add")
        add_option = _(u"Add Option")
        delete_option = _(u"Delete Option")
        edit_option = _(u"Edit Option")
        return self.js_template % dict(id=self.id, add=add, add_task=add_option,
                                       delete_task=delete_option,
                                       edit_task=edit_option)

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)


@zope.interface.implementer(interfaces.IFieldWidget)
def EnhancedTextLinesFieldWidget(field, request):
    """ IFieldWidget factory for EnhancedTextLinesFieldWidget.
    """
    return widget.FieldWidget(field, EnhancedTextLinesWidget(request))
