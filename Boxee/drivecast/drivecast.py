# -*- coding: utf-8 -*-

import sys, urllib, urllib2, unicodedata, mc
from simplejson import load
from base64 import b64encode
from xml.dom.minidom import parseString

# plugin constants
__url__ = 'https://drivecast.eu'
__api_key__ = "QXz8eEdSeKDoBvg4CzX4gU3n6MnliMZ9"
#__thumbnails__ = __settings__.getAddonInfo('path')+"/thumbnails/"

config = mc.GetApp().GetLocalConfig()

def log():
	username = config.GetValue("username")	#USERNAME
	password = config.GetValue("password")	#PASSWORD
	if username=="" or password=="":
		return login()
	else:
		aut = b64encode(username+':'+password)	#AUTENTICAZIONE IN BASE64
		return read_RSS(read_resource(__url__, aut, "feed"))

def login():
	username = config.GetValue("username")	#USERNAME
	password = config.GetValue("password")	#PASSWORD
	aut = b64encode(username+':'+password)	#AUTENTICAZIONE IN BASE64
	try:
		rss = read_RSS(read_resource(__url__, aut, "feed"))
		return rss
	except:
		username = mc.ShowDialogKeyboard("Enter Username", "")	#USERNAME
		password = mc.ShowDialogKeyboard("Enter Password", "", True)	#PASSWORD
		return None

#========================================================================================
#	LETTURA LIBRERIA UTENTE														<<<OK>>>>
#========================================================================================

#========================================================================================
#	API																			<<<OK>>>>
#========================================================================================
def read_resource(aut, resource):
	try:
		request = urllib2.Request(__url__+"/api/2.0/"+resource+"?fmt=xml")
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

