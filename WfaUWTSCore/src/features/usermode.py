###############################################################################
#
# Copyright (c) 2016 Wi-Fi Alliance
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#
###############################################################################

#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
import logging
from dbaccess import settingsdb
from dbaccess.usermodedb import UserModeService

class UserMode(object):
    """
    UserMode class deals with setting/getting settings pertaining to 
    usermodes.
    """
    
    def set_default_mode(self, mode):
        """
        Sets the default_user_mode setting the settings database to the 
        given parameter mode if mode is successfully validated against a set
        of modes provided by the user mode database.
        """
        updatethis = settingsdb.Settings(key='default_user_mode')
        with UserModeService() as ums, settingsdb.SettingsService(updatethis) as ss:
            umdao = ums.get_usermodeDAO()
            valid_modes = set(umdao.get_available_modes())
            if mode not in valid_modes:
                logging.error('Cannot set default user mode "%s" - unknown mode' % (mode))
                return -1
            ssdao = ss.get_settingsDAO()
            newsetting = settingsdb.Settings(key='default_user_mode', value=mode)
            ssdao.upsert_setting(newsetting)

    def get_default_mode(self):
        """
        Returns a string of the current default user mode from the settings
        database. If the setting for default_user_mode is not found then 
        precert is returned and the missing setting is logged as a warning.
        """
        getthis = settingsdb.Settings(key='default_user_mode')
        with settingsdb.SettingsService(getthis) as ss:
            ssdao = ss.get_settingsDAO()
            results = ssdao.get_setting_by_key(getthis)
            if len(results) == 0:
                logging.warn('Default user mode setting not found in DB')
                new_default = settingsdb.Settings(key='default_user_mode', value='precert')
                ssdao.upsert_setting(new_default)
                return 'precert'
            elif len(results) == 1:
                return results[0].value
            else:
                logging.warn('Settings database contains multiple entries for default_user_mode')
                return results[0].value

    def get_available_modes(self):
        """Returns a string list of available modes"""
        with UserModeService() as ums:
            umdao = ums.get_usermodeDAO()
            modes = umdao.get_available_modes()
        return ' '.join(modes)

    def get_mode_description(self, mode):
        """Returns the string description of the requested user mode"""
        with UserModeService() as ums:
            umdao = ums.get_usermodeDAO()
            description = umdao.get_mode_description(mode)
        return description
    
    def set_current_mode(self, mode):
        """
        Sets the current user mode and returns the value of the current user
        mode. If the mode is invalid, then it returns -1.
        """
        with UserModeService() as ums:
            umdao = ums.get_usermodeDAO()
            result = umdao.set_current_mode(mode)
        return result
    
    def get_current_mode(self):
        """Returns the string value of the current user mode"""
        with UserModeService() as ums, settingsdb.SettingsService() as ss:
            umdao = ums.get_usermodeDAO()
            sdao = ss.get_settingsDAO()
            current_mode = umdao.get_current_mode()
            if current_mode is None:
                request = settingsdb.Settings(key='default_user_mode')
                results = sdao.get_setting_by_key(request)
                default_mode = results[0].value
                if default_mode is None:
                    #database is missing a setting for default_user_mode
                    #this is not supposed to happen
                    default_mode = 'precert'
                umdao.set_current_mode(default_mode)
                current_mode = default_mode
        return current_mode
    
    def check_feature(self, feat):
        """
        Checks to see if the given feature is true or false for the current 
        user mode
        """
        with UserModeService() as ums:
            umdao = ums.get_usermodeDAO()
            result = umdao.check_feature(feat)
        return result
