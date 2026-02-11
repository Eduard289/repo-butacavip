import sys
import xbmc
import xbmcgui
import os
import traceback

# ---------------------------------------------------------------------------------------
#  BLOQUE DE COMPROBACIÓN DE ELEMENTUM
# ---------------------------------------------------------------------------------------
def verificar_elementum():
    if not xbmc.getCondVisibility('System.HasAddon(plugin.video.elementum)'):
        linea1 = "[B]⚠️ AVISO IMPORTANTE: FALTA ELEMENTUM[/B][CR][CR]"
        linea2 = "Este addon utiliza tecnología P2P. Para ver los enlaces Torrent necesitas instalar el motor [COLOR yellow][B]Elementum[/B][/COLOR].[CR][CR]"
        linea3 = "📥 Descarga la versión 'All-in-One' desde su web oficial:[CR]"
        linea4 = "[COLOR deepskyblue]https://elementum.org[/COLOR]"
        dialog = xbmcgui.Dialog()
        dialog.ok("ButacaVip - Requisito Faltante", linea1 + linea2 + linea3 + linea4)

verificar_elementum()

# ---------------------------------------------------------------------------------------
#  COMPATIBILIDAD PYTHON 2/3
# ---------------------------------------------------------------------------------------
if sys.version_info[0] < 3:
    PY3 = False
    import urllib2
else:
    PY3 = True
    import urllib.error as urllib2

from platformcode import config
if config.get_setting('PY3') == '': config.set_setting('PY3', PY3)

from platformcode import logger, platformtools
from core.item import Item
from core import servertools
from platformcode.config import WebErrorException

# Textos de búsqueda
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

logger.info('[COLOR blue]Starting with %s[/COLOR]' % sys.argv[1])

if sys.argv[2]: item = Item().fromurl(sys.argv[2])
else: item = Item(channel='mainmenu', action='mainlist')

sys.path.append(os.path.join(config.get_runtime_path(), 'lib'))

tipo_channel = ''
if item.channel != '' and item.action != '':
    path = os.path.join(config.get_runtime_path(), 'channels', item.channel + ".py")
    if os.path.exists(path): tipo_channel = 'channels.'
    else: tipo_channel = 'modules.'

if tipo_channel != '':
    try:
        canal = __import__(tipo_channel + item.channel, fromlist=[''])

        if item.action == 'findvideos':
            if hasattr(canal, item.action): itemlist = canal.findvideos(item)
            else: itemlist = servertools.find_video_items(item)
            platformtools.play_from_itemlist(itemlist, item)
        
        elif item.action == 'search':
            tecleado = item.buscando if item.buscando != '' else None
            if tecleado is None:
                txt_search = txt_pys # Simplificado para el ejemplo
                tecleado = platformtools.dialog_input(config.get_last_search('all'), txt_search)
            
            if tecleado:
                itemlist = canal.search(item, tecleado)
                config.set_last_search('all', tecleado)
            else:
                itemlist = False

        else:
            if hasattr(canal, item.action):
                func = getattr(canal, item.action)
                itemlist = func(item)
                
                # --- ZONA DE INYECCIÓN BUTACAVIP ---
                if item.channel == 'mainmenu' and item.action == 'mainlist' and isinstance(itemlist, list):
                    try:
                        ruta_img_estrenos = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'estrenos.png')
                        
                        boton_estrenos = Item(channel="estrenos_digitales", 
                                             action="mainlist", 
                                             title="[COLOR yellow]Estrenos ButacaVIP[/COLOR]", 
                                             thumbnail=ruta_img_estrenos, 
                                             plot="[B]Alta calidad:[/B] Selección de los últimos estrenos.")

                        boton_mantenimiento = Item(channel="mantenimiento", 
                                                 action="limpiar_todo", 
                                                 title="[COLOR orange][B]🛠️ Mantenimiento VIP[/B][/COLOR]", 
                                                 thumbnail="https://i.imgur.com/Q6XzY8n.png",
                                                 plot="Herramientas para limpiar caché.")

                        # Inyectamos los botones
                        itemlist.insert(0, boton_estrenos) # Lo ponemos arriba del todo para que lo veas rápido
                        itemlist.append(boton_mantenimiento)
                    except:
                        logger.error("Error inyectando menú ButacaVIP")

            else:
                itemlist = [] if item.folder else False

        if isinstance(itemlist, list):
            platformtools.render_items(itemlist, item)
        elif itemlist is None:
            platformtools.render_no_items()

    except Exception:
        logger.error(traceback.format_exc())
        platformtools.dialog_ok("ButacaVip", "Error Inesperado. Consulte el Log.")

logger.info('[COLOR blue]Ending with %s[/COLOR]' % sys.argv[1])
