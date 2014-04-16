from zope.interface import implements
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plumi.content import _
from plumi.content.interfaces import IPlumiVideo


DEFAULT_TITLE = _(u"Video categories")


class ICurrentVideoCategories(IPortletDataProvider):

    portletTitle = schema.TextLine(
        title=_(u"Portlet title"),
        description=_(u"If none provided defaults to 'Video categories'"),
        required=False,
        default=u''
    )


class Assignment(base.Assignment):

    """
    """

    implements(ICurrentVideoCategories)

    title = DEFAULT_TITLE
    portletTitle = ''

    def __init__(self, **kw):
        for k, v in kw.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)


class Renderer(base.Renderer):

    title = DEFAULT_TITLE
    render = ViewPageTemplateFile('current_video_categories.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.catalog = getToolByName(context, 'portal_catalog')
        self.portletTitle = data.portletTitle
        self.ps = context.restrictedTraverse('@@plone_portal_state')

    @property
    def display_title(self):
        """ title displayed in portlet
        """
        if self.portletTitle:
            return self.portletTitle
        return self.title

    def has_categories(self):
        return bool(self.categories())

    def is_manager(self):
        if not self.ps.anonymous():
            member = self.ps.member()
            return member.checkPermission('Manage portlets', self.context)
        return False

    def categories(self):
        categories = []
        view = self.context.restrictedTraverse('video_view', None)
        if view:
            categories = view.categories
        return categories

    @property
    def available(self):
        return IPlumiVideo.providedBy(self.context) and \
            (self.has_categories() or self.is_manager())


class AddForm(base.AddForm):

    form_fields = form.Fields(ICurrentVideoCategories)

    def create(self, data):
        """
        """
        return Assignment(**data)


class EditForm(base.EditForm):

    form_fields = form.Fields(ICurrentVideoCategories)
