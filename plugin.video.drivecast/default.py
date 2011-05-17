# -*- coding: utf-8 -*-

import sys, xbmc, xbmcaddon, xbmcplugin, xbmcgui, urllib, urllib2, unicodedata
from simplejson import load
from base64 import b64encode
from xml.dom.minidom import parseString

# plugin constants
__url__ = 'https://drivecast.eu'
__api_key__ = "QXz8eEdSeKDoBvg4CzX4gU3n6MnliMZ9"
__settings__ = xbmcaddon.Addon(id='plugin.video.drivecast')
__language__ = __settings__.getLocalizedString
__thumbnails__ = __settings__.getAddonInfo('path')+"/thumbnails/"

def MENU():
	username = __settings__.getSetting("login_name")	#USERNAME
	password = __settings__.getSetting("login_pass")	#PASSWORD
	aut = b64encode(username+':'+password)	#AUTENTICAZIONE IN BASE64
	addDir(__language__(30002),__url__,"1",__thumbnails__+"settings.png","")
	addPLAYLIST(read_resource(__url__, aut, "playlist"))
	addDir(__language__(30004),__url__,"2",__thumbnails__+"prova.png","")
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addPLAYLIST(playl):
	for pl in playl["elements"]:
		addDir("[PL] "+pl["name"],__url__,"1",__thumbnails__+"settings.png",pl["name"])

#========================================================================================
#	LOGIN - VISUALIZZATO NELLE CONFIGURAZIONI									<<<OK>>>>
#========================================================================================
def log():
	username = __settings__.getSetting("login_name")	#USERNAME
	password = __settings__.getSetting("login_pass")	#PASSWORD
	if(username=="" or password==""):
		return login()
	else:
		aut = b64encode(username+':'+password)	#AUTENTICAZIONE IN BASE64
		return read_RSS(read_resource(__url__, aut, "feed"))

def login():
	__settings__.openSettings()
	username = __settings__.getSetting("login_name")	#USERNAME
	password = __settings__.getSetting("login_pass")	#PASSWORD
	aut = b64encode(username+':'+password)	#AUTENTICAZIONE IN BASE64
	try:
		rss = read_RSS(read_resource(__url__, aut, "feed"))
		return rss
	except:
		__settings__.setSetting("login_name",'')	#USERNAME
		__settings__.setSetting("login_pass",'')	#PASSWORD

#========================================================================================
#	LOGOUT																		<<<OK>>>>
#========================================================================================
def logout():
	__settings__.setSetting("login_name",'')	#USERNAME
	__settings__.setSetting("login_pass",'')	#PASSWORD

#========================================================================================
#	LETTURA LIBRERIA UTENTE														<<<OK>>>>
#========================================================================================

#========================================================================================
#	API																			<<<OK>>>>
#========================================================================================
def read_resource(url, aut, resource):
	try:
		request = urllib2.Request(url+"/api/2.0/"+resource)
		opener = urllib2.build_opener()
		request.add_header('User-Agent','DriveCast apikey='+__api_key__)					# aggiungo apikey all'header
		request.add_header('Authorization','Basic '+aut)									# aggiungo dati login utente all'header
		src = load(opener.open(request))
		if (src['statusdesc']=='OK' and src['statuscode']=='200'):						# 'OK' se la richiesta è andata a buon fine CONTROLLARE LISTA VUOTA
			return src
	except urllib2.HTTPError, e:
		print " ---API HTTP ERROR--- : " + str(e.code)
		raise
	except urllib2.URLError, e:
		print " ---API URL ERROR--- : " + str(e.reason)
		raise

def read_RSS(feed):
	try:
		request = urllib2.Request(feed["feedURL"])
		opener = urllib2.urlopen(request).read()
		return parseString(opener)
	except urllib2.HTTPError, e:
		print " ---RSS HTTP ERROR--- : " + str(e.code)
		return e.code
	except urllib2.URLError, e:
		print " ---RSS URL ERROR--- : " + str(e.reason)
		return "url_error"

#========================================================================================
#	Creazione lista podcast														<<<OK>>>>
#========================================================================================
def listing(rss, playlist):
	for item in rss.getElementsByTagName('item'):
		pl = item.getElementsByTagName('carcast:playlists_string')[0].firstChild.data
		if(pl==playlist or pl.endswith(","+playlist) or pl.startswith(playlist+",") or pl.find(","+playlist+",")!=-1 or playlist==""):
			item_url = item.getElementsByTagName('guid')[0].firstChild.data
			item_title = item.getElementsByTagName("title")[0].firstChild.data
			item_author = item.getElementsByTagName("author")[0].firstChild.data
			item_thumb = item.getElementsByTagName("carcast:thumbnail")[0].firstChild.data
			addLink(item_title+" - "+item_author,item_url,item_thumb)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

#========================================================================================
#========================================================================================

#========================================================================================
#	ORGANIZZAZIONE LINK MENU													<<<OK>>>>
#========================================================================================
def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def addDir(name,url,mode,iconimage,playlist):
	ok=True
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&playlist="+playlist
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

#========================================================================================
#========================================================================================

#========================================================================================
#	INIZIALIZZAZIONE PARAMETRI PLUGIN	(tramite get)							<<<OK>>>>
#========================================================================================

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

#========================================================================================
#========================================================================================

params=get_params()
mode=None

rss = log()

try:
	mode=int(params["mode"])
	pl=str(params["playlist"])
except:
	pass

if mode==None:
	MENU()
elif mode == 1:
	listing(rss,pl)
elif mode == 2:
	logout()
	rss = None
	while rss==None:
		rss = log()
	MENU()
	#xbmc.executebuiltin("Container.Update")
	#xbmc.executebuiltin("ReplaceWindow(10000,plugin://video/)")
