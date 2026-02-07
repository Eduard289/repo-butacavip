# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# httptools (Versión Restaurada y Blindada)
# ------------------------------------------------------------

import os
import sys
import time
import ssl
import gzip
import io

# Importaciones de Python 3
import urllib.parse as urllib_parse
import urllib.request as urllib_request
import urllib.error as urllib_error
import http.cookiejar as cookielib

from platformcode import config, logger

# --- GESTIÓN INTELIGENTE DE SSL ---
try:
    ssl_context = ssl._create_unverified_context()
except AttributeError:
    ssl_context = None

def downloadpage(url, post=None, headers=None, timeout=None, cookies=None, user_agent=None, referer=None, follow_redirects=True, **kwargs):
    """
    Función de descarga robusta que corrige URLs, cabeceras y tipos al vuelo.
    """
    
    # 1. CORRECCIÓN DE TIMEOUT
    if not timeout:
        timeout = config.get_setting("timeout")
        if not timeout: timeout = 20

    # 2. SANITIZACIÓN DE CABECERAS
    clean_headers = []
    if headers:
        if isinstance(headers, dict):
            for k, v in headers.items():
                clean_headers.append((str(k), str(v)))
        elif isinstance(headers, list):
            for item in headers:
                if len(item) == 2:
                    clean_headers.append((str(item[0]), str(item[1])))
    
    # 3. USER-AGENT
    if not user_agent:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    req_headers = {
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip, deflate"
    }
    if referer:
        req_headers["Referer"] = referer

    # 4. GESTIÓN DE COOKIES
    cj = cookielib.LWPCookieJar()
    if cookies:
        for cookie in cookies:
            try: cj.set_cookie(cookie)
            except: pass

    # 5. HANDLERS Y SSL
    handlers = [urllib_request.HTTPHandler(), urllib_request.HTTPCookieProcessor(cj)]
    
    if ssl_context:
        handlers.append(urllib_request.HTTPSHandler(context=ssl_context))
    else:
        handlers.append(urllib_request.HTTPSHandler())
    
    if not follow_redirects:
        class NoRedirectHandler(urllib_request.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers): return fp
            http_error_301 = http_error_303 = http_error_307 = http_error_302
        handlers.append(NoRedirectHandler())

    opener = urllib_request.build_opener(*handlers)
    
    # 6. SANITIZACIÓN DE URL Y POST
    if isinstance(url, bytes):
        url = url.decode('utf-8', 'ignore')
    
    if isinstance(url, str):
        url = url.replace(' ', '%20') 

    if post:
        if isinstance(post, dict):
            post = urllib_parse.urlencode(post).encode('utf-8')
        elif isinstance(post, str):
            post = post.encode('utf-8')
    
    request = urllib_request.Request(url, data=post)

    for key, value in clean_headers:
        request.add_header(key, value)
    
    for key, value in req_headers.items():
        if not request.has_header(key):
            request.add_header(key, value)

    # --- INTENTO DE CONEXIÓN ---
    response_data = ""
    response_code = 500
    response_headers = {}
    response_url = url
    success = False
    error_msg = ""

    try:
        response = opener.open(request, timeout=timeout)
        
        data_bytes = response.read()
        response_headers = response.info()
        response_url = response.geturl()
        response_code = response.getcode()
        success = True
        
        # 7. DESCOMPRESIÓN (GZIP)
        encoding = response_headers.get('Content-Encoding', '').lower()
        if 'gzip' in encoding:
            try:
                buf = io.BytesIO(data_bytes)
                f = gzip.GzipFile(fileobj=buf)
                data_bytes = f.read()
            except Exception as e:
                logger.error("httptools: Error descomprimiendo GZIP: %s" % e)

        try:
            response_data = data_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                response_data = data_bytes.decode('iso-8859-1')
            except:
                response_data = data_bytes.decode('utf-8', 'ignore')

        response.close()

    except urllib_error.HTTPError as e:
        success = False
        response_code = e.code
        error_msg = str(e)
        try:
            response_data = e.read().decode('utf-8', 'ignore')
        except:
            response_data = str(e)

    except Exception as e:
        success = False
        error_msg = str(e)
        response_data = str(e)
        logger.error("httptools: Error Critico: %s" % e)

    # 9. RESULTADO
    result = type('obj', (object,), {
        'sucess': success, 
        'data': response_data,
        'code': response_code,
        'headers': response_headers,
        'url': response_url,
        'error': error_msg
    })

    return result

def get_url_headers(url):
    try:
        if isinstance(url, str):
            url = url.replace(' ', '%20')
            
        if ssl_context:
            response = urllib_request.urlopen(url, timeout=10, context=ssl_context)
        else:
            response = urllib_request.urlopen(url, timeout=10)
        headers = response.info()
        response.close()
        return headers
    except:
        return {}

# --- GESTIÓN DE COOKIES (RECUPERADAS) ---
def save_cookie(name, value, domain):
    try:
        cookie_path = os.path.join(config.get_data_path(), "cookies.dat")
        cj = cookielib.LWPCookieJar(cookie_path)
        if os.path.exists(cookie_path):
            try: cj.load(ignore_discard=True)
            except: pass
        c = cookielib.Cookie(0, name, value, None, False, domain, True, False, '/', True, False, int(time.time()+31536000), False, None, None, {'HttpOnly': None}, False)
        cj.set_cookie(c)
        cj.save(ignore_discard=True)
        return True
    except: return False

def get_cookie(name, domain):
    try:
        cookie_path = os.path.join(config.get_data_path(), "cookies.dat")
        cj = cookielib.LWPCookieJar(cookie_path)
        if os.path.exists(cookie_path):
            try: cj.load(ignore_discard=True)
            except: pass
            for cookie in cj:
                if cookie.name == name and domain in cookie.domain: return cookie.value
        return None
    except: return None

def load_cookies():
    try:
        cookie_path = os.path.join(config.get_data_path(), "cookies.dat")
        cj = cookielib.LWPCookieJar(cookie_path)
        if os.path.exists(cookie_path):
            try: cj.load(ignore_discard=True)
            except: pass
            return list(cj)
        return []
    except: return []

# =========================================================================
# DIAGNÓSTICO (DESACTIVADO PARA EVITAR CRASH)
# =========================================================================
def run_resolveurl_diagnostic():
    # Función vacía para que no de error si alguien la llama, pero no hace nada.
    pass