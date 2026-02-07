# -*- coding: utf-8 -*-
import sys
from platformcode import logger
# Importamos el módulo original para obtener sus datos
from modules import submnuctext

def submnu_news(item):
    """
    Esta función es un 'wrapper' (envoltorio).
    1. Llama al menú de novedades original.
    2. Recibe la lista completa.
    3. Elimina todo excepto las 3 últimas opciones.
    """
    logger.info()
    itemlist = []

    try:
        # 1. Obtenemos la lista completa del original
        # Usamos item.clone() para no modificar el objeto original por error
        lista_completa = submnuctext.submnu_news(item.clone())

        # 2. FILTRADO: Nos quedamos solo con los últimos 3 elementos
        # En Python, [-3:] significa "desde el antepenúltimo hasta el final"
        if len(lista_completa) >= 3:
            itemlist = lista_completa[-3:]
        else:
            # Si por alguna razón la lista es muy corta, la mostramos entera para no dar error
            itemlist = lista_completa

    except Exception as e:
        logger.error("Error generando menú custom: %s" % str(e))

    return itemlist