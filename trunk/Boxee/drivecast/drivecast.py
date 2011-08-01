# -*- coding: utf-8 -*-

import sys, urllib, urllib2, unicodedata, mc, httplib, threading
from simplejson import load
from simplejson import loads
from xml.dom.minidom import parse, parseString
from time import sleep
from base64 import standard_b64decode

# plugin constants
__url__ = 'https://drivecast.eu/'
__api_version__ = 'api/2.0/'
__api_key__ = "QXz8eEdSeKDoBvg4CzX4gU3n6MnliMZ9"
__device__ = "&name=Boxee&dev_type=boxee"

def log(up):
	config = mc.GetApp().GetLocalConfig()
	rssURL= read_resource(up, "feed")
	config.SetValue("rss",str(rssURL["feedURL"]))
	mc.HideDialogWait()
	config.Reset("up")
	mc.ActivateWindow(15000)

#========================================================================================
#	LETTURA LIBRERIA UTENTE														<<<OK>>>>
#========================================================================================

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
		request = urllib2.Request(feed+""+__device__)
		opener = urllib2.urlopen(request).read()
		return parseString(opener)
	except urllib2.HTTPError, e:
		print " ---RSS HTTP ERROR--- : " + str(e.code)
	except urllib2.URLError, e:
		print " ---RSS URL ERROR--- : " + str(e.reason)

#========================================================================================
#	LISTA INVISIBILE																<<<OK>>>>
#========================================================================================

def manage_RSS():
	__rss__ = read_RSS(mc.GetApp().GetLocalConfig().GetValue("rss"))
	wind = mc.GetActiveWindow()
	lista = mc.ListItems()
	playl = mc.ListItems()
	itempl = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
	itempl.SetLabel("Library")
	itempl.SetProperty("pl","")
	itempl.SetThumbnail("library.png")
	playl.append(itempl)
	exist= {}
	for item in __rss__.getElementsByTagName('item'):
		if item.getElementsByTagName('carcast:playlists_string'):
			item_playlist = item.getElementsByTagName('carcast:playlists_string')[0].firstChild.data.encode('utf-8')
		else:
			item_playlist = None
		item_url = item.getElementsByTagName('guid')[0].firstChild.data.encode('utf-8')
		item_title = item.getElementsByTagName("title")[0].firstChild.data.encode('utf-8')
		item_author = item.getElementsByTagName("author")[0].firstChild.data.encode('utf-8')
		item_thumb = item.getElementsByTagName("carcast:thumbnail")[0].firstChild.data.encode('utf-8')
		item_type = item.getElementsByTagName("carcast:element_type")[0].firstChild.data.encode('utf-8')
		desc = item.getElementsByTagName('description')[0].firstChild
		if desc == None:
			item_desc = "No description avaible"
		else:
			item_desc = desc.data.encode('utf-8')
		if item_type==("video"):
			elem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_OTHER)
			elem.SetGenre("video_icon.png")
		elif item_type==("audio"):
			elem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_MUSIC)
			elem.SetGenre("audio_icon.png")
		else:
			elem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_RADIO)
			elem.SetGenre("radio_icon.png")
		elem.SetTitle(item_title)
		elem.SetLabel(item_title)
		elem.SetArtist(item_author)
		elem.SetPath(item_url)
		elem.SetThumbnail(item_thumb)
		elem.SetContentType(item_type)
		if item_playlist != None:
			temp="["+item_playlist+"]"
			playli= temp[1:-1].split(',')
			for pla in playli:
				exist[pla]= 0
			elem.SetProperty("pl",item_playlist)
		elem.SetDescription(item_desc)
		lista.append(elem)
	for plname in exist:
		itempl = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		itempl.SetLabel(plname)
		itempl.SetProperty("pl",plname)
		itempl.SetThumbnail("playlist.png")
		playl.append(itempl)
	listaOUT = wind.GetList(1200)
	listaOUT.SetItems(lista)
	listaOUT.SetVisible(True)
	playlistOUT = wind.GetList(9001)
	playlistOUT.SetItems(playl)
	playlistOUT.SetVisible(True)

#========================================================================================
#	QRCODE																		<<<OK>>>>
#========================================================================================

def qrcode_post():
	conn = httplib.HTTPSConnection("drivecast.eu:443")
	conn.request("POST", "/"+__api_version__+"pair/AppleTV/AppleTV")
	response = conn.getresponse()
	data= loads(response.read())
	conn.close()
	win= mc.GetActiveWindow()
	win.GetImage(2000).SetTexture(str(data["QRcode"])+".png")
	pair= str(data["paircode"])
	mc.GetApp().GetLocalConfig().SetValue("qr",pair)
	win.GetLabel(2001).SetLabel(pair)

class qrcode_get(threading.Thread):
	def run(self):
		conf= mc.GetApp().GetLocalConfig()
		qr= conf.GetValue("qr")
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
				us = standard_b64decode(up).split(":")[0]
				mc.GetApp().GetLocalConfig().SetValue("username",us)
				conf.Reset("qr")
				log(up)

#========================================================================================
#	GUEST USER																	<<<OK>>>>
#========================================================================================
def guest():
	params= urllib.urlencode({'username': 'guest', 'type': 'drivecast', 'useragent': 'Boxee', 'device_type' : 'boxee', 'device_name' : 'boxee'})
	header= {"Content-type": "application/x-www-form-urlencoded"}
	conn = httplib.HTTPConnection("widgets.inrete.it:80")
	conn.request("POST", "/widget-boxee.php", params, header)
	response = conn.getresponse()
	res= response.read()
	data= parseString(res.split("?>")[1])
	conn.close()
	lista = mc.ListItems()
	for item in data.getElementsByTagName('item'):
		if item.getElementsByTagName('carcast:playlists_string'):
			item_playlist = item.getElementsByTagName('carcast:playlists_string')[0].firstChild.data.encode('utf-8')
		else:
			item_playlist = None
		item_url = item.getElementsByTagName('url')[0].firstChild.data.encode('utf-8')
		item_title = item.getElementsByTagName("title")[0].firstChild.data.encode('utf-8')
		item_author = item.getElementsByTagName("author")[0].firstChild.data.encode('utf-8')
		item_thumb = item.getElementsByTagName("thumbnail")[0].firstChild.data.encode('utf-8')
		item_type = item.getElementsByTagName("type")[0].firstChild.data.encode('utf-8')
		desc = item.getElementsByTagName('description')[0].firstChild
		if desc == None:
			item_desc = "No description avaible"
		else:
			item_desc = desc.data.encode('utf-8')
		if item_type==("video"):
			elem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_OTHER)
			elem.SetGenre("video_icon.png")
		elif item_type==("audio"):
			elem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_MUSIC)
			elem.SetGenre("audio_icon.png")
		else:
			elem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_RADIO)
			elem.SetGenre("radio_icon.png")
		elem.SetTitle(item_title)
		elem.SetLabel(item_title)
		elem.SetArtist(item_author)
		elem.SetPath(item_url)
		elem.SetThumbnail(item_thumb)
		if item_playlist != None:
			elem.SetProperty("pl",item_playlist)
		elem.SetDescription(item_desc)
		lista.append(elem)
	listaOUT = mc.GetWindow(15000).GetList(1200)
	listaOUT.SetItems(lista)
	listaOUT.SetVisible(True)
	
	playl = mc.ListItems()
	item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
	item.SetLabel("Library")
	item.SetProperty("pl","")
	item.SetThumbnail("library.png")
	playl.append(item)
	playlistOUT = mc.GetActiveWindow().GetList(9001)
	playlistOUT.SetItems(playl)
	playlistOUT.SetVisible(True)
