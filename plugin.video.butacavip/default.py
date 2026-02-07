# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui

# ---------------------------------------------------------------------------------------
#  BLOQUE DE COMPROBACIÓN DE ELEMENTUM (Con instrucciones)
# ---------------------------------------------------------------------------------------
def verificar_elementum():
    # Comprobamos si Elementum está instalado en el sistema
    if not xbmc.getCondVisibility('System.HasAddon(plugin.video.elementum)'):
        # Texto del aviso con formato Kodi ([B]=Negrita, [COLOR]=Color, [CR]=Salto de línea)
        linea1 = "[B]⚠️ AVISO IMPORTANTE: FALTA ELEMENTUM[/B][CR][CR]"
        linea2 = "Este addon utiliza tecnología P2P. Para ver los enlaces Torrent necesitas instalar el motor [COLOR yellow][B]Elementum[/B][/COLOR].[CR][CR]"
        linea3 = "📥 Descarga la versión 'All-in-One' desde su web oficial:[CR]"
        linea4 = "[COLOR deepskyblue]https://elementum.org[/COLOR]"
        
        # Mostramos la ventana
        dialog = xbmcgui.Dialog()
        dialog.ok("ButacaVip - Requisito Faltante", linea1 + linea2 + linea3 + linea4)

# Ejecutamos la verificación antes de cargar nada más
verificar_elementum()
# ---------------------------------------------------------------------------------------

if sys.version_info[0] < 3:
    PY3 = False
    import urllib2
else:
    PY3 = True
    import urllib.error as urllib2


import os
import traceback
from platformcode import config

if config.get_setting('PY3') == '': config.set_setting('PY3', PY3)


from platformcode import logger, platformtools, updater
from core.item import Item
from core import servertools
from platformcode.config import WebErrorException


txt_pys = '[COLOR yellow]Película y/ó Serie[/COLOR] texto a buscar ...'
txt_pel = '[COLOR deepskyblue]Película[/COLOR] texto a buscar ...'
txt_ser = '[COLOR hotpink]Serie[/COLOR] texto a buscar ...'
txt_doc = '[COLOR cyan]Documental[/COLOR] texto a buscar ...'
txt_tor = '[COLOR blue]Torrent[/COLOR] [COLOR yellow]Película y/ó Serie[/COLOR] texto a buscar ...'
txt_dor = '[COLOR firebrick]Dorama[/COLOR] texto a buscar ...'
txt_ani = '[COLOR springgreen]Anime[/COLOR] texto a buscar ...'
txt_lis = '[COLOR greenyellow]Lista[/COLOR] texto a buscar ...'
txt_per = '[COLOR tan]Persona[/COLOR] texto a buscar ...'
txt_vid = '[COLOR darkorange]+18 Vídeo[/COLOR] texto a buscar ...'
txt_yt  = '[COLOR darksalmon]Youtube[/COLOR] texto a buscar ...'


# ~ Obtener parámetros ejecución
logger.info('[COLOR blue]Starting with %s[/COLOR]' % sys.argv[1])

if sys.argv[2]: item = Item().fromurl(sys.argv[2])
else: item = Item(channel='mainmenu', action='mainlist')


sys.path.append(os.path.join(config.get_runtime_path(), 'lib'))


# ~ Establecer si channel es un canal ó un módulo
tipo_channel = ''

if item.channel == '' or item.action == '': logger.info('Empty channel/action, Nothing to do')
else:
    # ~ channel puede ser un canal ó un módulo
    path = os.path.join(config.get_runtime_path(), 'channels', item.channel + ".py")
    if os.path.exists(path): tipo_channel = 'channels.'
    else:
        path = os.path.join(config.get_runtime_path(), 'modules', item.channel + ".py")
        if os.path.exists(path): tipo_channel = 'modules.'
        else: tipo_channel = 'modules.'


# ~ Ejecutar según parámetros
if tipo_channel != '':
    try:
        canal = __import__(tipo_channel + item.channel, fromlist=[''])

        # ~ findvideos se considera reproducible y debe acabar haciendo play (ó play_fake en su defecto)
        if item.action == 'findvideos':
            if hasattr(canal, item.action): itemlist = canal.findvideos(item)
            else: itemlist = servertools.find_video_items(item)

            platformtools.play_from_itemlist(itemlist, item)
        else:
            # ~ search pide el texto a buscar antes de llamar a la rutina del canal (pasar item.buscando para no mostrar diálogo)
            if item.action == 'search':
                if item.buscando != '': tecleado = item.buscando
                else:
                    last_search = config.get_last_search(item.search_type)
                    txt_search = txt_pys

                    if item.search_type == 'all':
                        if item.search_pop:
                            last_search = config.get_last_search('list')
                            txt_search = txt_lis
                        elif item.search_video:
                            last_search = config.get_last_search('video')
                            txt_search = txt_vid
                        elif item.search_special == 'torrent':
                            last_search = config.get_last_search('torrent')
                            txt_search = txt_tor
                        elif item.search_special == 'dorama':
                            last_search = config.get_last_search('dorama')
                            txt_search = txt_dor
                        elif item.search_special == 'anime':
                            last_search = config.get_last_search('anime')
                            txt_search = txt_ani
                        elif item.search_special == 'youtube':
                            last_search = config.get_last_search('youtube')
                            txt_search = txt_yt
                        else: last_search = config.get_last_search('all')

                    elif item.search_type == 'movie':
                        if item.search_video:
                            last_search = config.get_last_search('video')
                            txt_search = txt_vid
                        else: txt_search = txt_pel

                    elif item.search_type == 'tvshow': txt_search = txt_ser
                    elif item.search_type == 'documentary': txt_search = txt_doc
                    elif item.search_type == 'person': txt_search = txt_per

                    elif item.search_special == 'torrent': txt_search = txt_tor
                    elif item.search_special == 'dorama': txt_search = txt_dor
                    elif item.search_special == 'anime': txt_search = txt_ani
                    elif item.search_special == 'youtube': txt_search = txt_yt

                    else:
                        if item.search_video:
                            last_search = config.get_last_search('video')
                            txt_search = txt_vid

                    tecleado = platformtools.dialog_input(last_search, txt_search)

                if tecleado is not None and tecleado != '':
                    itemlist = canal.search(item, tecleado)

                    if item.buscando == '':
                        last_bus = item.search_type
                        if item.search_type == 'all':
                            if item.search_pop: last_bus = 'list'
                            elif item.search_video: last_bus = 'video'
                            elif item.search_special == 'torrent': last_bus = 'torrent'
                            elif item.search_special == 'dorama': last_bus = 'dorama'
                            elif item.search_special == 'anime': last_bus = 'anime'
                            elif item.search_special == 'youtube': last_bus = 'youtube'
                            else: last_bus = 'all'
                        elif item.search_type == 'movie':
                            if item.search_video: last_bus = 'video'
                            else: last_bus = 'movie'
                        elif item.search_pop: last_bus = 'list'
                        elif item.search_video: last_bus = 'video'
                        elif item.search_type == 'person': last_bus = 'person'
                        elif item.search_special == 'torrent': last_bus = 'torrent'
                        elif item.search_special == 'dorama': last_bus = 'dorama'
                        elif item.search_special == 'anime': last_bus = 'anime'
                        elif item.search_special == 'youtube': last_bus = 'youtube'

                        if last_bus: config.set_last_search(last_bus, tecleado)
                else:
                    itemlist = []
                    item.folder = False
                    itemlist = False

            # ~ Cualquier otra acción se ejecuta en el canal
            else:
                if hasattr(canal, item.action):
                    func = getattr(canal, item.action)
                    itemlist = func(item)
                    
                    # ------------------------------------------------------------------
                    # ZONA DE INYECCIÓN BUTACAVIP (LIMPIA - SIN SAGAS EN MENU PRINCIPAL)
                    # ------------------------------------------------------------------
                    if item.channel == 'mainmenu' and item.action == 'mainlist' and isinstance(itemlist, list):
                        try:
                            # --- 1. PREPARAR IMÁGENES ---
                            ruta_img_estrenos = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'estrenos.png')
                            
                            # --- 2. DEFINIR ELEMENTOS --
                            # Botón ESTRENOS
                            boton_estrenos = Item(channel="estrenos_digitales", 
                                                  action="mainlist", 
                                                  title="Estrenos ButacaVIP", 
                                                  thumbnail=ruta_img_estrenos, 
                                                  plot="[B]Alta calidad:[/B] Selección de los últimos estrenos en cines.")

                            # Botón Mantenimiento
                            boton_mantenimiento = Item(channel="mantenimiento", 
                                                 action="limpiar_todo", 
                                                 title="[COLOR orange][B]🛠️ Mantenimiento VIP[/B][/COLOR]", 
                                                 thumbnail="https://i.imgur.com/Q6XzY8n.png",
                                                 plot="Herramientas para limpiar caché.")

                            # --- 3. INYECCIÓN ---
                            
                            # A) Colocar ESTRENOS debajo de "v2.0"
                            idx_v2 = -1
                            for i, it in enumerate(itemlist):
                                if "v2.0" in it.title or "Edición" in it.title:
                                    idx_v2 = i
                                    break
                            
                            if idx_v2 != -1:
                                itemlist.insert(idx_v2 + 1, boton_estrenos)
                                itemlist.insert(idx_v2 + 2, separador)

                            # B) Mantenimiento al final
                            itemlist.append(boton_mantenimiento)

                        except:
                            logger.error("Error inyectando menú ButacaVIP")
                    # ------------------------------------------------------------------

                else:
                    logger.info('Action Not Found in channel')
                    itemlist = [] if item.folder else False

            if type(itemlist) == list:
                logger.info('Renderizar itemlist')
                platformtools.render_items(itemlist, item)

            elif itemlist == None:
                logger.info('Sin renderizar')
                platformtools.render_no_items()

            elif itemlist == True: logger.info('El canal ha ejecutado Correctamente una acción.')
            elif itemlist == False:logger.info('El canal ha ejecutado una acción que no devuelve listado.') 

    except urllib2.URLError as e:
        logger.error(traceback.format_exc())
        if hasattr(e, 'reason'):
            logger.error("Razon del error: %s" % str(e.reason))
            platformtools.dialog_ok(config.__addon_name, "No se puede Conectar con el Servidor")
        elif hasattr(e, 'code'):
            logger.error("Codigo de error HTTP: %d" % e.code)
            platformtools.dialog_ok(config.__addon_name, "Error HTTP %d" % e.code)

    except WebErrorException as e:
        logger.error(traceback.format_exc())
        if item.contentType in ['movie', 'tvshow', 'season', 'episode'] and config.get_setting('tracking_weberror_dialog', default=True):
            if item.action == 'findvideos': platformtools.play_fake()
            item_search = platformtools.dialogo_busquedas_por_fallo_web(item)
            if item_search is not None: platformtools.itemlist_update(item_search)
        else:
            platformtools.dialog_ok(config.__addon_name, "La Web asociada al Canal parece no estar disponible.")

    except:
        logger.error(traceback.format_exc())
        platformtools.dialog_ok(config.__addon_name, "Error Inesperado. Consulte el Log.")

logger.info('[COLOR blue]Ending with %s[/COLOR]' % sys.argv[1])