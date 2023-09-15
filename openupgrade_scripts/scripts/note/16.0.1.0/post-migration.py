import logging
import random
import re
import string

import requests

from openupgradelib import openupgrade

from markupsafe import Markup
from odoo.addons.openupgrade_scripts.py_etherpad import EtherpadLiteClient

_logger = logging.getLogger(__name__)

def _pad_get(env):
    pad = {
        "server": env['ir.config_parameter'].sudo().get_param('pad.pad_server'),
        "key": env['ir.config_parameter'].sudo().get_param('pad.pad_key'),
    }
    myPad = EtherpadLiteClient(pad['key'], (pad['server'] or '') + '/api')
    return myPad


def _pad_get_content(env, pad, url):
    content = ''
    if url and pad:
        split_url = url.split('/p/')
        path = len(split_url) == 2 and split_url[1]
        try:
            content = pad.getHtml(path).get('html', '')
        except IOError:
            _logger.warning('Http Error: the credentials might be absent for url: "%s". Falling back.' % url)
            try:
                r = requests.get('%s/export/html' % url)
                r.raise_for_status()
            except Exception:
                _logger.warning("No pad found with url '%s'.", url)
            else:
                mo = re.search('<body>(.*)</body>', r.content.decode(), re.DOTALL)
                if mo:
                    content = mo.group(1)

    return Markup(content)


def _update_content_from_pad_to_note(env):
    if not openupgrade.column_exists(
        env.cr, "note_note", "note_pad_url"
    ):
        return
    pad = _pad_get(env)
    if pad:
        env.cr.execute(
            """
            SELECT id, note_pad_url FROM note_note
            WHERE note_pad_url IS NOT NULL
            """
        )
        for note_id, note_pad_url in env.cr.fetchall():
            note = env["note.note"].browse(note_id)
            note.memo = _pad_get_content(env, pad, note_pad_url)

@openupgrade.migrate()
def migrate(env, version):
    _update_content_from_pad_to_note(env)
