# -*- coding: utf-8 -*-
import os.path

from Acquisition import aq_inner
from Acquisition import aq_parent

# Five & zope3 thingies
from zope import i18n
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryMultiAdapter

from plone.registry.interfaces import IRegistry
from plone.memoize import view

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.AdvancedQuery import Eq

from plumi.content.browser.interfaces import IVideoView
from plumi.content.browser.interfaces import ITopicsProvider
from plumi.content.browser.interfaces import IPlumiVideoBrain
from plumi.content.utils import get_settings
from plumi.content.permissions import ReTranscodePermission

# check if em.taxonomies is installed
try:
    from em.taxonomies.config import (
        TOPLEVEL_TAXONOMY_FOLDER,
        COUNTRIES_FOLDER,
        GENRE_FOLDER,
        CATEGORIES_FOLDER,
        LANGUAGES_FOLDER
    )
    TAXONOMIES = True
except ImportError:
    TAXONOMIES = False


# Internationalization
_ = i18n.MessageFactory("plumi.content")


class VideoView(BrowserView):
    u"""This browser view is used as utility for the atvideo view
    """
    implements(IVideoView, ITopicsProvider)

    def __init__(self, context, request):
        super(VideoView, self).__init__(context, request)
        self.portal_url = getToolByName(self.context, "portal_url")()
        self.vocab_tool = getToolByName(self.context, "portal_vocabularies")
        self.settings = get_settings()

    @property
    def transcode_helpers(self):
        return self.context.restrictedTraverse('@@transcode-helpers')

    @property
    def video_info(self):
        annotations = IAnnotations(self.context, None)
        return annotations.get('plumi.video_info')

    @property
    def categories(self):
        categories = self.context.getCategories()
        if categories:
            return self.get_categories_dict(categories)
        return tuple()

    @property
    def genres(self):
        """Actually, the genre is unique. We masquarade that.
        We might want the genre to be multivalued.
        """
        genres = self.context.getGenre()
        if genres and genres not in ['none', 'aaa_none']:
            return self.get_genres_info((genres,))
        return tuple()

    @property
    def subjects(self):
        subjects = self.context.Subject()
        if subjects:
            return self.get_subjects_info(subjects)
        return tuple()

    @property
    def country(self):
        country_id = self.context.getCountries()
        if country_id in ['OO', 'none', '']:
            return None
        if country_id:
            return self.get_country_info(country_id)
        return None

    @property
    def video_language(self):
        video_language_id = self.context.getVideoLanguage()
        if video_language_id:
            return self.get_video_language_info(video_language_id)
        return None

    @property
    def language(self):
        lang_id = self.context.Language()
        if lang_id:
            return self.get_country_info(lang_id)
        return None

    @property
    def review_state(self):
        wtool = getToolByName(self.context, "portal_workflow")
        return wtool.getInfoFor(self.context, 'review_state', None)

    @property
    def transcoding_rights(self):
        ps = self.context.restrictedTraverse('@@plone_portal_state')
        if not ps.anonymous():
            return ps.member().checkPermission(ReTranscodePermission,
                                               self.context)
        return False

    @property
    def bt_availability(self):
        """XXX fix bittorrent functionality
        media_tool = getToolByName(self.context, "portal_atmediafiletool")
        enabled_bt = media_tool.getEnable_bittorrent()
        enable_ext_bt = media_tool.getEnable_remote_bittorrent()
        bt_url = self.context.getTorrentURL()
        """
        bt_url = ''

        available = False
        return dict(available=available, url=bt_url)

    def playable(self):
        """ Is the source video in a web friendly format? """
        return len([ True for ext in ['.webm','.mp4','.m4v']
                    if self.context.video_file.filename.endswith(ext)])

    @property
    def transcoding(self):
        # XXX: refactor this!
        ret = {}
        helpers = self.transcode_helpers
        try:
            fname = helpers.fieldname
            info = helpers.info[fname]
            for k in info.keys():
                ret[k] = [info[k]['status'],
                          info[k]['status'] == 'ok' and info[k]['address'] + '/' + info[k]['path'] or \
                          info[k]['status'] == 'pending' and \
                          helpers.get_progress(k) or '0']
            return ret
        except Exception:
            return {}

    def is_transcoded(self):
        return self.transcode_helpers.is_transcoded()

    def get_categories_dict(self, cats):
        """Uses the portal vocabularies to retrieve the video categories"""
        voc = self.vocab_tool.getVocabularyByName('video_categories')

        if not TAXONOMIES:
            url = "%s/@@search?getCategories=" % (self.portal_url)
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                             TOPLEVEL_TAXONOMY_FOLDER, CATEGORIES_FOLDER)
        return (dict(id=cat_id,
                     url=url + cat_id,
                     title=voc.get(cat_id, None) and voc[cat_id].Title()) for cat_id in cats)

    def get_genres_info(self, genres):
        """Uses the portal vocabularies to retrieve the video genres"""
        voc = self.vocab_tool.getVocabularyByName('video_genre')

        if not TAXONOMIES:
            url = "%s/@@search?getGenre=" % self.portal_url
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                                 TOPLEVEL_TAXONOMY_FOLDER, GENRE_FOLDER)
        return (dict(id=genre_id,
                     url=url + genre_id,
                     title=voc[genre_id].Title()) for genre_id in genres)

    def get_subjects_info(self, subjects):
        """Fake the genres/categories process to return keywords infos"""
        url = "%s/@@search?Subject=" % (self.portal_url)
        return (dict(id=kw, url=url + kw, title=kw) for kw in subjects)

    def get_country_info(self, country_id):
        """Fake the genres/categories process to return the country infos"""
        voc = self.vocab_tool.getVocabularyByName('video_countries')
        country = voc[country_id]

        if not TAXONOMIES:
            url = "%s/@@search?getCountries=" % self.portal_url
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                                 TOPLEVEL_TAXONOMY_FOLDER, COUNTRIES_FOLDER)
        return dict(id=country_id, url=url + country_id, title=country.Title())

    def get_video_language_info(self, video_language_id):
        """Fake the genres/categories process
        to return the video language infos"""
        voc = self.vocab_tool.getVocabularyByName('video_languages')
        try:
            video_language = voc[video_language_id]
            language_title = video_language.Title
        except KeyError:
            language_title = video_language_id

        if not TAXONOMIES:
            url = "%s/@@search?getCountries=" % self.portal_url
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                                 TOPLEVEL_TAXONOMY_FOLDER,
                                 LANGUAGES_FOLDER)

        return dict(id=video_language_id,
                    url=url + video_language_id,
                    title=language_title)

    def _get_videos(self, extra_query=None,
                    sorting=None, exclude_self=True, render=True):
        query = {
            'portal_type': 'PlumiVideo',
            'review_state': ('published', 'featured'),
        }
        if extra_query is None:
            extra_query = {}
        query.update(extra_query)

        if sorting is None:
            sorting = [('effective','desc'), ]

        catalog = getToolByName(self.context, "portal_catalog")
        aq = catalog.makeAdvancedQuery(query)
        if exclude_self:
            # exclude content with current context UID
            aq &=~Eq('UID', self.context.UID())

        brains = catalog.evalAdvancedQuery(aq, sorting)
        if render:
            brains = [
                queryMultiAdapter((brain, self), IPlumiVideoBrain)
                for brain in brains
            ]
        return brains

    @view.memoize
    def authors_latest(self, **kw):
        parent = aq_parent(aq_inner(self.context))
        folder_path = '/'.join(parent.getPhysicalPath())
        extra_query = {
            'path': {'query': folder_path, 'depth': 1},
        }
        return self._get_videos(extra_query=extra_query, **kw)

    def show_authors_latest(self):
        if self.settings.video_related_display_author:
            return bool(self.authors_latest())
        return False

    @view.memoize
    def categories_latest(self, **kw):
        extra_query = {
            'getCategories': self.context.getCategories(),
        }
        return self._get_videos(extra_query=extra_query, **kw)

    def show_categories_latest(self):
        if self.settings.video_related_display_categories:
            return bool(self.categories_latest())
        return False

    @property
    def isVideo(self):
        return 'video' in self.context.getContentType()

    @property
    def isAudio(self):
        return 'audio' in self.context.getContentType()

    @property
    def isImage(self):
        return 'image' in self.context.getContentType()

    def hasThumbnailImage(self):
        if getattr(self.context, 'thumbnailImage', None) is None:
                return False
        imgfield = self.context.getField('thumbnailImage')
        #XXX test if the field is ok
        if imgfield is None or imgfield is '' or\
        imgfield.getSize(self.context) == (0, 0):
            return False
        return True

    @property
    def has_torrent(self):
        try:
            registry = getUtility(IRegistry)
            seeder = [i for i in getToolByName(self.context,
                        "portal_quickinstaller").listInstalledProducts()
                      if i['id']=='collective.seeder']
            if not seeder:
                return False
            torrent_dir = registry['collective.seeder.interfaces.ISeederSettings.safe_torrent_dir']
            torrentPath = os.path.join(torrent_dir, self.context.UID() + '_' +\
                            self.context.video_file.getFilename()) + '.torrent'
            if os.path.exists(torrentPath):
                return True
            else:
                return False
        except:
            return False


class flowplayerConfig(BrowserView):

    def transcoding(self, profile):
        if profile in self.transcode_profiles:
            if self.transcode_profiles[profile]['status'] == 0:
                return self.transcode_profiles[profile]['URL']
        return ''

    def __call__(self, request=None, response=None):

        self.request.response.setHeader("Content-type", "text/javascript")

        self.annotations = IAnnotations(self.context)
        self.transcode_profiles = self.annotations.get('plumi.transcode.profiles')
        if not self.transcode_profiles:
            self.transcode_profiles = {}
        return """
{
    'embedded': 'true',
    // common clip properties
    'clip': {
        'url': '%s',
    },
    'plugins': {
        // use youtube controlbar
        'controls': {
            'url': '%s/%%2B%%2Bresource%%2B%%2Bplumi.content.flowplayer/flowplayer.controls-3.2.1.swf'
            'height': 30,
            'backgroundColor': '#115233'
        }
    }
}
        """ % (self.transcoding('mp4'), self.portal_url, )
