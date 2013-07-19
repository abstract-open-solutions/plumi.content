# -*- coding: utf-8 -*-

# ported from PlumiSkin 0.2.x trunk - 17/7/09
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.topic import IATTopic
from Products.ATContentTypes.interface.folder import IATFolder

try:
    from plone.app.collection.interfaces import ICollection
except ImportError:
    class ICollection(Interface):
        """ dummy klass in case we do not have p.a.collection
        """

from interfaces import IVideosProvider


class TopicVideosProvider(object):
    adapts(IATTopic)
    implements(IVideosProvider)

    def __init__(self, context):
        """It would be much better not to count on the acquisition and
        old python script, and recode this part.
        """
        self.videos = context.queryCatalog()


class CollectionVideosProvider(object):
    adapts(ICollection)
    implements(IVideosProvider)

    def __init__(self, context):
        """It would be much better not to count on the acquisition and
        old python script, and recode this part.
        """
        self.videos = context.queryCatalog()


class OrderedFolderVideosProvider(object):
    adapts(IATFolder)
    implements(IVideosProvider)

    def __init__(self, context):
        """It would be much better not to count on the acquisition and
        old python script, and recode this part.
        """
        if context.portal_type == 'Plumi Video Folder':
            path = "/".join(context.getPhysicalPath())
            content_filter = {}
            content_filter['path'] = path
            content_filter['portal_type']='PlumiVideo'
            content_filter['sort_on'] = 'effective'
            content_filter['sort_order'] = 'reverse'
            self.videos = context.getFolderContents(contentFilter=content_filter)
        else:
            self.videos = context.getFolderContents()
