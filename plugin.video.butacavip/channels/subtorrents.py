# -*- coding: utf-8 -*-

import sys
import re
import os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools

# --- OPTIMIZACIÓN: Variables globales vacías ---
PY3 = False
if sys.version_info[0] >= 3: PY3 = True

LINUX = False
BR = False
BR2 = False
_INIT_DONE = False
balandroresolver = None
tmdb = None

host = 'https://www1.subtorrents.zip/'

# ~ por si viene de enlaces guardados
ant_hosts = ['https://www.subtorrents.nl/', 'https://www.subtorrents.ch/', 'https://www.subtorrents.nz/',
             'https://www.subtorrents.in/', 'https://www.subtorrents.li/', 'https://www.subtorrents.do/',
             'https://www.subtorrents.re/']

def _initialize():
    from core import tmdb
    global LINUX, BR, BR2, _INIT_DONE, balandroresolver, tmdb
    if _INIT_DONE: return
    
    # Carga perezosa de TMDB
# [OPTIMIZADO] from core import tmdb as tmdb_module -> Movido a funciones
    tmdb = tmdb_module

    if PY3:
        try:
           import xbmc
           if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
        except: pass
    try:
       if LINUX:
           try:
              from lib import balandroresolver2 as balandroresolver
              BR2 = True
           except: pass
       else:
           if PY3:
               from lib import balandroresolver as balandroresolver_mod
               balandroresolver = balandroresolver_mod
               BR = True
           else:
              try:
                 from lib import balandroresolver2 as balandroresolver
                 BR2 = True
              except: pass
    except:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
    _INIT_DONE = True

def do_downloadpage(url, post=None, headers=None):
    from core import tmdb
    _initialize()
    for ant in ant_hosts: url = url.replace(ant, host)
    return httptools.downloadpage(url, post=post, headers=headers).data

def mainlist(item):
    from core import tmdb
    return mainlist_pelis(item)

def mainlist_pelis(item):
    from core import tmdb
    logger.info()
    itemlist = []
    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-subtituladas/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=estrenos', search_type = 'movie', text_color='cyan' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=puntuacion', search_type = 'movie' ))
    return itemlist

def list_all(item):
    from core import tmdb
    _initialize()
    logger.info()
    itemlist = []
    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    matches = scrapertools.find_multiple_matches(data, '<div class=\"relative\">(.*?)</div></div></div>')
    for match in matches:
        url = scrapertools.find_single_match(match, '<a href=\"(.*?)\"')
        title = scrapertools.find_single_match(match, 'alt=\"(.*?)\"').strip()
        if not url or not title: continue
        thumb = scrapertools.find_single_match(match, 'src=\"(.*?)\"')
        year = scrapertools.find_single_match(match, '<span class=\"year\">(.*?)</span>')
        if not year: year = '-'
        title_clean = title.replace('Subtitulada', '').replace('Castellano', '').strip()
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title_clean, infoLabels={'year': year} ))
    tmdb.set_infoLabels(itemlist)
    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class=\"next page-numbers\" href=\"(.*?)\"')
        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))
    return itemlist

def findvideos(item):
    from core import tmdb
    logger.info()
    itemlist = []
    data = do_downloadpage(item.url)
    matches = scrapertools.find_multiple_matches(data, 'data-url=\"(.*?)\".*?data-lang=\"(.*?)\"')
    for url_b64, lang_code in matches:
        import base64
        url = base64.b64decode(url_b64).decode("utf-8")
        lang = 'Vose' if lang_code == '1' else 'Esp'
        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='torrent', language=lang, quality='HD' ))
    return itemlist

def play(item):
    from core import tmdb
    logger.info()
    itemlist = []
    itemlist.append(item.clone(url = item.url, server = 'torrent'))
    return itemlist

def search(item, texto):
    from core import tmdb
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       return []