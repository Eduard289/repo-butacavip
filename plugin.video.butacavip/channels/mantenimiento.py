# -*- coding: utf-8 -*-
import os
import xbmc
import xbmcgui
import xbmcvfs
from platformcode import logger
from core.item import Item

def limpiar_todo(item):
    """
    Limpia la caché, temporales y paquetes de instalación de Kodi.
    """
    # Rutas estándar de basura en Kodi
    rutas = [
        xbmcvfs.translatePath("special://home/cache/"),
        xbmcvfs.translatePath("special://home/temp/"),
        xbmcvfs.translatePath("special://home/addons/packages/")
    ]
    
    contador = 0
    
    for ruta in rutas:
        if os.path.exists(ruta):
            archivos = os.listdir(ruta)
            for archivo in archivos:
                # No borramos carpetas, solo archivos sueltos
                ruta_completa = os.path.join(ruta, archivo)
                try:
                    if os.path.isfile(ruta_completa):
                        os.remove(ruta_completa)
                        contador += 1
                except:
                    logger.error("No se pudo borrar: " + ruta_completa)

    # Mostrar resultado
    dialog = xbmcgui.Dialog()
    if contador > 0:
        dialog.notification("ButacaVIP", "[COLOR green]Limpieza completada:[/COLOR] %d archivos borrados" % contador, xbmcgui.NOTIFICATION_INFO, 5000)
        # Opcional: Sonido de éxito
        xbmc.executebuiltin('PlayMedia(special://xbmc/media/Streams/success.wav)')
    else:
        dialog.notification("ButacaVIP", "Tu sistema ya está limpio ✨", xbmcgui.NOTIFICATION_INFO, 3000)
    
    return True