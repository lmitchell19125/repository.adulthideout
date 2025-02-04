import os
import re
import json
import six
import urllib
import sys
import importlib
from kodi_six import xbmc, xbmcvfs, xbmcaddon, xbmcplugin, xbmcgui
from six.moves import urllib_request, urllib_parse, http_cookiejar
from resources.search import *
from resources.websites.websites import websites
from resources.functions import *
import urllib.parse
import logging

search_results = None
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

xbmcplugin.setContent(addon_handle, 'movies')
addon = xbmcaddon.Addon()
viewtype = int(addon.getSetting('viewtype'))
view_modes = [50, 51, 500, 501, 502]
view_mode = view_modes[viewtype]
xbmc.executebuiltin('Container.SetViewMode({})'.format(view_mode))

def menulist():
    try:
        with open(homemenu, 'r') as mainmenu:
            content = mainmenu.read()
            match = re.findall('#.+,(.+?)\n(.+?)\n', content)
            return match
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print("An unknown error occurred: ", e)

def main():
    for site in websites:
        name = site['name']
        url = site['url']
        add_dir(f'{name.capitalize()} [COLOR yellow] Videos[/COLOR]', url, 2, logos + f'{name}.png', fanart)

def start(url):
    addon_handle = int(sys.argv[1])
    add_home_button()
    xbmc.log('start function called with URL: ' + url, xbmc.LOGINFO)
    for site in websites:
        if url.startswith(site["url"]):
            site["function"](url)
            break
    xbmcplugin.setContent(addon_handle, 'movies')
    addon = xbmcaddon.Addon()
    viewtype = int(addon.getSetting('viewtype'))
    view_modes = [50, 51, 500, 501, 502]
    view_mode = view_modes[viewtype]
    xbmc.executebuiltin('Container.SetViewMode({})'.format(view_mode))

def add_home_button():
    add_dir("Home", "", 100, os.path.join(logos, 'adulthideout.png'), fanart)

def process_website(url):
    parsed_input_url = urlparse(url)
    input_domain = parsed_input_url.netloc.replace("www.", "")
    
    input_domain = re.sub(r'^[a-z]{2}\.', "", input_domain)
    
    print(f"Input domain: {input_domain}")  # Log statement
    
    search_results = []
    
    for site in websites:
        parsed_site_url = urlparse(site["url"])
        site_domain = parsed_site_url.netloc.replace("www.", "")
        
        site_domain = re.sub(r'^[a-z]{2}\.', "", site_domain)
        
        print(f"Comparing input domain '{input_domain}' with site domain '{site_domain}'")  # Log statement
        
        if site_domain == input_domain:
            function_name = site["function"].replace("-", "_")
            print(f"Matching website found: {site['name']}. Calling function {function_name}.")
            try:
                search_results = eval(f"{function_name}(url)")
            except Exception as e:
                print(f"An error occurred while executing the function {function_name}: ", e)
            break
                
    return search_results
    xbmcplugin.setContent(addon_handle, 'movies')
    addon = xbmcaddon.Addon()
    viewtype = int(addon.getSetting('viewtype'))
    view_modes = [50, 51, 500, 501, 502]
    view_mode = view_modes[viewtype]
    xbmc.executebuiltin('Container.SetViewMode({})'.format(view_mode))

def search_website(website_name):
    site = next((site for site in websites if site["name"] == website_name or site["url"].find(website_name) != -1), None)
    if site is None:
        return

    last_query = get_last_query()
    keyb = xbmc.Keyboard(str(last_query), "[COLOR yellow]Enter search text[/COLOR]")
    all_queries = get_all_queries()
    options = ["[COLOR yellow]New Search[/COLOR]"] + all_queries + ["[COLOR yellow]Clear Search History[/COLOR]"]
    valid_options = [option for option in options if isinstance(option, str)]
    selected_index = xbmcgui.Dialog().select("Select a Query", valid_options)

    if selected_index >= 0 and selected_index == 0:
        keyb.doModal()
        if keyb.isConfirmed():
            search_word = keyb.getText()
            search_word_encoded = urllib.parse.quote_plus(search_word)
            if search_word not in all_queries:
                save_query(search_word)

            search_url = site["search_url"].replace("{}", search_word_encoded)
            xbmc.log("Search URL: " + search_url, xbmc.LOGINFO)
            site["function"](search_url, 1)
    elif selected_index >= 0 and selected_index > 0 and selected_index < len(valid_options) - 1:
        search_word = valid_options[selected_index]
        search_word_encoded = urllib.parse.quote_plus(search_word)

        search_url = site["search_url"].replace("{}", search_word_encoded)
        site["function"](search_url)
    elif selected_index >= 0 and selected_index == len(valid_options) - 1:
        clear_search_history()
    xbmcplugin.setPluginCategory(int(sys.argv[1]), 'Search Results')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play_video(url):
    media_url = resolve_url(url, websites)
    listitem = xbmcgui.ListItem(path=media_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)


def get_params():
    param = {}
    try:
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
            params = sys.argv[2]
            cleanedparams = params.replace('?', '')
            if (params[len(params) - 1] == '/'):
                params = params[0:len(params) - 2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for pair in pairsofparams:
                if '=' in pair:
                    key, value = pair.split('=')
                    param[key] = value
    except:
        pass
    return param


if __name__ == '__main__':
    params = get_params()
    url = params.get("url") and urllib_parse.unquote_plus(params["url"])
    name = params.get("name") and urllib_parse.unquote_plus(params["name"])
    mode = params.get("mode") and int(params["mode"])
    iconimage = params.get("iconimage") and urllib_parse.unquote_plus(params["iconimage"])

    if mode is None or url is None or len(url) < 1:
        if search_results is not None:
            show_search_results()
        else:
            main()
    elif mode == 1:
        search_website(name)
    elif mode == 2:
        start(url)
    elif mode == 3:
        media_list(url)
    elif mode == 4:
        play_video(url)
    elif mode == 5:
        search_website(url)
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))