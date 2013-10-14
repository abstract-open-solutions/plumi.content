#-*- coding: utf-8 -*-

from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from plumi.content.browser.interfaces import IPlumiSettings


def get_settings():
    registry = getUtility(IRegistry)
    return registry.forInterface(IPlumiSettings)
