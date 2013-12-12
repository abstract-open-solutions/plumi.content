from zope.interface import implements
from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plumi.content import _
from plumi.content.interfaces import IPlumiVideo


class IVideoFromSameCategories(IPortletDataProvider):

    portletTitle = schema.TextLine(
        title=_(u"Portlet title"),
        description=_(u"The title of the portlet."),
        required=True,
        default=u"Tag Cloud"
    )

    count = schema.Int(
        title=_(u"Maximum number of shown tags."),
        description=_(u"If greater than zero this number will limit the "
                      "tags shown."),
        required=True,
        min=0,
        default=10
    )


class Assignment(base.Assignment):

    """
    """

    implements(IVideoFromSameCategories)

    portletTitle = 'Video from same categories'
    count = 10

    def __init__(self, **kw):
        for k, v in kw.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)

    @property
    def title(self):
        """
        """
        return self.portletTitle


class Renderer(base.Renderer):

    """
    """

    render = ViewPageTemplateFile('video_from_same_categories.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.catalog = getToolByName(context, 'portal_catalog')
        self.portletTitle = data.portletTitle
        self.count = data.count
        self.ps = context.restrictedTraverse('@@plone_portal_state')

    def has_related(self):
        return bool(self.related())

    def related(self):
        view = getMultiAdapter((self.context, self.request),
                               name="video_view")
        return view.categories_latest(render=False)[:self.count or 10]

    def is_manager(self):
        if not self.ps.anonymous():
            member = self.ps.member()
            return member.checkPermission('Manage portlets', self.context)
        return False

    @property
    def available(self):
        return IPlumiVideo.providedBy(self.context) and \
            (self.has_related() or self.is_manager())


class AddForm(base.AddForm):

    """
    """

    form_fields = form.Fields(IVideoFromSameCategories)

    def create(self, data):
        """
        """
        return Assignment(**data)


class EditForm(base.EditForm):

    """
    """
    form_fields = form.Fields(IVideoFromSameCategories)
