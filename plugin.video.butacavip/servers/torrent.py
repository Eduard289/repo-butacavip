
# -*- coding: utf-8 -*-
import urllib.parse
from platformcode import logger, platformtools

def get_video_url(page_url, url_referer=''):
    logger.info("server=torrent, procesando enlace para motor externo")
    video_urls = []
    
    # Preparamos el formato para el reproductor
    if page_url.startswith("magnet:"):
        video_urls.append(["magnet: [torrent]", page_url])
    else:
        video_urls.append([".torrent [torrent]", page_url])

    return video_urls

def play(item):
    logger.info("server=torrent, iniciando reproducción vía Elementum")
    
    # 1. Codificamos la URL del magnet o torrent
    media_url = urllib.parse.quote_plus(item.url)
    
    # 2. Creamos la instrucción para llamar a Elementum
    # Esta es la URL interna que Kodi entiende para abrir el motor
    url_elementum = "plugin://plugin.video.elementum/play?uri=%s" % media_url
    
    # 3. Lanzamos la reproducción
    platformtools.platform_play(url_elementum, item)