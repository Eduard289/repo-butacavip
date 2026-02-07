# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import json
import time
from datetime import datetime

# Importamos httptools de forma segura (clave para que funcionen las imágenes dinámicas)
try:
    from core import httptools
except ImportError:
    pass

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen

from platformcode import config, logger, platformtools, updater
from core.item import Item
from core import channeltools, scrapertools

# Definimos PY3 como True por defecto
PY3 = True

fanart = os.path.join(config.get_runtime_path(), 'fanart.jpg')

color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

current_year = int(datetime.today().year)
current_month = int(datetime.today().month)


team = False
if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developergenres.py')): team = True
elif os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertest.py')): team = True
elif os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertools.py')): team = True

config.set_setting('developer_team', team)


avisar = False
kver = str(xbmc.getInfoLabel('System.BuildVersion'))

if not kver:
    kver = 0
    avisar = True
else:
    if kver.startswith('18.'): kver = 18
    elif kver.startswith('19.'): kver = 19
    elif kver.startswith('20.'): kver = 20
    elif kver.startswith('21.'): kver = 21
    elif kver.startswith('22.'): kver = 22
    elif kver.startswith('23.'): kver = 23
    elif kver.startswith('24.'): kver = 24
    else: 
        try:
            kver = int(kver.split('.')[0])
        except:
            kver = 0

kver = int(kver)

if avisar:
    if config.get_setting('developer_mode', default=False):
        if config.get_setting('developer_team'):
            platformtools.dialog_notification(config.__addon_name + ' Media Center', '[COLOR red][B]Versión/Release Desconocida[/COLOR][/B]')


config.set_setting('kver', kver)
config.set_setting('PY3', True)
config.set_setting('ses_pin', False)


con_incidencias = ''
no_accesibles = ''
con_problemas = ''

# Lectura de dominios
try:
    file_path = os.path.join(config.get_runtime_path(), 'dominios.txt')
    with open(file_path, 'r', encoding='utf-8') as f:
        txt_status = f.read()
except Exception:
    txt_status = ''

if txt_status:
    # ~ Incidencias
    bloque = scrapertools.find_single_match(txt_status, 'SITUACION CANALES(.*?)CANALES TEMPORALMENTE DES-ACTIVADOS')
    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")
    for match in matches:
        match = match.strip()
        if '[COLOR moccasin]' in match: 
            con_incidencias += '[B' + match + '/I][/B][/COLOR][CR]'

    # ~ No Accesibles
    bloque = scrapertools.find_single_match(txt_status, 'CANALES PROBABLEMENTE NO ACCESIBLES(.*?)ULTIMOS CAMBIOS DE DOMINIOS')
    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")
    for match in matches:
        match = match.strip()
        if '[COLOR moccasin]' in match: 
            no_accesibles += '[B' + match + '/I][/B][/COLOR][CR]'

    # ~ Con Problemas
    bloque = scrapertools.find_single_match(txt_status, 'CANALES CON PROBLEMAS(.*?)$')
    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")
    for match in matches:
        match = match.strip()
        if '[COLOR moccasin]' in match: 
            con_problemas += '[B' + match + '/I][/B][/COLOR][CR]'


# --- DEFINICIÓN DE CONTEXT MENUS ---

context_desarrollo = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR goldenrod][B]Miscelánea[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_help_miscelanea'})
tit = '[COLOR %s]Ajustes categoría Team[/COLOR]' % color_exec
context_desarrollo.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_menu = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_menu.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR fuchsia][B]Preferencias Play[/B][/COLOR]'
context_menu.append({'title': tit, 'channel': 'helper', 'action': 'show_play_parameters'})
tit = '[COLOR powderblue][B]Preferencias Buscar[/B][/COLOR]'
context_menu.append({'title': tit, 'channel': 'helper', 'action': 'show_help_parameters_search'})
tit = '[COLOR %s]Ajustes categorías Menú, Play y Buscar[/COLOR]' % color_exec
context_menu.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_buscar = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR fuchsia][B]Preferencias Play[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_play_parameters'})
tit = '[COLOR powderblue][B]Preferencias Buscar[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_parameters_search'})
tit = '[COLOR darkcyan][B]Preferencias Proxies[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_prx_parameters'})
tit = '[COLOR bisque]Gestión Dominios[/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR darkorange][B]Quitar Dominios Memorizados[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})
tit = '[COLOR gold][B]Qué Canales No Intervienen[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'channels_no_searchables'})
tit = '[COLOR gray][B]Qué Canales están Desactivados[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'filters', 'action': 'no_actives'})
tit = '[COLOR yellow][B]Búsquedas Solo en ...[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included'})

if config.get_setting('search_included_all', default=''):
    tit = '[COLOR indianred][B]Quitar Búsquedas Solo en ...[/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included_del'})

tit = '[COLOR greenyellow][B]Excluir Canales[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded'})

if config.get_setting('search_excludes_all', default=''):
    tit = '[COLOR violet][B]Quitar Canales Excluidos[/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

if config.get_setting('search_excludes_movies', default=''):
    tit = '[B][COLOR deepskyblue]Películas [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_movies'})

if config.get_setting('search_excludes_tvshows', default=''):
    tit = '[B][COLOR hotpink]Series [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_tvshows'})

if config.get_setting('search_excludes_documentaries', default=''):
    tit = '[B][COLOR cyan]Documentales [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_documentaries'})

if config.get_setting('search_excludes_torrents', default=''):
    tit = '[B][COLOR blue]Torrents [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_torrents'})

if config.get_setting('search_excludes_mixed', default=''):
    tit = '[B][COLOR teal]Películas y/ó Series [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_mixed'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_buscar.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_list_proxies
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR %s][B]Información Búsquedas[/B][/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_search'})
tit = '[COLOR %s]Ajustes categorías Canales, Dominios, Play, Proxies y Buscar[/COLOR]' % color_exec
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_generos = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_generos.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_infor
context_generos.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_list_proxies
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR %s]Ajustes categorías Menú, Canales, Dominios y Proxies[/COLOR]' % color_exec
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_proxy_channels = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_proxy_channels.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_list_proxies
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR %s]Ajustes categorías Menú, Canales, Dominios y Proxies[/COLOR]' % color_exec
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_cfg_search = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_cfg_search.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR %s]Ajustes categoría Menú[/COLOR]' % color_exec
context_cfg_search.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_torrents = []
tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

if config.get_setting('cliente_torrent') == 'Seleccionar' or config.get_setting('cliente_torrent') == 'Ninguno':
    tit = '[COLOR %s][B]Información Motores Torrent[/B][/COLOR]' % color_infor
    context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_help_torrents'})

tit = '[COLOR %s][B]Motores torrents instalados[/B][/COLOR]' % color_avis
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_clients_torrent'})
tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_torrents.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_list_proxies
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR %s]Ajustes categorías Canales, Dominios, Proxies y Torrents[/COLOR]' % color_exec
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_parental = []
tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

if config.get_setting('adults_password'):
    tit = '[COLOR %s][B]Eliminar Pin Parental[/B][/COLOR]' % color_adver
    context_parental.append({'title': tit, 'channel': 'actions', 'action': 'adults_password_del'})
else:
    tit = '[COLOR %s][B]Información Parental[/B][/COLOR]' % color_infor
    context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_help_adults'})
    tit = '[COLOR %s][B]Establecer Pin Parental[/B][/COLOR]' % color_avis
    context_parental.append({'title': tit, 'channel': 'actions', 'action': 'adults_password'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_parental.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_list_proxies
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR %s]Ajustes categorías Canales, Parental, Dominios y Proxies[/COLOR]' % color_exec
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_desactivados = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_desactivados.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_desactivados.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR %s]Ajustes categorías Menú, Dominios y Canales[/COLOR]' % color_exec
context_desactivados.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_preferidos = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_preferidos.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR %s][B]Información Preferidos[/B][/COLOR]' % color_infor
context_preferidos.append({'title': tit, 'channel': 'helper', 'action': 'show_help_tracking'})
tit = '[COLOR %s][B]Comprobar Nuevos Episodios[/B][/COLOR]' % color_adver
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'comprobar_nuevos_episodios'})
tit = '[COLOR %s][B]Eliminar Todos los Preferidos[/B][/COLOR]' % color_alert
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'manto_tracking_dbs'})
tit = '[COLOR %s]Ajustes categorías Menú, Dominios y Preferidos[/COLOR]' % color_exec
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_descargas = []
tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_descargas.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_descargas.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR %s][B]Información Descargas[/B][/COLOR]' % color_adver
context_descargas.append({'title': tit, 'channel': 'helper', 'action': 'show_help_descargas'})
tit = '[COLOR %s][B]Ubicación Descargas[/B][/COLOR]' % color_infor
context_descargas.append({'title': tit, 'channel': 'downloads', 'action': 'show_folder_downloads'})
tit = '[COLOR %s][B]Eliminar Todas las Descargas[/B][/COLOR]' % color_alert
context_descargas.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_downloads'})
tit = '[COLOR %s]Ajustes categoría Menú, Dominios y Descargas[/COLOR]' % color_exec
context_descargas.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_config = []
tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})
tit = '[COLOR bisque]Gestión Dominios[/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})
tit = '[COLOR %s][B]Últimos Cambios Dominios[/B][/COLOR]' % color_exec
context_config.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR darkorange][B]Quitar Dominios Memorizados[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})
tit = '[COLOR green][B]Información Plataforma[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_plataforma'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR olive][B]Limpiezas[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_limpiezas'})
tit = '[COLOR orange][B]Borrar Carpeta Caché[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_cache'})
tit = '[COLOR %s][B]Sus Ajustes Personalizados[/B][/COLOR]' % color_avis
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_sets'})
tit = '[COLOR %s]Cookies Actuales[/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_cook'})
tit = '[COLOR %s][B]Eliminar Cookies[/B][/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_cookies'})
tit = '[COLOR %s]Sus Advanced Settings[/COLOR]' % color_adver
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_advs'})
tit = '[COLOR fuchsia][B]Eliminar Advanced Settings[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_advs'})
tit = '[COLOR mediumaquamarine][B]Restablecer Parámetros Internos[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_params'})

context_usual = []
tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})
tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})
tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_usual.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_list_proxies
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})
tit = '[COLOR %s]Ajustes categorías Canales, Dominios y Proxies[/COLOR]' % color_exec
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


# ========================================================================================
# FUNCIÓN DE ESTRENOS DINÁMICOS (ALEATORIA)
# ========================================================================================
def get_cartelera_dinamica(item):
    """
    Descarga la cartelera y muestra 3 películas AL AZAR cada vez.
    """
    import random # Importamos la librería del azar
    
    lista_estrenos = []
    
    # API Key
    api_key = config.get_setting('tmdb_api')
    if not api_key: api_key = '5c88939574e202d8432edcb638e08e10'
    
    # Pedimos la página 1 de cartelera (trae 20 películas)
    url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=%s&language=es-ES&page=1' % api_key
    
    try:
        # Usamos httptools
        resp = httptools.downloadpage(url)
        
        if resp.data:
            data = json.loads(resp.data)
            results = data.get('results', [])
            
            # --- EL TRUCO DE MAGIA ---
            # Si hay resultados, los barajamos aleatoriamente
            if results:
                random.shuffle(results)
            
            # Ahora cogemos las 3 primeras de la lista barajada
            # (A veces saldrá Dune, otras veces Sonic, otras veces otra...)
            for peli in results[:3]:
                titulo = peli.get('title', 'Pelicula')
                
                # Imágenes (usamos calidad w500 para cargar rápido)
                poster = "https://image.tmdb.org/t/p/w500" + peli.get('poster_path', '')
                backdrop = "https://image.tmdb.org/t/p/original" + peli.get('backdrop_path', '')
                sinopsis = peli.get('overview', '')
                
                # Creamos el item
                it = item.clone(
                    channel='search',
                    action='search',
                    title='[B][COLOR gold]★ SUGERENCIA:[/COLOR] %s[/B]' % titulo,
                    thumbnail=poster,
                    fanart=backdrop if peli.get('backdrop_path') else fanart,
                    plot=sinopsis,
                    buscando=titulo, 
                    contentTitle=titulo,
                    contentType='movie',
                    folder=True
                )
                lista_estrenos.append(it)
                
    except Exception as e:
        logger.error("Error obteniendo cartelera dinámica: %s" % str(e))
        
    return lista_estrenos

def mainlist(item):
    logger.info()
    itemlist = []
    item.category = config.__addon_name

    # --- VARIABLE PARA LA IMAGEN TRANSPARENTE ---
    img_transparente = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'transparent.png')

    # --- FUNCIÓN SEPARADOR CORREGIDA ---
    def add_separator():
        itemlist.append(item.clone(
            action='',
            title='[COLOR dimgray]──────────────────────────────────────────[/COLOR]',
            thumbnail=img_transparente,
            folder=False
        ))

    # --- MODO DESARROLLADOR ---
    if config.get_setting('developer_mode', default=False):
        titulo = '[B]Desarrollo[/B]'
        if not config.get_setting('developer_team'): titulo = '[B]Falso Desarrollo[/B]'
        itemlist.append(item.clone( channel='submnuteam', action='submnu_team', title = titulo, context=context_desarrollo, thumbnail=config.get_thumb('team'), fanart=fanart ))

    # =========================================================================
    # CABECERA Y TEXTOS INFORMATIVOS
    # =========================================================================

    # 1. TÍTULO PRINCIPAL
    itemlist.append(item.clone(
        action='', 
        title='[B][COLOR gold]★ BUTACAVIP ★[/COLOR][/B]', 
        thumbnail=os.path.join(config.get_runtime_path(), 'icon.png'), 
        plot='Bienvenido a tu centro multimedia personal', 
        folder=False,
        text_color='gold'
    ))

    # 2. SUBTÍTULO
    itemlist.append(item.clone(
        action='', 
        title='[COLOR lime]¿Eres nuevo?[/COLOR] Revisa la sección [B]Ayuda > ¿Cómo funciona?[/B]', 
        thumbnail=img_transparente,
        folder=False
    ))

    # 3. VERSIÓN
    itemlist.append(item.clone(
        action='', 
        title='Tu colección gratis de peliculas y series preferidas  [I][COLOR gray]v2.0 Edición Especial[/COLOR][/I]', 
        thumbnail=img_transparente,
        folder=False
    ))

    add_separator()
    
    # =========================================================================
    # BLOQUE 2: ZONA TMDB + ESTRENOS DINÁMICOS
    # =========================================================================
    
    icon_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'tmdb_icon.png')
    
    # Opción 1: Cartelera
    itemlist.append(item.clone(
        channel='tmdblists', action='listado', title='[B]Peliculas en TMDB[/B] (Ver todas)',
        extra='now_playing', search_type='movie',
        thumbnail=icon_tmdb, fanart=fanart,
        plot='Los últimos estrenos de cine actualizados desde The Movie Database'
    ))
    
    # Opción 2: Listas
    itemlist.append(item.clone( 
        channel='tmdblists', action='mainlist', title='[B]Listas TMDB[/B] (Populares, Valoradas...)', 
        plot='Explora listas populares, mejor valoradas, por recaudación, etc.',
        thumbnail=icon_tmdb, fanart=fanart
    ))
    
    # --- INICIO BLOQUE DINÁMICO (HTTPTOOLS) ---
    try:
        if 'get_cartelera_dinamica' in globals():
            estrenos_tmdb = get_cartelera_dinamica(item)
            if estrenos_tmdb:
                add_separator()
                itemlist.extend(estrenos_tmdb)
                add_separator()
    except:
        pass
    # --- FIN BLOQUE DINÁMICO ---


    # =========================================================================
    # BLOQUE 3: ZONA FILMAFFINITY
    # =========================================================================

    icon_fa = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'filmaffinity_icon.png')

    itemlist.append(item.clone(
        channel='filmaffinitylists', action='list_all', url='https://www.filmaffinity.com/es/cat_new_th_es.html',
        title='[B]Estrenos Filmaffinity[/B] (Ver todas)', search_type='movie',
        thumbnail=icon_fa, fanart=fanart,
        plot='La cartelera de cines España según Filmaffinity'
    ))
    
    add_separator()

    # =========================================================================
    # BLOQUE 4: HERRAMIENTAS Y NOVEDADES
    # =========================================================================

    itemlist.append(item.clone( 
        channel='submnuctext_custom', 
        action='submnu_news',
        title='[B]Tendencias & selección[/B]', 
        context=context_cfg_search, 
        extra='all',
        thumbnail=config.get_thumb('novedades'), 
        fanart=fanart, 
        mnupral='main',
        plot='Menú de tendencias & selección(Venta y Alquiler)'
    ))

    add_separator()

    itemlist.append(Item( channel='search', action='mainlist', title='[B]Buscar[/B]', context=context_buscar, thumbnail=config.get_thumb('search'), mnupral = 'main', fanart=fanart ))

    # --- NUEVO BOTÓN: REPRODUCTOR DIRECTO + LISTA GITHUB ---
    # Apuntamos a 'magnet_menu' para ver la lista y el buscador juntos
    itemlist.append(item.clone( 
        channel='mainmenu', 
        action='magnet_menu', 
        title='[B]Reproductor Directo[/B] (Pegar Magnet/Torrent)', 
        thumbnail=config.get_thumb('search'), 
        plot='Accede a enlaces directos y a la lista de novedades destacadas (GitHub/Gist).',
        folder=True 
    ))
    # ----------------------------------------

    if config.get_setting('sub_mnu_news', default=True):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades 2026[/B]', context=context_cfg_search, extra = 'all',thumbnail=config.get_thumb('novedades'), fanart=fanart, mnupral = 'main' ))

    if config.get_setting('sub_mnu_special', default=True):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Sagas[/B]', context=context_cfg_search, extra='all', thumbnail=config.get_thumb('heart'), fanart=fanart, mnupral = 'main' ))
    

    if config.get_setting('sub_mnu_favoritos', default=False):
        itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Mis Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart ))

    if not config.get_setting('mnu_simple', default=False):
        if config.get_setting('mnu_desargas', default=True) and config.get_setting('ord_descargas', default=False):
            itemlist.append(item.clone( channel='downloads', action='mainlist', title='[B]Descargas[/B]', context=context_descargas, thumbnail=config.get_thumb('downloads'), fanart=fanart ))

    add_separator()
    # =========================================================================
    # BLOQUE 5: CATEGORÍAS
    # =========================================================================

    itemlist.append(item.clone( 
        channel='generos',
        action='mainlist', 
        title='[B]Explorar por Categorías[/B]', 
        thumbnail=config.get_thumb('stack'), 
        fanart=fanart, 
        text_color='white' 
    ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='channels', extra='all', title='Canales', context=context_usual, detallar = True, thumbnail=config.get_thumb('stack'), fanart=fanart ))

    if config.get_setting('mnu_series', default=True):
        itemlist.append(item.clone( action='channels', extra='tvshows', title='Series', context=context_usual, thumbnail=config.get_thumb('tvshow'), fanart=fanart ))

    if config.get_setting('channels_link_pyse', default=False):
       itemlist.append(item.clone( action='channels', extra='mixed', title='Películas y Series', context=context_usual, no_docs = True, detallar = True, thumbnail=config.get_thumb('booklet'), fanart=fanart ))


    if config.get_setting('mnu_animes', default=True):
        itemlist.append(item.clone( action='channels', extra='anime', title='Animes', context=context_parental, thumbnail=config.get_thumb('anime'), fanart=fanart ))

    add_separator()

    # =========================================================================
    # BLOQUE 6: SISTEMA
    # =========================================================================

    itemlist.append(item.clone( 
        channel='mainmenu', 
        action='submnu_status', 
        title='[B][COLOR aqua]Estado del Sistema[/COLOR][/B]', 
        plot='Revisa si tus cuentas y motores están bien configurados para reproducir.',
        thumbnail=config.get_thumb('tools'), 
        fanart=fanart 
    ))

    try: last_ver = updater.check_addon_version()
    except: last_ver = None
    if last_ver is None: last_ver = ''
    elif not last_ver: last_ver = ' [COLOR violet](Update)[/COLOR]'
    else: last_ver = ''

    title = '[B]Ayuda y Configuración Avanzada[/B] %s' % last_ver
    itemlist.append(item.clone( action='ayuda', title=title, thumbnail=config.get_thumb('settings'), fanart=fanart ))

    return itemlist

def channels(item):
    logger.info()
    itemlist = []

    # -------------------------------------------------------------------------
    # BLOQUE PELÍCULAS
    # -------------------------------------------------------------------------
    if item.extra == 'movies':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), fanart=fanart, text_color='red' ))

        if config.get_setting('sub_mnu_favoritos', default=False):
            itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart, text_color='plum' ))

        item.category = 'Canales con Películas'
        itemlist.append(item.clone( action='', title='[B]- [I]Películas:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('movie'), fanart=fanart, text_color='deepskyblue' ))

        accion = 'mainlist_pelis'
        filtros = {'categories': 'movie'}

    # -------------------------------------------------------------------------
    # BLOQUE SERIES
    # -------------------------------------------------------------------------
    elif item.extra == 'tvshows':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), fanart=fanart, text_color='red' ))

        if config.get_setting('sub_mnu_favoritos', default=False):
            itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart, text_color='plum' ))

        item.category = 'Canales con Series'
        itemlist.append(item.clone( action='', title='[B]- [I]Series:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('tvshow'), fanart=fanart, text_color='hotpink' ))

        accion = 'mainlist_series'
        filtros = {'categories': 'tvshow'}

    # -------------------------------------------------------------------------
    # BLOQUE MIXTO (PELIS Y SERIES)
    # -------------------------------------------------------------------------
    elif item.extra == 'mixed':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), fanart=fanart, text_color='red' ))

        if config.get_setting('sub_mnu_favoritos', default=False):
            itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart, text_color='plum' ))

        item.category = 'Canales con Películas y Series (ambos contenidos)'
        itemlist.append(item.clone( action='', title='[B]- [I]Películas y Series:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('booklet'), fanart=fanart, text_color='teal' ))

        accion = 'mainlist'
        filtros = {}

    # -------------------------------------------------------------------------
    # BLOQUE GENERAL (TODOS LOS CANALES / ANIME / INFANTIL / ETC)
    # -------------------------------------------------------------------------
    else:
        # Lógica general (Excluidos Adultos y Novelas)
        if item.extra == 'anime': pass
        elif item.extra == 'infantil': pass
        elif not item.extra == 'groups':
            presentar = True

            if config.get_setting('mnu_proxies', default=False):
                if item.extra == 'proxies': presentar = False

            if config.get_setting('mnu_clones', default=False):
                if item.extra == 'clones': presentar = False

            if config.get_setting('mnu_problematicos', default=False):
                if item.extra == 'problematics': presentar = False

            if config.get_setting('mnu_desactivados', default=False):
                if item.extra == 'disableds': presentar = False

            if presentar:
               if config.get_setting('mnu_search_proxy_channels', default=False):
                   itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), fanart=fanart, text_color='red' ))

               if config.get_setting('sub_mnu_favoritos', default=False):
                   itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart, text_color='plum' ))
               
               # AQUI SE HAN ELIMINADO: NOVEDADES, ESPECIALES, BUSCAR, GRUPOS Y GÉNEROS

        # Configuración de categorías y títulos según el tipo
        if item.extra == 'anime': item.category = 'Solo los Canales exclusivos de Animes'
        elif item.extra == 'infantil': item.category = 'Solo los Canales exclusivos Infantiles'

        elif item.extra == 'suggested':
           item.category = 'Solo los Canales Sugeridos'
           itemlist.append(item.clone( action='', title='[B]- [I]Sugeridos:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('suggested'), fanart=fanart, text_color='aquamarine' ))

        elif item.extra == 'proxies': item.category = 'Solo los Canales con Proxies Memorizados'
        elif item.extra == 'clones': item.category = 'Solo los Canales que sean Clones'
        elif item.extra == 'disableds': item.category = 'Solo los Canales que estén Desactivados'
        elif item.extra == 'problematics': item.category = 'Solo los Canales que sean Problemáticos (Predominan Sin enlaces Disponibles/Válidos/Soportados)'

        elif not item.extra == 'groups':
           if item.extra == 'prefereds':
               item.category = 'Solo los Canales Preferidos'
               itemlist.append(item.clone( action='', title='[B]- [I]Canales Preferidos:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('stack'), fanart=fanart, text_color='coral' ))
           else:
               item.category = 'Todos los Canales'
               itemlist.append(item.clone( action='', title='[B]- [I]Canales:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('stack'), fanart=fanart, text_color='gold' ))

        else: item.category = 'Canales con Agrupaciones'

        # Submenús específicos de Infantil y Anime (Limpios de Buscar/Grupos)
        if item.extra == 'infantil':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), fanart=fanart, text_color='red' ))
            
            if config.get_setting('sub_mnu_favoritos', default=False):
                itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart, text_color='plum' ))
            
            itemlist.append(item.clone( channel='groups', action='ch_groups', title = '[COLOR tan][B]Todos[/B][/COLOR][B] los canales con contenido Infantil[/B]', group = 'kids', fanart=fanart ))
            itemlist.append(item.clone( action='', title='[B]- [I]Infantiles:[/I][/B]', context=context_usual, plot=item.category, thumbnail=config.get_thumb('booklet'), fanart=fanart, text_color='lightyellow' ))

        if item.extra == 'anime':
            if not config.get_setting('animes_password'):
                 itemlist.append(item.clone( channel='helper', action='show_help_adults', title='[COLOR green][B]Información [COLOR goldenrod]Parental[/B][/COLOR]', thumbnail=config.get_thumb('news'), fanart=fanart ))
                 itemlist.append(item.clone( channel='actions', action='adults_password', title= '[COLOR goldenrod][B]Establecer[/B][/COLOR] un PIN Parental', thumbnail=config.get_thumb('pencil'), fanart=fanart ))
            else:
                itemlist.append(item.clone( channel='helper', action='show_pin_parental', title= '[COLOR springgreen][B]Ver[/B][/COLOR] el PIN Parental', thumbnail=config.get_thumb('pencil'), fanart=fanart ))
                itemlist.append(item.clone( channel='actions', action='adults_password_del', title= '[COLOR red][B]Eliminar[/B][/COLOR] PIN parental', erase = True, folder=False, thumbnail=config.get_thumb('pencil'), fanart=fanart ))

            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), fanart=fanart, text_color='red' ))

            if config.get_setting('sub_mnu_favoritos', default=False):
                itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), fanart=fanart, text_color='plum' ))

            itemlist.append(item.clone( channel='groups', action='ch_groups', title = '[COLOR springgreen][B]Todos[/B][/COLOR] los canales con contenido Anime', group = 'anime', thumbnail=config.get_thumb('stack'), fanart=fanart  ))
            itemlist.append(item.clone( action='', title='[B]- [I]Animes:[/I][/B]', context=context_parental, plot=item.category, thumbnail=config.get_thumb('anime'), fanart=fanart, text_color='springgreen' ))

        if item.extra == 'proxies' or item.extra == 'clones' or item.extra == 'problematics' or item.extra == 'disableds':
            itemlist.append(item.clone( channel='actions', action='open_settings', title='[COLOR chocolate][B]Ajustes[/B][/COLOR] preferencias (categoría [COLOR tan][B]Menú)[/B][/COLOR]', context=context_config, folder=False, thumbnail=config.get_thumb('settings'), fanart=fanart ))

            if item.extra == 'proxies':
                itemlist.append(item.clone( action='', title='[B]- [I]Proxies:[/I][/B]', context=context_proxy_channels, plot=item.category, thumbnail=config.get_thumb('stack'), fanart=fanart, text_color='red' ))

            if item.extra == 'clones':
                itemlist.append(item.clone( action='', title='[B]- [I]Clones:[/I][/B]', context=context_proxy_channels, plot=item.category, thumbnail=config.get_thumb('stack'), fanart=fanart, text_color='turquoise' ))

            if item.extra == 'problematics':
                itemlist.append(item.clone( action='', title='[B]- [I]Problemáticos:[/I][/B]', context=context_desactivados, plot=item.category, thumbnail=config.get_thumb('stack'), fanart=fanart, text_color='darkgoldenrod' ))

            if item.extra == 'disableds':
                itemlist.append(item.clone( action='', title='[B]- [I]Desactivados:[/I][/B]', context=context_desactivados, plot=item.category, thumbnail=config.get_thumb('stack'), fanart=fanart, text_color='gray' ))

        accion = 'mainlist'
        filtros = {}

    # -------------------------------------------------------------------------
    # GENERACIÓN DEL LISTADO DE CANALES
    # -------------------------------------------------------------------------
    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        # ---------------------------------------------------------------------
        # FILTRO DE SEGURIDAD GLOBAL (ELIMINAR ADULTOS Y NOVELAS)
        # ---------------------------------------------------------------------
        if 'adults' in ch['clusters'] or '+18' in ch['notes']: continue
        if 'tales' in ch['clusters'] or 'exclusivamente en novelas' in ch['notes']: continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if not item.extra == 'all':
            if 'dedicada exclusivamente a los tráilers' in ch['notes']: continue

        if item.extra == 'prefereds':
            if not ch['status'] == 1: continue

        if item.extra == 'problematics':
            if not 'problematic' in ch['clusters']: continue
        else:
            if not item.extra == 'all':
                if config.get_setting('mnu_problematicos', default=False):
                    if 'problematic' in ch['clusters']: continue

        if item.extra == 'disableds':
            if not ch['status'] == -1: continue
        else:
            if not item.extra == 'all':
                if config.get_setting('mnu_desactivados', default=False):
                    if ch['status'] == -1: continue

        if item.extra == 'proxies':
            if not 'Puede requerir el uso de proxies' in ch['notes']: continue
            if not config.get_setting(cfg_proxies_channel, default=''): continue

        if item.extra == 'clones':
            if not 'clone' in ch['clusters']: continue

        else:
            if not item.extra == 'all':
                if item.extra == 'proxies': pass
                elif item.extra == 'clones': pass
                elif not item.extra == 'disableds':
                    if config.get_setting('mnu_proxies', default=False):
                        if 'Puede requerir el uso de proxies' in ch['notes']:
                            if config.get_setting(cfg_proxies_channel, default=''): continue

                    if config.get_setting('mnu_clones', default=False):
                        if 'clone' in ch['clusters']: continue

        if item.extra == 'movies':
            if ch['searchable'] == False:
                if 'anime' in ch['clusters']:
                   if config.get_setting('mnu_animes', default=True): continue
                elif 'infantil' in ch['clusters']:
                   if config.get_setting('mnu_infantiles', default=True): continue

        elif item.extra == 'tvshows':
            if ch['searchable'] == False:
                if 'mangas' in ch['notes'].lower(): continue
                elif 'anime' in ch['clusters']:
                   if config.get_setting('mnu_animes', default=True): continue
                elif 'infantil' in ch['clusters']:
                   if not ch['id'] == 'seodiv':
                       if config.get_setting('mnu_infantiles', default=True): continue

        elif item.extra == 'anime':
            if ch['searchable'] == True: continue
            if not 'anime' in ch['clusters']: continue

        elif item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue
            if not 'movie' in tipos: continue
            if not 'tvshow' in tipos: continue

        elif item.extra == 'torrents':
            if 'Streaming y Torrent' in ch['notes']: continue
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        elif item.extra == 'suggested':
            if not 'suggested' in ch['clusters']: continue
            if config.get_setting('mnu_simple', default=False):
                if str(ch['search_types']) == "['documentary']": continue
            if not config.get_setting('mnu_documentales', default=True):
                if str(ch['search_types']) == "['documentary']": continue

        elif item.extra == 'infantil':
            if not 'infantil' in ch['clusters']: continue

        else:
           # Lógica para "Todos los Canales" o genérica
           if config.get_setting('mnu_simple', default=False):
               if ch['searchable'] == False:
                   if 'anime' in ch['clusters']: continue
                   elif 'infantil' in ch['clusters']: continue
               else:
                   if str(ch['search_types']) == "['documentary']": continue
                   elif 'enlaces torrent exclusivamente' in ch['notes']: continue
                   elif not config.get_setting('mnu_documentales', default=True):
                       if str(ch['search_types']) == "['documentary']": continue
           else:
              if not config.get_setting('mnu_documentales', default=True):
                  if str(ch['search_types']) == "['documentary']": continue
              if not config.get_setting('mnu_infantiles', default=True):
                  if 'infantil' in ch['clusters']: continue
              if not config.get_setting('mnu_torrents', default=True):
                  if 'enlaces torrent exclusivamente' in ch['notes']: continue
              if not config.get_setting('mnu_animes', default=True):
                  if ch['searchable'] == False: continue
                  elif 'anime' in ch['clusters']: continue

        context = []

        if 'proxies' in ch['notes'].lower():
            if config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s]Quitar Proxies del Canal[/COLOR]' % color_list_proxies
                context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_proxies'})

        if ch['searchable']:
            if not ch['status'] == -1:
                cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

                if config.get_setting(cfg_searchable_channel, default=False):
                    tit = '[COLOR %s][B]Quitar Excluido Búsquedas[/B][/COLOR]' % color_adver
                    context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_no_searchables'})
                else:
                    if config.get_setting('search_included_all', default=''):
                        search_included_all = config.get_setting('search_included_all')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_included_all):
                            tit = '[COLOR indianred][B]Quitar Búsquedas Solo en[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included_del_one'})

                    if config.get_setting('search_excludes_all', default=''):
                        search_excludes_all = config.get_setting('search_excludes_all')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_all):
                            tit = '[COLOR indianred][B]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})
                    elif config.get_setting('search_excludes_movies', default=''):
                        search_excludes_movies = config.get_setting('search_excludes_movies')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_movies):
                            tit = '[B][COLOR deepskyblue]Películas [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})
                    elif config.get_setting('search_excludes_tvshows', default=''):
                        search_excludes_tvshows = config.get_setting('search_excludes_tvshows')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_tvshows):
                            tit = '[B][COLOR hotpink]Series [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})
                    elif config.get_setting('search_excludes_documentaries', default=''):
                        search_excludes_documentaries = config.get_setting('search_excludes_documentaries')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_documentaries):
                            tit = '[B][COLOR cyan]Documentales [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})
                    elif config.get_setting('search_excludes_torrents', default=''):
                        search_excludes_torrents = config.get_setting('search_excludes_torrents')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_torrents):
                            tit = '[B][COLOR blue]Torrents [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})
                    elif config.get_setting('search_excludes_mixed', default=''):
                        search_excludes_mixed = config.get_setting('search_excludes_mixed')
                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_mixed):
                            tit = '[B][COLOR teal]Películas y/ó Series [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})
                    else:
                        tit = '[COLOR %s][B]Excluir en Búsquedas[/B][/COLOR]' % color_adver
                        context.append({'title': tit, 'channel': item.channel, 'action': '_poner_no_searchables'})

        if ch['status'] != 1:
            tit = '[COLOR %s][B]Marcar Canal como Preferido[/B][/COLOR]' % color_list_prefe
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 1})

        if ch['status'] != 0:
            if ch['status'] == 1:
                tit = '[COLOR %s][B]Des-Marcar Canal Preferido[/B][/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            elif ch['status'] == -1:
                tit = '[COLOR %s][B]Re-Activar Canal Desactivado[/B][/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            else:
                tit = '[COLOR white][B]Marcar Canal como Activo[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})

        if ch['status'] != -1:
            tit = '[COLOR %s][B]Marcar Canal como Desactivado[/B][/COLOR]' % color_list_inactive
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

        cfg_domains = False

        if 'current' in ch['clusters']:
            cfg_domains = True
            tit = '[COLOR bisque]Gestión Dominios[/COLOR]'
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

        tit = '[COLOR %s][B]Últimos Cambios Dominios[/B][/COLOR]' % color_exec
        context.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

        if cfg_domains:
            tit = '[COLOR yellowgreen][B]Dominio Vigente[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_vigente'})

            if 'Dispone de varios posibles dominios' in ch['notes']:
                tit = '[COLOR powderblue][B]Configurar Dominio a usar[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_dominios'})

            tit = '[COLOR orange][B]Modificar Dominio Memorizado[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_memorizado'})

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'

            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
                tit = '[COLOR green][B]Información Registrarse[/B][/COLOR]'
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_register'})
                tit = '[COLOR teal][B]Credenciales Cuenta[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})
            else:
                cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_login'
                presentar = True
                if 'dominios' in ch['notes'].lower():
                    cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                    if not config.get_setting(cfg_dominio_channel, default=''): presentar = False
                if presentar:
                    if config.get_setting(cfg_login_channel, default=False):
                        tit = '[COLOR teal][B]Cerrar Sesión[/B][/COLOR]'
                        context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})

        if 'proxies' in ch['notes'].lower():
            if not config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s][B]Información Proxies[/B][/COLOR]' % color_infor
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})
            tit = '[COLOR %s][B]Configurar Proxies a usar[/B][/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

        if 'notice' in ch['clusters']:
            tit = '[COLOR tan][B]Aviso Canal[/B][/COLOR]'
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_' + ch['id']})

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'
            if config.get_setting(cfg_user_channel, default='') and config.get_setting(cfg_pass_channel, default=''):
               cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_login'
               if config.get_setting(cfg_login_channel, default=False):
                   tit = '[COLOR springgreen][B]Test Login Cuenta[/B][/COLOR]'
                   context.append({'title': tit, 'channel': 'submnuctext', 'action': '_credenciales_' + ch['id']})

        tit = '[COLOR darkorange][B]Test Web Canal[/B][/COLOR]'
        context.append({'title': tit, 'channel': item.channel, 'action': '_tests'})

        if cfg_domains:
            tit = '[COLOR %s]Ajustes categoría Dominios[/COLOR]' % color_exec
            context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

        color = color_list_prefe if ch['status'] == 1 else 'white' if ch['status'] == 0 else color_list_inactive
        
        # Plot description
        plot = ''
        if item.extra == 'all': plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']

        if ch['status'] == -1:
            if not item.extra == 'disableds': titulo += '[I][B][COLOR %s] (desactivado)[/COLOR][/I][/B]' % color_list_inactive
            if config.get_setting(cfg_proxies_channel, default=''): titulo += '[I][B][COLOR %s] (proxies)[/COLOR][/I][/B]' % color_list_proxies
        else:
            if ch['status'] == 1:
               if not item.extra == 'prefereds': titulo += '[I][B][COLOR wheat] (preferido)[/COLOR][/I][/B]'
            else:
                if not item.extra == 'suggested':
                    if 'suggested' in ch['clusters']: titulo += '[I][B][COLOR olivedrab] (sugerido)[/COLOR][/I][/B]'

            if config.get_setting(cfg_proxies_channel, default=''):
                if ch['status'] == 1: titulo += '[I][B][COLOR %s] (proxies)[/COLOR][/I][/B]' % color_list_proxies
                else: color = color_list_proxies

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'
            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
               titulo += '[I][B][COLOR teal] (cuenta)[/COLOR][/I][/B]'
            else:
               cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_login'
               if config.get_setting(cfg_login_channel, default=False):
                   presentar = True
                   if 'dominios' in ch['notes'].lower():
                       cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                   if presentar: titulo += '[I][B][COLOR teal] (sesión)[/COLOR][/I][/B]'
               else: titulo += '[I][COLOR teal] (login)[/COLOR][/I]'

        if 'current' in ch['clusters']:
            cfg_current_channel = 'channel_' + ch['id'] + '_dominio'
            if config.get_setting(cfg_current_channel, default=False): titulo += '[I][B][COLOR green] (dominio)[/COLOR][/I][/B]'

        if 'inestable' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            elif config.get_setting('channels_list_no_inestables', default=False): continue
            titulo += '[I][B][COLOR plum] (inestable)[/COLOR][/I][/B]'

        elif 'problematic' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            if not item.extra == 'all':
                if not item.extra == 'problematics': 
                    if config.get_setting('mnu_problematicos', default=False): continue
                    elif config.get_setting('channels_list_no_problematicos', default=False): continue
            if not item.extra == 'problematics': titulo += '[I][B][COLOR darkgoldenrod] (problemático)[/COLOR][/I][/B]'

        elif 'clone' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            if not item.extra == 'all':
                if not item.extra == 'clones': 
                    if config.get_setting('mnu_clones', default=False): continue
                    elif config.get_setting('channels_list_no_clones', default=False): continue
            if not item.extra == 'clones': titulo += '[I][B][COLOR turquoise] (clon)[/COLOR][/I][/B]'

        if con_incidencias:
           if ch['name'] in str(con_incidencias): titulo += '[I][B][COLOR tan] (incidencia)[/COLOR][/I][/B]'
        if no_accesibles:
           if ch['name'] in str(no_accesibles): titulo += '[I][B][COLOR indianred] (no accesible)[/COLOR][/I][/B]'
        if con_problemas:
           if ch['name'] in str(con_problemas):
               hay_problemas = str(con_problemas).replace('[B][COLOR moccasin]', 'CHANNEL').replace('[COLOR lime]', '/CHANNEL')
               channels_con_problemas = scrapertools.find_multiple_matches(hay_problemas, "CHANNEL(.*?)/CHANNEL")
               for channel_con_problema in channels_con_problemas:
                    channel_con_problema = channel_con_problema.strip()
                    if not channel_con_problema == ch['name']: continue
                    titulo += '[I][B][COLOR tomato] (con problema)[/COLOR][/I][/B]'
                    break

        if ch['searchable']:
            if not ch['status'] == -1:
                cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'
                if config.get_setting(cfg_searchable_channel, default=False): titulo += '[I][B][COLOR yellowgreen] (no búsquedas)[/COLOR][/I][/B]'
                if config.get_setting('search_included_all', default=''):
                   if ch['id'] in str(config.get_setting('search_included_all')): titulo += '[I][B][COLOR yellowgreen] (solo buscar)[/COLOR][/I][/B]'

        presentar = False
        if config.get_setting('mnu_simple', default=False): presentar = True
        elif config.get_setting('channels_link_main', default=True): presentar = True
        if not item.detallar: presentar = False

        if presentar:
            if 'movie' in ch['categories']:
                if 'tvshow' in ch['categories']: titulo += '[B][I][COLOR deepskyblue] películas[/COLOR] [COLOR hotpink]series[/COLOR][/I][/B]'
                else: titulo += '[B][I][COLOR deepskyblue] películas[/COLOR][/I][/B]'
            else:
                if 'tvshow' in ch['categories']: titulo += '[B][I][COLOR hotpink] series[/COLOR][/I][/B]'
                elif "documentary" in ch['categories']: titulo += '[B][I][COLOR cyan] documentales[/COLOR][/I][/B]'

        i += 1 

        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot=plot, extra=item.extra, thumbnail=ch['thumbnail'], fanart=fanart, category=ch['name'] ))

    if len(ch_list) == 0 or i == 0:
        if item.extra == 'Proxies' or item.extra == 'disableds':
            itemlist.append(item.clone( channel='actions', action='open_settings', title='[COLOR chocolate][B]Ajustes[/B][/COLOR] preferencias (categoría [COLOR tan][B]Menú)[/B][/COLOR]', context=context_config, folder=False, thumbnail=config.get_thumb('settings'), fanart=fanart ))

        if item.extra == 'proxies':
            itemlist.append(item.clone( channel='filters', action='with_proxies', title='[B]Sin canales con Proxies Memorizados[/B]', text_color=color_list_proxies, thumbnail=config.get_thumb('stack'), fanart=fanart, folder=False ))
        elif item.extra == 'clones':
            itemlist.append(item.clone( channel='filters', action='show_channels_list', title='[B]Sin canales Problemáticos[/B]', text_color='darkgoldenrod', problematics=True, thumbnail=config.get_thumb('stack'), fanart=fanart, folder=False ))
        elif item.extra == 'problematics':
            itemlist.append(item.clone( channel='filters', action='show_channels_list', title='[B]Sin canales Problemáticos[/B]', text_color='darkgoldenrod', clones=True, thumbnail=config.get_thumb('stack'), fanart=fanart, folder=False ))
        elif item.extra == 'disableds':
            itemlist.append(item.clone( channel='filters', action='channels_status', title='[B]Sin canales Desactivados[/B]', text_color=color_list_inactive, des_rea=True, thumbnail=config.get_thumb('stack'), fanart=fanart, folder=False ))
        else:
            itemlist.append(item.clone( channel='filters', action='channels_status', title='[B]Opción Sin canales[/B]', text_color=color_list_prefe, des_rea=False, thumbnail=config.get_thumb('stack'), fanart=fanart, folder=False ))

    return itemlist


def ver_saga_nativa(item):
    logger.info("Cargando saga: " + item.title)
    itemlist = []
    
    # 1. Usamos la API de TMDB directamente para sacar las pelis
    # Esto evita depender de canales externos
    import json
    from core import httptools
    
    # API Key pública de respaldo (si el usuario no tiene la suya configurada)
    api_key = config.get_setting('tmdb_api')
    if not api_key: api_key = '5c88939574e202d8432edcb638e08e10'
    
    url = 'https://api.themoviedb.org/3/collection/%s?api_key=%s&language=es-ES' % (item.url, api_key)
    
    try:
        data = httptools.downloadpage(url).data
        if data:
            data = json.loads(data)
            parts = data.get('parts', [])
            
            # Ordenamos por fecha de estreno
            parts.sort(key=lambda x: x.get('release_date', '9999'))
            
            fanart_saga = "https://image.tmdb.org/t/p/original" + data.get('backdrop_path', '')
            
            for peli in parts:
                if not peli.get('poster_path'): continue
                
                titulo = peli.get('title')
                thumb = "https://image.tmdb.org/t/p/w500" + peli.get('poster_path')
                year = peli.get('release_date', '')[:4]
                
                # Al pulsar la película, BUSCAMOS en todos los canales (search)
                itemlist.append(Item(
                    channel='search',
                    action='search',
                    title=titulo + " [COLOR yellow](" + year + ")[/COLOR]",
                    buscando=titulo,
                    thumbnail=thumb,
                    fanart=fanart_saga,
                    search_type='movie',
                    contentTitle=titulo,
                    contentType='movie'
                ))
    except:
        pass
        
    return itemlist

def idioma_canal(lang):
    idiomas = { 'cast': 'Castellano', 'lat': 'Latino', 'eng': 'Inglés', 'pt': 'Portugués', 'vo': 'VO', 'vose': 'Vose', 'vos': 'Vos', 'cat': 'Català' }
    return idiomas[lang] if lang in idiomas else lang


def _marcar_canal(item):
    from modules import submnuctext
    submnuctext._marcar_canal(item)


def _poner_no_searchables(item):
    from modules import submnuctext
    submnuctext._poner_no_searchable(item)

def _quitar_no_searchables(item):
    from modules import submnuctext
    submnuctext._quitar_no_searchable(item)


def _quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)


def _dominio_vigente(item):
    from modules import submnuctext
    submnuctext._dominio_vigente(item)


def _dominio_memorizado(item):
    from modules import submnuctext
    submnuctext._dominio_memorizado(item)


def _dominios(item):
    from modules import submnuctext
    submnuctext._dominios(item)


def _credenciales(item):
    from modules import submnuctext
    submnuctext._credenciales(item)


def _proxies(item):
    from modules import submnuctext
    submnuctext._proxies(item)


def _tests(item):
    from modules import submnuctext
    submnuctext._test_webs(item)

# =========================================================================
# FUNCIONES AUXILIARES MENÚ AYUDA
# =========================================================================

def ayuda(item):
    logger.info()
    itemlist = []

    # Definimos el icono unificado (el de Ajustes) para todo el menú
    icon_settings = config.get_thumb('settings')

    # 1. Tutorial de Uso
    itemlist.append(item.clone( 
        action='tutorial_uso', 
        title='[B]¿Cómo funciona?[/B] (Tutorial Rápido)', 
        thumbnail=icon_settings, 
        plot='Aprende los pasos básicos: Canal > Película > Servidor.'
    ))

    # 2. Mantenimiento y Limpieza
    itemlist.append(item.clone( 
        channel='actions', 
        action='manto_limpiezas', 
        title='[B]Limpieza y Optimización[/B]', 
        thumbnail=icon_settings, 
        plot='[COLOR orange]Recomendado:[/COLOR] Borra caché, elimina archivos temporales y optimiza el rendimiento del addon.'
    ))
    
    # 3. Legalidad
    itemlist.append(item.clone( 
        action='show_legal', 
        title='[B]Legalidad[/B]', 
        thumbnail=icon_settings, 
        plot='Información legal, exención de responsabilidad y términos de uso.'
    ))

    # 4. Ajustes
    itemlist.append(item.clone( 
        channel='actions', 
        action='open_settings', 
        title='[B]Ajustes[/B]', 
        thumbnail=icon_settings, 
        plot='Configuración general del addon.'
    ))

    # 5. Contacto con el Desarrollador 
    itemlist.append(item.clone( 
        action='show_contact', 
        title='[B]Contacto con el Desarrollador[/B]', 
        thumbnail=icon_settings, 
        plot='Información de contacto para sugerencias o reportes.'
    ))

    return itemlist


def show_contact(item):
    import xbmcgui
    
    # Mensaje de contacto
    txt = "[B][COLOR yellow]CONTACTO CON EL DESARROLLADOR[/COLOR][/B]\n\n"
    txt += "Hola, gracias por usar ButacaVip.\n\n"
    txt += "Si tienes sugerencias, agradecimientos o quieres comentar algo sobre el funcionamiento, puedes encontrarnos en:\n\n"
    txt += "[B][COLOR deepskyblue]Telegram:[/COLOR][/B] t.me/ButacaVip\n\n" 
    txt += "Estaremos encantados de leerte."

    # Usamos textviewer para que se lea bien
    xbmcgui.Dialog().textviewer("Contacto", txt)
    return True

def tutorial_uso(item):
    import xbmcgui
    
    txt = "[B][COLOR yellow]¿CÓMO VER UNA PELÍCULA O SERIE?[/COLOR][/B]\n\n"
    txt += "[B]1. ELIGE UN CANAL o UNA OPCIÓN DEL MENU PARA VER ESTRENOS O NOVEDADES:[/B]\n"
    txt += "[B]Te recomendamos que elijas opciones del menú como[COLOR blue] ESTRENOS BUTACAVIP, PELICULAS EN TMDB y ESTRENOS FILMAFFINITY[/COLOR][/B]\n"
    txt += "Los canales (ej. Filmaffinity, Cinecalidad...) son como 'páginas web'. Entra en el que más te guste.\n\n"
    txt += "[B]2. BUSCA EL CONTENIDO:[/B]\n"
    txt += "Navega por las listas o usa el Buscador hasta encontrar título de la pelicula o estreno que quieres ver.\n\n"
    txt += "[B]3. ELIGE EL SERVIDOR (El paso importante):[/B]\n"
    txt += "Al pinchar en la peli, verás una lista de 'enlaces' (ej: Gamovideo, Streamtape...).\n"
    txt += "- Pincha en uno.\n"
    txt += "- Si no carga, [B]prueba con el siguiente[/B].\n"
    txt += "- Los enlaces dependen de las webs externas. ¡Paciencia!\n\n"
    txt += "[B]CONSEJO:[/B] Los enlaces '1080p' se ven mejor pero requieren buena conexión."

    xbmcgui.Dialog().textviewer("Guía Rápida - ButacaVip", txt)
    return True

def upload_log(item):
    import xbmc, xbmcgui, os, socket
    
    # Lógica simplificada
    log_path = os.path.join(xbmc.translatePath('special://logpath'), 'kodi.log')

    if not os.path.exists(log_path):
        platformtools.dialog_notification("Error", "No hay log disponible")
        return

    if not xbmcgui.Dialog().yesno("Reportar Error", "Se subirá el log a internet para revisión.\n¿Deseas continuar?"): return

    try:
        platformtools.dialog_notification("Subiendo...", "Espere un momento")
        with open(log_path, 'rb') as f: content = f.read()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(('termbin.com', 9999))
        s.sendall(content)
        s.shutdown(socket.SHUT_WR)
        url = s.recv(1024).decode('utf-8').strip()
        s.close()
        
        from urllib.parse import quote
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" + quote(url)
        xbmcgui.Dialog().ok("Log Subido", f"Pásame este enlace:\n[COLOR yellow]{url}[/COLOR]")
    except:
        xbmcgui.Dialog().ok("Error", "Fallo al subir el log.")

def show_legal(item):
    import xbmcgui
    
    # Cabecera
    txt = "[B][COLOR red]TÉRMINOS DE USO, AVISO LEGAL Y EXENCIÓN DE RESPONSABILIDAD[/COLOR][/B]\n\n"
    
    # 1. FINALIDAD DEL PROYECTO
    txt += "[B][COLOR deepskyblue]1. NATURALEZA DEL PROYECTO[/COLOR][/B]\n"
    txt += "ButacaVip es un proyecto estrictamente [B]EDUCATIVO[/B], experimental y sin ánimo de lucro. "
    txt += "No existe ningún tipo de comercialización, publicidad, suscripción ni monetización asociada a esta herramienta. "
    txt += "Su único fin es didáctico, orientado a la investigación del desarrollo de software, el aprendizaje del lenguaje Python y la automatización de procesos de navegación web.\n\n"

    # 2. ASPECTOS TÉCNICOS
    txt += "[B][COLOR deepskyblue]2. FUNCIONAMIENTO TÉCNICO[/COLOR][/B]\n"
    txt += "Esta herramienta es un script de código abierto (Open Source) desarrollado en [B]Python 3[/B]. "
    txt += "Técnicamente, funciona como un navegador web automatizado que utiliza librerías estándar de procesamiento de datos (como [I]requests, json, regex[/I]) para interpretar la estructura de sitios web públicos. "
    txt += "El addon no 'emite' contenido, simplemente organiza información que ya es pública en internet.\n\n"
    
    # 3. NO ALOJAMIENTO (SAFE HARBOR)
    txt += "[B][COLOR deepskyblue]3. NO ALOJAMIENTO DE CONTENIDOS[/COLOR][/B]\n"
    txt += "Desde ButacaVip [B]NO se compila, almacena, distribuye ni gestiona[/B] archivos de vídeo, audio o datos personales. "
    txt += "El proyecto actúa exclusivamente como un [B]motor de búsqueda e indexación[/B] de enlaces (URLs).\n"
    txt += "• Todo el contenido visualizado reside en servidores de terceros (como Uptobox, Streamtape, Fembed, etc.) ajenos totalmente a este proyecto.\n"
    txt += "• ButacaVip no tiene control, relación contractual ni capacidad de administración sobre dichos servidores externos.\n\n"

    # 4. PRIVACIDAD DE DATOS
    txt += "[B][COLOR deepskyblue]4. POLÍTICA DE PRIVACIDAD[/COLOR][/B]\n"
    txt += "Este software no requiere registro. No recopilamos, almacenamos ni transmitimos datos personales, direcciones IP ni historiales de navegación de los usuarios. "
    txt += "El uso es completamente anónimo desde el punto de vista del desarrollador.\n\n"

    # 5. RESPONSABILIDAD DEL USUARIO
    txt += "[B][COLOR deepskyblue]5. RESPONSABILIDAD DE USO[/COLOR][/B]\n"
    txt += "El desarrollador declina toda responsabilidad sobre el uso indebido que se haga de esta herramienta. "
    txt += "Es responsabilidad exclusiva del usuario final:\n"
    txt += "• Hacer un uso estrictamente privado del contenido.\n"
    txt += "• Asegurarse de cumplir con las leyes de propiedad intelectual y normativas vigentes en su país de residencia antes de acceder a los enlaces.\n\n"

    # 6. AUSENCIA DE GARANTÍA (AS-IS)
    txt += "[B][COLOR deepskyblue]6. AUSENCIA DE GARANTÍA[/COLOR][/B]\n"
    txt += "Este software se proporciona 'tal cual' (as-is), sin garantías de funcionamiento continuo. Al ser un proyecto de investigación dependiente de webs de terceros, la disponibilidad del contenido puede variar sin previo aviso."

    xbmcgui.Dialog().textviewer("Aviso Legal - ButacaVip", txt)
    return True

def submnu_status(item):
    itemlist = []
    import xbmc
    
    # --- RUTAS DE IMÁGENES ---
    icon_status = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'bolt.png')
    img_trans   = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'transparent.png')

    # 1. TEXTO INFORMATIVO
    itemlist.append(item.clone( 
        title="[B][COLOR lime]HERRAMIENTAS DEL SISTEMA[/COLOR][/B]", 
        action="", 
        thumbnail=img_trans, 
        folder=False
    ))
    
    itemlist.append(item.clone( 
        title="[COLOR white]Estos complementos son muy recomendables para evitar potenciales errores[/COLOR]", 
        action="", 
        thumbnail=img_trans, 
        folder=False
    ))
    
    itemlist.append(item.clone( 
        title="[COLOR white]y mejorar la visualización del contenido.[/COLOR]", 
        action="", 
        thumbnail=img_trans, 
        folder=False
    ))
    
    # Separador
    itemlist.append(item.clone( title='[COLOR dimgray]──────────────────────────────────────────[/COLOR]', action='', thumbnail=img_trans, folder=False ))

    # 2. REAL-DEBRID (BOTÓN CONFIGURABLE)
    rd_active = config.get_setting('rd_enabled', default=False)
    rd_token = config.get_setting('rd_token', default='')
    
    if rd_active and rd_token:
        status_rd = "[COLOR green]ACTIVO Y VINCULADO[/COLOR]"
        plot_rd = "Tu cuenta está correctamente configurada."
    elif rd_active and not rd_token:
        status_rd = "[COLOR yellow]FALTA TOKEN (Clic para configurar)[/COLOR]"
        plot_rd = "Falta el API Token. Pulsa para abrir Ajustes."
    else:
        status_rd = "[COLOR red]DESACTIVADO (Clic para activar)[/COLOR]"
        plot_rd = "Pulsa para abrir Ajustes y activar Real-Debrid."
    
    # Al hacer click, llama a la función 'open_settings'
    itemlist.append(item.clone( 
        title="Real-Debrid: %s" % status_rd, 
        action="open_settings", 
        thumbnail=icon_status, 
        folder=False,
        plot=plot_rd
    ))

    # 3. ELEMENTUM
    if xbmc.getCondVisibility('System.HasAddon(plugin.video.elementum)'):
        status_ele = "[COLOR green]INSTALADO[/COLOR]"
    else:
        status_ele = "[COLOR red]NO DETECTADO[/COLOR]"
    
    itemlist.append(item.clone( title="Motor Elementum: %s" % status_ele, action="", thumbnail=icon_status, folder=False ))

    # 4. TORRSERVER
    if xbmc.getCondVisibility('System.HasAddon(script.module.torrserver)'):
        status_torr = "[COLOR green]INSTALADO[/COLOR]"
    else:
        status_torr = "[COLOR red]NO DETECTADO[/COLOR]"
        
    itemlist.append(item.clone( title="Motor TorrServer: %s" % status_torr, action="", thumbnail=icon_status, folder=False ))

    # 5. RESOLVEURL (NUEVO)
    if xbmc.getCondVisibility('System.HasAddon(script.module.resolveurl)'):
        status_res = "[COLOR green]INSTALADO[/COLOR]"
    else:
        status_res = "[COLOR red]NO DETECTADO[/COLOR]"
        
    itemlist.append(item.clone( title="ResolveURL: %s" % status_res, action="", thumbnail=icon_status, folder=False ))

    return itemlist


# =========================================================================
# FUNCIÓN: TEST DE CONEXIÓN REAL-DEBRID (CON LOGS DE DEPURACIÓN)
# =========================================================================
def test_rd_connection(item):
    from core import httptools
    from platformcode import config, platformtools, logger # Importamos logger
    import json
    
    logger.info("[ButacaVip] --- INICIANDO TEST REAL-DEBRID ---")
    
    # 1. Obtener el Token
    token = config.get_setting('rd_token')
    
    if not token:
        logger.info("[ButacaVip] Error: No hay token guardado.")
        platformtools.dialog_notification("ButacaVip", "Falta el API Token", time=3000)
        return

    # Log de seguridad (solo muestra los primeros 4 caracteres)
    token_parcial = token[:4] + "****"
    logger.info("[ButacaVip] Token encontrado: " + token_parcial)

    # 2. Conectar
    headers = {"Authorization": "Bearer " + token}
    url = "https://api.real-debrid.com/rest/1.0/user"
    
    platformtools.dialog_notification("ButacaVip", "Conectando...", time=2000)
    logger.info("[ButacaVip] Enviando petición a: " + url)
    
    try:
        resp = httptools.downloadpage(url, headers=headers)
        
        # LOG IMPORTANTE: Ver qué responde el servidor
        logger.info("[ButacaVip] Código de respuesta: " + str(resp.code))
        logger.info("[ButacaVip] Datos recibidos: " + str(resp.data))
        
        if resp.code == 200:
            if not resp.data:
                logger.error("[ButacaVip] Error: Respuesta vacía (200 OK pero sin datos)")
                platformtools.dialog_ok("Error", "Real-Debrid respondió OK pero sin datos.")
                return

            data = json.loads(resp.data)
            usuario = data.get('username', 'Desconocido')
            tipo = data.get('type', 'free') 
            caducidad = data.get('expiration', 'Nunca')
            
            mensaje = "[B]CONEXIÓN EXITOSA[/B]\n\n"
            mensaje += "Usuario: [COLOR gold]" + usuario + "[/COLOR]\n"
            mensaje += "Estado: [COLOR green]" + tipo.upper() + "[/COLOR]\n"
            mensaje += "Caduca: " + caducidad
            
            logger.info("[ButacaVip] Test Exitoso. Usuario: " + usuario)
            platformtools.dialog_ok("Real-Debrid", mensaje)
            
        elif resp.code == 401:
            logger.info("[ButacaVip] Error 401: Token inválido.")
            platformtools.dialog_ok("Error", "El Token introducido es [COLOR red]INVÁLIDO[/COLOR].\nRevísalo y vuelve a intentar.")
            
        elif resp.code == 403:
            logger.info("[ButacaVip] Error 403: Acceso prohibido (Token caducado o IP baneada).")
            platformtools.dialog_ok("Error", "Acceso Prohibido (403).\nTu token puede haber caducado.")
            
        else:
            logger.error("[ButacaVip] Error desconocido. Code: " + str(resp.code))
            platformtools.dialog_ok("Error", "Respuesta del servidor: " + str(resp.code))
            
    except Exception as e:
        import traceback
        logger.error("[ButacaVip] EXCEPCIÓN CRÍTICA: " + str(e))
        logger.error(traceback.format_exc()) # Esto nos dirá la línea exacta del error
        platformtools.dialog_ok("Error Interno", "Fallo al conectar: " + str(e))
        
# =========================================================================
# FUNCIÓN: REPRODUCIR DESDE MAGNET/URL (INTELIGENTE)
# =========================================================================
def play_from_magnet(item):
    import xbmc
    import xbmcgui
    import urllib.parse
    from platformcode import platformtools

    # 1. Abrir teclado
    keyboard = xbmc.Keyboard("", "Pega tu enlace (Magnet, Torrent o HTTP)")
    keyboard.doModal()

    if keyboard.isConfirmed():
        url = keyboard.getText()

        if url:
            url = url.strip()
            
            # =========================================================
            # CASO A: Es un Torrent o Magnet (Para Elementum)
            # =========================================================
            if url.lower().startswith('magnet:') or url.lower().endswith('.torrent'):
                platformtools.dialog_notification("ButacaVip", "Enviando a Elementum...", time=2000)
                try:
                    # Codificamos la URL para evitar errores con caracteres especiales
                    url_encoded = urllib.parse.quote_plus(url)
                    media_url = "plugin://plugin.video.elementum/play?uri=" + url_encoded
                    
                    # Usamos un ListItem y PlayMedia para asegurar la ejecución
                    xbmc.executebuiltin('PlayMedia(' + media_url + ')')
                except:
                    platformtools.dialog_notification("Error", "Fallo al enviar a Elementum")

            # =========================================================
            # CASO B: Es un enlace HTTP (Real-Debrid, Uptobox, Directo...)
            # =========================================================
            elif url.lower().startswith('http') or url.lower().startswith('https'):
                platformtools.dialog_notification("ButacaVip", "Procesando enlace...", time=1000)
                
                stream_url = url 
                es_resuelto = False
                nombre_video = "Reproducción Directa"

                # 1. Intentamos RESOLVER con ResolveURL (Para enlaces premium/hosters)
                # Esto es lo que faltaba: convertir la web de descarga en un archivo de vídeo real
                try:
                    import resolveurl
                    # Intentamos resolver directamente
                    msg = resolveurl.resolve(url)
                    if msg:
                        stream_url = msg
                        es_resuelto = True
                        nombre_video = "Enlace Resuelto (Premium)"
                        platformtools.dialog_notification("ButacaVip", "¡Enlace Resuelto!", time=2000)
                except Exception as e:
                    # Si falla resolveurl o no es un hoster soportado, seguimos con la URL original
                    pass

                # 2. Si NO se resolvió (es un enlace directo propio), añadimos User-Agent
                # Esto engaña al servidor para que crea que somos un navegador y no nos bloquee (Error 403)
                if not es_resuelto and "|" not in stream_url:
                    stream_url += "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

                # 3. Reproducir
                li = xbmcgui.ListItem(path=stream_url)
                li.setInfo('video', {'title': nombre_video})
                # Marcamos que es reproducible
                li.setProperty('IsPlayable', 'true')
                
                xbmc.Player().play(stream_url, li)

            else:
                platformtools.dialog_notification("Error", "Formato no reconocido", time=3000)
                
# =========================================================================
# NUEVAS FUNCIONES PARA TU MENÚ DE NOVEDADES + ELEMENTUM
# =========================================================================

def get_gist_list():
    """Descarga tu lista de GitHub"""
    from core import httptools
    import json
    
    # Tu URL exacta corregida para que se actualice siempre
    URL_MAESTRA = "https://gist.githubusercontent.com/Eduard289/99519b8cdba169c3bde095db129bdc2f/raw/gistfile1.txt"
    
    items_gist = []
    try:
        # Descargamos sin usar caché para ver cambios al instante
        resp = httptools.downloadpage(URL_MAESTRA, use_cache=False)
        if resp.data:
            data_json = resp.data.strip()
            lista = json.loads(data_json)
            
            for entrada in lista:
                titulo = entrada.get('title', 'Sin título')
                magnet = entrada.get('magnet', '')
                
                # Creamos el botón para cada película de la lista
                item = Item(
                    channel = "mainmenu",
                    action = "play_magnet_elementum", # Al pulsar, reproduce
                    title = "[COLOR gold]★ " + titulo + "[/COLOR]",
                    url = magnet,
                    thumbnail = "", 
                    plot = "Enlace destacado del desarrollador.",
                    folder = False
                )
                items_gist.append(item)
    except:
        pass
    return items_gist

def magnet_menu(item):
    """Este es el MENÚ que muestra: 1. Pegar manual, 2. Tu lista"""
    import os
    itemlist = []
    
    # OPCIÓN 1: El botón de siempre para pegar texto
    itemlist.append(item.clone(
        action='play_magnet_elementum', 
        url='manual_input',
        title='[B][COLOR lime]➤ Escribir o Pegar enlace Magnet/Hash...[/COLOR][/B]', 
        thumbnail=item.thumbnail, 
        plot='Pulsar para sacar el teclado y pegar un enlace manualmente.',
        folder=False 
    ))
    
    # SEPARADOR
    img_transparente = os.path.join(config.get_runtime_path(), 'resources', 'media', 'themes', 'default', 'transparent.png')
    itemlist.append(item.clone(action='', title='[COLOR cyan]--- TUS NOVEDADES Y SELECCIÓN ---[/COLOR]', thumbnail=img_transparente, folder=False))
    
    # OPCIÓN 2: Tu lista de GitHub
    tus_enlaces = get_gist_list()
    itemlist.extend(tus_enlaces)
    
    return itemlist

def play_magnet_elementum(item):
    """La lógica que reproduce el enlace en Elementum"""
    import xbmc
    import xbmcgui
    import urllib.parse
    from platformcode import platformtools

    url = item.url

    # Si pulsó "Escribir o Pegar", abrimos el teclado
    if not url or url == "manual_input":
        keyboard = xbmc.Keyboard("", "Pega tu enlace Magnet")
        keyboard.doModal()
        if keyboard.isConfirmed():
            url = keyboard.getText()
    
    if url:
        url = url.strip()
        
        # Corrección si pegan solo el hash
        if len(url) == 40 and not url.startswith("magnet"):
            url = "magnet:?xt=urn:btih:" + url

        # Ejecutar en Elementum
        if url.lower().startswith('magnet:') or url.lower().endswith('.torrent'):
            platformtools.dialog_notification("ButacaVip", "Abriendo Elementum...", time=1000)
            try:
                url_encoded = urllib.parse.quote_plus(url)
                media_url = "plugin://plugin.video.elementum/play?uri=" + url_encoded
                xbmc.executebuiltin('PlayMedia(' + media_url + ')')
            except:
                pass
        else:
            platformtools.dialog_notification("Error", "Solo Magnets o Torrents", time=3000)
                
def open_settings(item):
    import xbmc
    xbmc.executebuiltin('Addon.OpenSettings(plugin.video.butacavip)')