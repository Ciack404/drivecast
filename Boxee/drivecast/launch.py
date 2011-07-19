import mc, drivecast

rssURL = mc.GetApp().GetLocalConfig().GetValue("rss")
if rssURL:
	mc.ShowDialogWait()
	mc.ActivateWindow(15000)
else:
	mc.ActivateWindow(14000)
