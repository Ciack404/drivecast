import mc, drivecast

rssURL = mc.GetApp().GetLocalConfig().GetValue("rss")
mc.GetApp().GetLocalConfig().SetValue("refresh","start")
if rssURL:
	mc.ShowDialogWait()
	mc.GetWindow(15000).ClearStateStack(False)
	mc.ActivateWindow(15000)
else:
	mc.ActivateWindow(14000)
