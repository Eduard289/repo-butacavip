# -*- coding: utf-8 -*-

import os, re, time, datetime, sys

# --- CORRECCIÓN DE RUTAS (Vital para 'No module named lib') ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    lib_dir = os.path.join(root_dir, 'lib')
    if os.path.exists(lib_dir) and lib_dir not in sys.path:
        sys.path.append(lib_dir)
except:
    pass
# -------------------------------------------------------------

from core import httptools, scrapertools, jsontools, filetools
from core.item import Item
from platformcode import config, logger, platformtools

PY3 = False
if config.get_setting('PY3', default=''): PY3 = True

if PY3:
    unicode = str
    from urllib.parse import parse_qs, urlparse
else:
    from urlparse import parse_qs, urlparse    

dict_servers_parameters = {}

def find_video_items(item=None, data=None):
    logger.info()
    itemlist = []
    if data is None and item is None: return itemlist
    if data is None: data = httptools.downloadpage(item.url).data
    if item is None: item = Item()

    for label, url, server in findvideos(data):
        title = "Enlace encontrado en %s" % label
        itemlist.append(Item(channel=item.channel, action='play', title=title, url=url, server=server))
    return itemlist

def normalize_url(serverid, url):
    new_url = url 
    server_parameters = get_server_parameters(serverid)
    for pattern in server_parameters.get("find_videos", {}).get("patterns", []):
        found = False
        if not isinstance(url, str): url = (str(url))
        if not PY3 and isinstance(url, unicode): url = url.encode('utf-8', 'strict')
        elif PY3 and isinstance(url, bytes): url = url.decode('utf-8', 'strict')

        for match in re.compile(pattern["pattern"], re.DOTALL).finditer(url):
            new_url = pattern["url"]
            for x in range(len(match.groups())):
                new_url = new_url.replace("\\%s" % (x + 1), match.groups()[x])
            ignore_urls = server_parameters["find_videos"].get("ignore_urls", [])
            if new_url not in ignore_urls:
                if str(ignore_urls) == "['https://vk.com/video']" or str(ignore_urls) == "['https://vtbe.to']":
                    new_url = url
                found = True
            else:
                new_url = url
            break
        if found: break
    return new_url

def get_servers_itemlist(itemlist):
    for serverid in get_servers_list().keys():
        server_parameters = get_server_parameters(serverid)
        if server_parameters.get("active") == False: continue
        for pattern in server_parameters.get("find_videos", {}).get("patterns", []):
            for match in re.compile(pattern["pattern"], re.DOTALL).finditer("\n".join([item.url.split('|')[0] for item in itemlist if not item.server])):
                url = pattern["url"]
                for x in range(len(match.groups())):
                    url = url.replace("\\%s" % (x + 1), match.groups()[x])
                for item in itemlist:
                    if match.group() in item.url:
                        item.server = serverid
                        if '|' in item.url: item.url = url + '|' + item.url.split('|')[1]
                        else: item.url = url
    for item in itemlist:
        if not item.server and item.url: item.server = "desconocido" 
    return itemlist

def findvideos(data, skip=False, disabled_servers=False):
    logger.info()
    devuelve = []
    skip = int(skip)
    servers_list = get_servers_list().keys()
    for serverid in servers_list:
        if not disabled_servers and not is_server_enabled(serverid): continue
        devuelve.extend(findvideosbyserver(data, serverid, disabled_servers=disabled_servers))
        if skip and len(devuelve) >= skip:
            devuelve = devuelve[:skip]
            break
    return devuelve

def findvideosbyserver(data, serverid, disabled_servers=False):
    devuelve = []
    serverid = get_server_id(serverid)
    if not disabled_servers and not is_server_enabled(serverid): return devuelve
    server_parameters = get_server_parameters(serverid)
    if "find_videos" in server_parameters:
        for pattern in server_parameters["find_videos"].get("patterns", []):
            msg = "%s\npattern: %s" % (serverid, pattern["pattern"])
            if not isinstance(data, str): data = (str(data))
            if not PY3 and isinstance(data, unicode): data = data.encode('utf-8', 'strict')
            elif PY3 and isinstance(data, bytes): data = data.decode('utf-8', 'strict')
            for match in re.compile(pattern["pattern"], re.DOTALL).finditer(data):
                url = pattern["url"]
                for x in range(len(match.groups())):
                    url = url.replace("\\%s" % (x + 1), match.groups()[x])
                value = server_parameters["name"], url, serverid
                if value not in devuelve and url not in server_parameters["find_videos"].get("ignore_urls", []):
                    devuelve.append(value)
                msg += "\nurl encontrada: %s" % url
                logger.info(msg)
    return devuelve

def get_server_from_url(url, disabled_servers=False):
    encontrado = findvideos(url, skip=True, disabled_servers=disabled_servers)
    if len(encontrado) > 0: return encontrado[0][2]
    else:
        if not disabled_servers: return 'directo'
        else: return None

# --- PUENTE RESOLVEURL ---
def resolve_video_urls_for_playing(server, url, url_referer=''):
    video_urls = []
    logger.info("Server: %s, Url: %s" % (server, url))
    server = get_server_id(server)

    if server == "directo" or server == "local":
        video_urls.append(["%s [%s]" % (urlparse(url)[2][-4:], server), url])
    else:
        # Intentamos usar ResolveURL PRIMERO
        try:
            import resolveurl
            hmf = resolveurl.HostedMediaFile(url=url)
            if hmf.valid_url():
                logger.info("ButacaVip: ResolveURL detectado -> %s" % url)
                resolved = hmf.resolve()
                if resolved:
                    video_urls.append(["%s [ResolveURL]" % server.capitalize(), resolved])
                    return video_urls, True, ''
        except Exception as e:
            logger.info("ButacaVip: Salto ResolveURL (%s)" % str(e))

        # Si falla, usamos el conector interno (Ahora con lib arreglado)
        server_parameters = get_server_parameters(server) if server else {}
        server_name = server_parameters['name'] if 'name' in server_parameters else server.capitalize()

        if 'active' not in server_parameters:
            return [], False, '[COLOR red]Falta el Servidor[/COLOR] %s' % server_name

        if server_parameters['active'] == False:
            return [], False, '%s [COLOR red]Servidor Inactivo.[/COLOR]' % server_name

        try:
            server_module = __import__('servers.%s' % server, None, None, ["servers.%s" % server])
            response = server_module.get_video_url(page_url=url, url_referer=url_referer)
            if isinstance(response, list) and len(response) > 0:
                video_urls.extend(response)
            elif not isinstance(response, list):
                return [], False, response
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
            return [], False, 'Error interno: %s' % server_name

        if len(video_urls) == 0:
            return [], False, 'Vídeo No localizado en %s' % server_name

    return video_urls, True, ''

# --- FUNCIONES DE AYUDA (Restauradas para evitar el crash) ---
def get_server_id(serverid):
    return corregir_servidor(serverid)

def corregir_servidor(servidor):
    servidor = servidor.strip().lower()
    if servidor in ['netuplayer', 'netutv', 'waaw', 'zures']: return 'waaw'
    elif servidor in ['doodstream', 'dood']: return 'doodstream'
    return servidor

def corregir_other(servidor):
    """Función alias necesaria para dpeliculas.py"""
    return corregir_servidor(servidor)

def corregir_zures(servidor):
    """Función alias necesaria para algunos canales"""
    return corregir_servidor(servidor)
# -------------------------------------------------------------

def is_server_enabled(server):
    server_parameters = get_server_parameters(server)
    if 'active' not in str(server_parameters) or server_parameters['active'] == False: return False
    return config.get_setting('status', server=server, default=0) >= 0

def is_server_available(server):
    path = os.path.join(config.get_runtime_path(), 'servers', server + '.json')
    return os.path.isfile(path)

def get_server_parameters(server):
    global dict_servers_parameters
    if server not in dict_servers_parameters:
        try:
            if server == 'desconocido': 
                dict_server = {'active': False, 'id': 'desconocido', 'name': 'Desconocido'}
                dict_servers_parameters[server] = dict_server
                return dict_server
            path = os.path.join(config.get_runtime_path(), 'servers', server + '.json')
            if not os.path.isfile(path): return {}
            data = filetools.read(path)
            dict_server = jsontools.load(data)
            dict_server['active'] = dict_server.get('active', False)
            if 'find_videos' in dict_server:
                dict_server['find_videos']['patterns'] = dict_server['find_videos'].get('patterns', list())
                dict_server['find_videos']['ignore_urls'] = dict_server['find_videos'].get('ignore_urls', list())
            dict_servers_parameters[server] = dict_server
        except: return {}
    return dict_servers_parameters[server]

def get_server_setting(name, server, default=None):
    return config.get_setting('server_' + server + '_' + name, default=default)

def set_server_setting(name, value, server):
    return config.set_setting('server_' + server + '_' + name, value)

def get_servers_list():
    server_list = {}
    for server in os.listdir(os.path.join(config.get_runtime_path(), 'servers')):
        if server.endswith('.json'):
            serverid = server.replace('.json', '')
            server_list[serverid] = get_server_parameters(serverid)
    return server_list

def filter_and_sort_by_quality(itemlist):
    return itemlist

def filter_and_sort_by_server(itemlist):
    return itemlist

def filter_and_sort_by_language(itemlist):
    return itemlist

def get_parse_hls(video_urls):
    return video_urls