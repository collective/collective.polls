# -*- coding: utf-8 -*-
from collective.polls import MessageFactory as _
from collective.polls.widgets.interfaces import IEnhancedTextLinesWidget
from z3c.form import widget
from z3c.form.browser import textarea
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IFieldWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from zope.interface import implementsOnly


JS_TEMPLATE = """\
(function($) {{
    $().ready(function() {{
    tp_i18n = {{
        add:'{add}',
        add_task:'{add_task}',
        delete_task:'{delete_task}',
        edit_task:'{edit_task}'
    }}
     $('#{id}').tasksplease();
    }});
}})(jQuery);
"""


class EnhancedTextLinesWidget(textarea.TextAreaWidget):
    """Widget for adding new keywords and autocomplete with the ones in the
    system.
    """
    implementsOnly(IEnhancedTextLinesWidget)
    klass = u'keyword-widget'
    display_template = ViewPageTemplateFile('enhancedtextlines_display.pt')
    input_template = ViewPageTemplateFile('enhancedtextlines_input.pt')

    def js(self):
        add = _(u'Add')
        add_option = _(u'Add Option')
        delete_option = _(u'Delete Option')
        edit_option = _(u'Edit Option')
        return JS_TEMPLATE.format(
            id=self.id,
            add=add,
            add_task=add_option,
            delete_task=delete_option,
            edit_task=edit_option,
        )

    def render(self):
        if self.mode == DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)


@implementer(IFieldWidget)
def EnhancedTextLinesFieldWidget(field, request):
    """IFieldWidget factory for EnhancedTextLinesFieldWidget."""
    return widget.FieldWidget(field, EnhancedTextLinesWidget(request))
