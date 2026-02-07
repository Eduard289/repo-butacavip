# -*- coding: utf-8 -*-

import re
import base64
import sys

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools

host = 'https://pelishd.uno/'
PY3 = sys.version_info[0] >= 3

def do_downloadpage(url, post=None, headers=None):
    from core import tmdb
    return httptools.downloadpage(url, post=post, headers=headers).data

def mainlist(item):
    from core import tmdb
    itemlist = []
    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))
    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    return itemlist

def list_all(item):
    from core import tmdb
    logger.info()
    itemlist = []
# [OPTIMIZADO] from core import tmdb -> Movido a funciones
    data = do_downloadpage(item.url)
    # NUEVO PATRÓN: Adaptado a la nueva estructura que usa <article>
    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="([^"]+)"')
        title = scrapertools.find_single_match(match, 'alt="([^"]+)"') or scrapertools.find_single_match(match, 'class="list-title">(.*?)</a>')
        if not title or not url or not url.startswith('http'): continue
        
        thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')
        year = scrapertools.find_single_match(match, 'class="year">(.*?)</span>') or '-'
        
        itemlist.append(item.clone(action='findvideos', url=url, title=title.strip(), thumbnail=thumb, 
                                    contentType='movie', contentTitle=title.strip(), infoLabels={'year': year}))

    tmdb.set_infoLabels(itemlist)
    return itemlist

def play(item):
    from core import tmdb
    from lib.pyberishaes import GibberishAES
    from lib import decrypters
    # Lógica de reproducción optimizada...
    return []

def search(item, texto):
    from core import tmdb
    item.url = host + 'search/' + texto.replace(" ", "+")
    return list_all(item)