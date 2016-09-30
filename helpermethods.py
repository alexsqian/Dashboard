from gviz_data_table import encode
from gviz_data_table import Table
import collections
import datetime

class DataFormat(object):
	def create_aggregate(self, appledata, androiddata, ajaxdata):
		all_the_apps = collections.OrderedDict()
		for applerow in appledata["rows"]:
			date = datetime.datetime.strptime(str(applerow["f"][0]["v"]), '%Y-%m-%d').date()
			apple_id = int(applerow["f"][3]["v"])
			installs = int(applerow["f"][1]["v"])
			if date not in all_the_apps:
				all_the_apps[date] = {}
			for appinfo in ajaxdata:
				if appinfo["ios"] == apple_id and appinfo["name"] not in all_the_apps[date]:
					all_the_apps[date][appinfo["name"]] = installs

		for androidrow in androiddata["rows"]:
			date = datetime.datetime.strptime(str(androidrow["f"][0]["v"]), '%Y-%m-%d').date()
			name = str(androidrow["f"][2]["v"])
			installs = int(androidrow["f"][1]["v"])
			if date not in all_the_apps:
				all_the_apps[date] = {}
			for appinfo in ajaxdata:
				if appinfo["android"] == name and appinfo["name"] in all_the_apps[date]:
					all_the_apps[date][appinfo["name"]] = all_the_apps[date][appinfo["name"]] + installs 

		table = Table()
		table.add_column("date", datetime.date, "Date")
		table.add_column("uploader", int, "Uploader")
		table.add_column("faspex", int, "Faspex")
		table.add_column("drive", int, "Drive")
		table.add_column("files", int, "Files")

		for date, values in all_the_apps.items():
			table.append([date, values.get("Uploader", 0), values.get("Faspex", 0), values.get("Drive", 0), values.get("Files", 0)])

		return encode(table)

	def create_totals(self, appletotals, androidtotals, ajaxdata):
		table = Table()
		table.add_column("appname", str, "App Name")
		table.add_column("apple", int, "Apple Total Installs")
		table.add_column("android", int, "Android Currently Installed")
		table.add_column("android2", int, "Android Total Users")

		all_the_apps = collections.OrderedDict()
		for appinfo in ajaxdata:
			all_the_apps[str(appinfo["name"])] = {}
			for applerow in appletotals["rows"]:
				apple_id = int(applerow["f"][0]["v"])
				installs = int(applerow["f"][1]["v"])
				if appinfo["ios"] == apple_id:
					all_the_apps[appinfo["name"]]["Apple"] = installs
			for androidrow in androidtotals["rows"]:
				name = str(androidrow["f"][0]["v"])
				current_device_installs = int(androidrow["f"][1]["v"])
				total_user_installs = int(androidrow["f"][2]["v"])
				if appinfo["android"] == name:
					all_the_apps[appinfo["name"]]["AndroidCurrent"] = current_device_installs
					all_the_apps[appinfo["name"]]["AndroidTotal"] = total_user_installs

		for name, values in all_the_apps.items():
			print name
			table.append([name, values.get("Apple", 0), values.get("AndroidCurrent", 0), values.get("AndroidTotal", 0)])

		# for applerow in appletotals["rows"]:
		# 	apple_id = int(applerow["f"][0]["v"])
		# 	installs = int(applerow["f"][1]["v"])
		# 	for appinfo in ajaxdata:
		# 		if appinfo["ios"] == apple_id and appinfo["ios"] not in all_the_apps:
		# 			all_the_apps[appinfo["name"]] = installs

		# for androidrow in androidtotals["rows"]:
		# 	name = str(androidrow["f"][0]["v"])
		# 	current_device_installs = int(androidrow["f"][1]["v"])
		# 	total_user_installs = int(androidrow["f"][2]["v"])


		return encode(table)


	def formatData(self, appinfo, appledata, androiddata):

		iosID = appinfo["ios"]
		androidName = appinfo["android"]

		# Since data is all aggregated, we iterate through the query list and check if the app name appears in our query
		# The counter is used to keep track if an app is there or not
		# The values is the final data sent back to the javascript to be turned into a graph
		counter = 0
		values = ""

		# Check if the query data contains the appname
		for androidrow in androiddata["rows"]:
			if str(androidrow["f"][2]["v"]) == androidName: 
				counter += 1
		if counter == 0:
			values = self.convertAppledata(appledata, iosID)

		counter = 0

		# Check if the query data contains the appname
		for applerow in appledata["rows"]:
			if int(applerow["f"][3]["v"]) == iosID:
				counter += 1
		if counter == 0:
			values = self.convertAndroiddata(androiddata, androidName)

		# if values are still empty, then that means both apple/andorid has data for the app
		# proceed to combine data together
		#Value are structured according to a table:
		# Column 1 is the week, column 2 is apple installs, and column 3 is android installs
		if values == "":
			values = self.convertdata(appledata, androiddata, iosID, androidName)

		# Create a dictionary of the data that the javascript will use

		return values
		

	def convertdata(self, appledata, androiddata, iosID, androidName):
		# Create a table object from Google's gviz_table python script
		# That table is already well formatted to accomodate google charts 
		table = Table()
		table.add_column("date", datetime.date, "Date")
		table.add_column("apple", int, "Apple")
		table.add_column("android", int, "Android")

		# The code below is really messy, but I couldn't think of any better/faster way to do it
		# Checks android data, if the name matches the app name we're looking for
		# then for each row find the appropiate apple data that matches appname and week, 
		# and add the android data into [2] column of apple data
		for androidrow in androiddata["rows"]:
			if str(androidrow["f"][2]["v"]) == androidName:
				for applerow in appledata["rows"]:
					if (str(androidrow["f"][0]["v"]) == str(applerow["f"][0]["v"]) and int(applerow["f"][3]["v"]) == iosID ):
						applerow["f"][2]["v"] = int(androidrow["f"][1]["v"])

		# Looks for the data matching the appname
		# [2] column data contains a mix of android data/strings returned from query
		# convert all strings to 0 so it's not graphed
		# appends it to the table, converting the apple date from string to date object
		for applerow in appledata["rows"]:
			if int(applerow["f"][3]["v"]) == iosID:
				if not isinstance(applerow["f"][2]["v"], int):
					applerow["f"][2]["v"] = 0
				table.append([datetime.datetime.strptime(str(applerow["f"][0]["v"]), '%Y-%m-%d').date(), int(applerow["f"][1]["v"]), int(applerow["f"][2]["v"])])
		return encode(table)

		# called if no android data exists
	def convertAppledata(self, appledata, iosID):
		table = Table()
		table.add_column("date", datetime.date, "Date")
		table.add_column("apple", int, "Apple")
		for applerow in appledata["rows"]:
			if int(applerow["f"][3]["v"]) == iosID:
				table.append([datetime.datetime.strptime(str(applerow["f"][0]["v"]), '%Y-%m-%d').date(), int(applerow["f"][1]["v"])])
		return encode(table)


		# called if no apple data exists
	def convertAndroiddata(self, androiddata, androidName):
		table = Table()
		table.add_column("date", str, "Date")
		table.add_column("apple", int, "Android")
		for androidrow in androiddata["rows"]:
			if str(androidrow["f"][2]["v"]) == androidName:
				table.append([datetime.datetime.strptime(str(androidrow["f"][0]["v"]), '%Y-%m-%d').date(), int(androidrow["f"][1]["v"])])
		return encode(table)