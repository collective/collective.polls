# -*- coding: utf-8 -*-

from collective.polls import MessageFactory as _
from zope.schema.vocabulary import SimpleVocabulary

resultsAsVocabulary = SimpleVocabulary.fromItems((
    (_(u'Votes count'), 'votes'),
    (_(u'Percentage'), 'percentage')))
