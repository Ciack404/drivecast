# -*- coding: utf-8 -*-

import sys, xbmc, xbmcaddon, xbmcplugin, xbmcgui, urllib, urllib2, unicodedata, httplib, threading
from simplejson import load, loads
from base64 import b64encode, b64decode
from xml.dom.minidom import parseString

# plugin constants
__url__ = 'https://drivecast.eu/'
__api_version__ = "api/2.0/"
__api_key__ = "QXz8eEdSeKDoBvg4CzX4gU3n6MnliMZ9"
__device__ = "&name=XBMC&dev_type=boxee"
__settings__ = xbmcaddon.Addon(id='plugin.video.drivecast')
__language__ = __settings__.getLocalizedString
__thumbnails__ = __settings__.getAddonInfo('path')+"/thumbnails/"
__rss__= __settings__.getSetting("rss")

#========================================================================================
#	LOG MENU																	<<<OK>>>>
#========================================================================================
def log_menu():
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?guest",listitem=xbmcgui.ListItem("Prova DriveCast come utente guest",iconImage=__thumbnails__+"user.png", thumbnailImage=__thumbnails__+"user.png"),isFolder=True)
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?form",listitem=xbmcgui.ListItem("Login...",iconImage=__thumbnails__+"user.png", thumbnailImage=__thumbnails__+"user.png"),isFolder=True)
	qr= qrcode_post()
	qrcode_get().start()
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?qrcode",listitem=xbmcgui.ListItem("Login via QR Code"+__settings__.getSetting("qr"),iconImage=qr, thumbnailImage=qr),isFolder=True)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

#========================================================================================
#	QRCODE																		<<<OK>>>>
#========================================================================================
def qrcode_post():
	conn = httplib.HTTPSConnection("drivecast.eu:443")
	conn.request("POST", "/"+__api_version__+"pair/AppleTV/AppleTV")
	response = conn.getresponse()
	data= loads(response.read())
	conn.close()
	__settings__.setSetting("qr",str(data["paircode"]))
	return str(data["QRcode"])+".png"

class qrcode_get(threading.Thread):
	def run(self):
		qr= __settings__.getSetting("qr")
		request = ""
		while request!="OK":
			try:
				conn = httplib.HTTPConnection("push.drivecast.eu:80")
				conn.request("GET", "/listen/?channel="+qr)
				request = conn.getresponse().read()
			except urllib2.HTTPError, e:
				print "TIMEOUT"
		if request == "OK":
			get= read_resource("","pair/AppleTV/AppleTV/AppleTV/"+qr)
			if get["statuscode"]!=404:
				up= str(get["Authorization"])
				us = b64decode(up).split(":")[0]
				__settings__.setSetting("login_name",us)
				__settings__.setSetting("qr","")
				log(str(get["Authorization"]))

#========================================================================================
#	LOG FUNCTION																<<<OK>>>>
#========================================================================================
def login_form():
	__settings__.openSettings()
	username = __settings__.getSetting("login_name")	#USERNAME
	password = __settings__.getSetting("login_pass")	#PASSWORD
	aut = b64encode(username+':'+password)	#AUTENTICAZIONE IN BASE64
	try:
		log(aut)
	except:
		xbmc.executebuiltin("Notification("+__language__(30006)+","+__language__(30007)+")")
		xbmc.executebuiltin("Container.Refresh")

def log(up):
	rssURL= read_resource(up, "feed")
	__settings__.setSetting("up",up)
	__settings__.setSetting("rss", str(rssURL["feedURL"]))
	xbmc.executebuiltin("Notification("+__language__(30005)+","+__language__(30007)+")")
	xbmc.executebuiltin("Container.Refresh")

def logout():
	__settings__.setSetting("login_name",'')	#USERNAME
	__settings__.setSetting("login_pass",'')	#PASSWORD
	__settings__.setSetting("rss",'')			#RSS
	__settings__.setSetting("up","")			#USER:PASS

#========================================================================================
#	ELENCO ITEMS																<<<OK>>>>
#========================================================================================
def playlists():
	playl= read_resource(__settings__.getSetting("up"), "playlist?type=Boxee")
	fu= xbmcgui.ListItem(label="Library", thumbnailImage=__thumbnails__+"library.png", path=sys.argv[0])
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys.argv[0], listitem=fu)
	for pl in playl["elements"]:
		u=sys.argv[0]+"?"+pl["name"]
		item= xbmcgui.ListItem(label=pl["name"], thumbnailImage=__thumbnails__+"pl.png", path=u)
		xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=item)
		#addDir("----------  "+pl["name"],"1",__thumbnails__+"pl.png",pl["name"])	#u'\U0001D15F'
	lo= xbmcgui.ListItem(label="Logout...", thumbnailImage=__thumbnails__+"user.png", path=sys.argv[0]+"?logout")
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys.argv[0]+"?logout", listitem=lo)
	

#========================================================================================
#	ELENCO ITEMS																<<<OK>>>>
#========================================================================================
def manage_RSS():
	xbmc.executebuiltin("Container.Udate")
	"""itempl= xbmcgui.ListItem(label="Library", ThumbnailImage=__thumbnails__+"library.png")
	itempl.SetProperty("pl","")
	playl.append(itempl)"""
	lo= xbmcgui.ListItem(label="Logout...", thumbnailImage=__thumbnails__+"user.png", path=sys.argv[0]+"?logout")
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys.argv[0]+"?logout", listitem=lo)
	feed= read_RSS()
	for item in feed.getElementsByTagName('item'):
		item_url = item.getElementsByTagName('guid')[0].firstChild.data.encode('utf-8')					#path
		item_title = item.getElementsByTagName("title")[0].firstChild.data.encode('utf-8')				#label
		item_author = item.getElementsByTagName("author")[0].firstChild.data.encode('utf-8')			#label2
		item_thumb = item.getElementsByTagName("carcast:thumbnail")[0].firstChild.data.encode('utf-8')	#thumbnailimage
		item_type = item.getElementsByTagName("carcast:element_type")[0].firstChild.data.encode('utf-8')
		desc = item.getElementsByTagName('description')[0].firstChild
		elem= xbmcgui.ListItem(label=item_title, label2=item_author, thumbnailImage=item_thumb, path=item_url)
		if item_type==("video"):
			elem.setInfo(type="Video", infoLabels={"Title": item_title})
			elem.setIconImage(__thumbnails__+"video_icon.png")
		elif item_type==("audio"):
			elem.setInfo(type="Music", infoLabels={"Title": item_title})
			elem.setIconImage(__thumbnails__+"audio_icon.png")
		else:
			elem.setInfo(type="Music", infoLabels={"Title": item_title})
			elem.setIconImage(__thumbnails__+"radio_icon.png")
		pl=item.getElementsByTagName('carcast:playlists_string')
		"""if pl:
			item_playlist = pl[0].firstChild.data.encode('utf-8')
			temp="["+item_playlist+"]"
			playli= temp[1:-1].split(',')
			for pla in playli:
				exist[pla]= 0
			elem.SetProperty("pl",item_playlist)
		lista.append((item_url,elem,False))
	for plname in exist:
		itempl=xbmcgui.ListItem(label=plname, ThumbnailImage=__thumbnails__+"playlist.png")
		itempl.SetProperty("pl",plname)
		playl.append(itempl)"""
		xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item_url,listitem=elem)
	#playl E L'ELENCO DELLE PLAYLIST
	#lista È L'ELENCO DELLE ITEM
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

#========================================================================================
#	API																			<<<OK>>>>
#========================================================================================
def read_resource(aut, resource):
	try:
		request = urllib2.Request(__url__+""+__api_version__+""+resource)
		opener = urllib2.build_opener()
		request.add_header('User-Agent','DriveCast apikey='+__api_key__)					# aggiungo apikey all'header
		if aut != "":
			request.add_header('Authorization','Basic '+aut)									# aggiungo dati login utente all'header
		src = load(opener.open(request))
		if (src['statusdesc']=='OK' and src['statuscode']=='200'):						# 'OK' se la richiesta è andata a buon fine
			return src
	except urllib2.HTTPError, e:
		print " ---API HTTP ERROR--- : " + str(e.code)
		raise
	except urllib2.URLError, e:
		print " ---API URL ERROR--- : " + str(e.reason)
		raise

def read_RSS():
	try:
		request = urllib2.Request(__rss__+""+__device__)#__settings__.GetSetting("rss")+""+__device__)
		opener = urllib2.urlopen(request).read()
		return parseString(opener)
	except urllib2.HTTPError, e:
		print " ---RSS HTTP ERROR--- : " + str(e.code)
	except urllib2.URLError, e:
		print " ---RSS URL ERROR--- : " + str(e.reason)

#========================================================================================
#	MAIN																		<<<OK>>>>
#========================================================================================
mode= sys.argv[2][1:]

if __rss__ == "":
	if  mode=="":
		log_menu()
	elif mode=="guest":
		guest()
	elif mode=="form":
		login_form()
else:
	if mode =="logout":
		logout()
		xbmc.executebuiltin("Container.Update("+sys.argv[0]+")")
	else:
		manage_RSS()
