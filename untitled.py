apple = {}
android = {}
apps = ['files', 'drive', 'uploader', 'faspex']

for appname in apps:
	apple[appname] = ("SELECT LEFT((format_utc_usec(week)),10) as week, installs, title FROM (SELECT week, SUM(units) as installs, title FROM (SELECT UTC_USEC_TO_WEEK(PARSE_UTC_USEC(date_for_query), 0) as week, title, units, product_type_identifier FROM [asperadashboard:app_statistics.appledata]) WHERE (product_type_identifier LIKE '1%') and (UPPER (title) CONTAINS UPPER (%s)) GROUP BY title, week ORDER BY week)") % appname
	android[appname] = ("SELECT LEFT((format_utc_usec(week)),10) as week, installs, package_name, FROM ( SELECT week, SUM(daily_device_installs) as installs, package_name FROM ( SELECT UTC_USEC_TO_WEEK(PARSE_UTC_USEC(date), 0) as week, package_name, daily_device_installs FROM [asperadashboard:app_statistics.androiddata]) WHERE UPPER (package_name) CONTAINS UPPER ({0}) GROUP BY week, package_name ORDER BY week )").format(appname)

print apple