# -*- coding: utf-8 -*-
from platformcode import config, logger
from core.item import Item
from core import tmdb
import os

def mainlist(item):
    logger.info("Entrando en Estrenos Digitales VIP")
    itemlist = []
    
    # --- IMÁGENES ONLINE COLORIDAS (Con truco ?reload=2 para forzar actualización) ---
    
    # 1. Alquiler: Ticket Amarillo/Naranja (Muy visual)
    img_alquiler = "https://cdn-icons-png.flaticon.com/512/2503/2503508.png?reload=2"
    
    # 2. Venta 4K: ¡NUEVO! Cinta de cine con colores vivos (Rojo/Azul/Amarillo)
    # Sustituye al "reloj oscuro" anterior
    img_venta    = "https://cdn-icons-png.flaticon.com/512/3163/3163478.png?reload=2"
    
    # Opción 1: ALQUILER
    itemlist.append(item.clone( 
        action='listado_digital',
        title='[COLOR lime]Estrenos alta calidad digital[/COLOR]',
        monetization_types='rent', 
        thumbnail=img_alquiler,  
        icon=img_alquiler,       
        plot='Películas formato de alta calidad  digital.' 
    ))

    # Opción 2: VENTA / COMPRA
    itemlist.append(item.clone( 
        action='listado_digital',
        title='[COLOR yellow]Estrenos en calidad  4K/HD[/COLOR]',
        monetization_types='buy', 
        thumbnail=img_venta,
        icon=img_venta,
        plot='Películas disponibles 4k/HD.' 
    ))

    return itemlist

def listado_digital(item):
    if not item.page: item.page = 1
    
    # Filtros para TMDB
    discover_params = {
        'url': 'discover/movie',
        'language': 'es-ES',
        'page': item.page,
        'sort_by': 'primary_release_date.desc', 
        'watch_region': 'ES',
        'with_watch_monetization_types': item.monetization_types,
        'vote_count.gte': 50 
    }
    
    try:
        tmdb_obj = tmdb.Tmdb(discover=discover_params)
        elementos = tmdb_obj.get_list_resultados()
        return lista(item, elementos)
        
    except Exception as e:
        logger.error("Error en Estrenos Digitales: " + str(e))
        return []

# --- Función auxiliar para pintar los resultados ---

def lista(item, elementos):
    itemlist = []
    if not item.page: item.page = 1

    for elemento in elementos:
        titulo = elemento.get('title', elemento.get('name', ''))
        
        itemlist.append(item.clone( 
            channel='search', 
            action='search', 
            buscando=titulo, 
            title=titulo, 
            search_type='movie', 
            contentType='movie', 
            contentTitle=titulo, 
            infoLabels={'tmdb_id': elemento['id']},
            thumbnail=elemento.get('thumbnail', ''),
            fanart=elemento.get('fanart', '')
        ))

    tmdb.set_infoLabels(itemlist)

    if len(itemlist) > 0:
        itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, text_color='coral' ))

    return itemlist