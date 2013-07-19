"""This package adds extensions to portal_catalog.
"""
import logging

from zope.component import getUtility
from zope.interface import providedBy, Interface
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.indexer.decorator import indexer

from collective.transcode.star.interfaces import ITranscodeTool
from plumi.content.interfaces import IPlumiVideo


@indexer(IPlumiVideo)
def hasImageAndCaption(obj, **kw):
    logger=logging.getLogger('plumi.content.indexes')

    logger.debug('hasImageAndCaption - have %s ' % obj )
    img = obj.getThumbnailImage()
    #check that the image is set
    md = {'image': False, 'caption': u''}
    if img is not None and img is not '':
        caption = obj.getThumbnailImageDescription() or u''
        md = {'image': True, 'caption': caption }

    logger.debug('hasImageAndCaption returning %s  . thumbnail obj is %s' %
                 (md, obj.getThumbnailImage()))
    return md

@indexer(IPlumiVideo)
def isTranscodedPlumiVideoObj(obj,**kw):
    logger=logging.getLogger('plumi.content.indexes')
    logger.debug(' isTranscodedPlumiVideoObj - have %s ' % obj )
    try:
        tt = getUtility(ITranscodeTool)
        return tt[obj.UID()]['video_file']
    except:
        return

@indexer(IPlumiVideo)
def isPublishablePlumiVideoObj(obj,**kw):
    logger=logging.getLogger('plumi.content.indexes')
    logger.debug(' isPublishablePlumiVideoObj - have %s ' % obj )

    portal_workflow = getToolByName(obj,'portal_workflow')
    portal_membership = getToolByName(obj,'portal_membership')
    portal_contentlicensing = getToolByName(obj,'portal_contentlicensing')

    #wf state
    item_state = portal_workflow.getInfoFor(obj, 'review_state', '')
    #name of creator 
    member_name = obj.Creator()
    #get the actual user obj
    user = portal_membership.getMemberById(member_name)
    obj.plone_log("Item %s by %s is in state %s. user is %s " % (obj.absolute_url(), member_name, item_state,user))
    if user is None:
        obj.plone_log("No matching members??")

    if user is not None and item_state == 'published':
        (url,length,type) = obj.getFileAttribs()
        cclicense = portal_contentlicensing.getLicenseAndHolderFromobj(obj)
        cclicense_text = portal_contentlicensing.DefaultSiteLicense[0]
        cclicense_url  = None
        if cclicense[1][1] != 'None':
                cclicense_text = cclicense[1][1]
        if cclicense[1][2] != 'None':
                cclicense_url  = cclicense[1][2]

        d = {
              'published':True,
              'item_title': obj.Title(),
              'item_creator_email': user.getProperty('email',''),
              'item_creator_fullname':user.getProperty('fullname',''),
              'subject': obj.Subject(),
              'item_rfc822_datetime': DateTime(obj.Date()).rfc822(),
              'item_rfc3339_datetime': DateTime(obj.Date()).HTML4(),
              'file_url': url,
              'file_length':length,
              'file_type':type,
              'item_url':obj.absolute_url(),
              'license_text':cclicense_text,
              'license_url':cclicense_url
            }
    else:
        d = {'published': False }

    return d

@indexer(IPlumiVideo)
def videoDuration(obj,**kw):
    logger=logging.getLogger('plumi.content.indexes')
    logger.debug('videoDuration - have %s ' % obj )
    duration = obj.plumiVideoDuration()
    logger.debug(' videoDuration returning %s  ' % (duration))
    return duration