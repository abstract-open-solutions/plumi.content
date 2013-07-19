# -*- coding: utf-8 -*-

from zope.component import queryMultiAdapter
from zope.interface import Interface

from plone.memoize.view import memoize as view_memoize

from interfaces import IVideosProvider
from interfaces import IPlumiVideoBrain
from taxonomy import CategoriesProvider


class VideosListing(CategoriesProvider):
    """
    This browser view is convenient to fetch videos informations
    necessary to the display of a videos provider.
    """

    @property
    @view_memoize
    def videos(self):
        return IVideosProvider(self.context).videos

    @property
    def empty(self):
        return bool(not self.videos)

    @property
    def renderers(self):
        """Batch prevents us to only returns a list of renderers.
        This list of renderers is the one to iterate if a rendering
        is wanted.
        """
        return [queryMultiAdapter((brain, self), IPlumiVideoBrain)\
                for brain in self.videos]

    @property
    def parent_url(self):
        return self.context.navigationParent(self.context,
                                            "video_listing_view")
