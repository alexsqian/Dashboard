import os
import bqclient
import helpermethods
from flask import Flask, session, g, redirect, url_for, abort, render_template, flash, request, json
import json
import datetime
import httplib2
import collections

#Using a service account to avoid having to use GAE as well as not having to log in with OAuth
from oauth2client.service_account import ServiceAccountCredentials

from gviz_data_table import encode
from gviz_data_table import Table

# Necessary variables to access Bigquery. These can all be found on the online dashbaord as well
# The Queries organize the dates by week, sums up the # of installs per week, and gives out the associate data
# Apple query returns week, # of installs during that week, provider (filler space to replace with android), and the app name
# Android query returns week, # of installs during that week, name of the app, name of app (again, as filler for replacing data)
app = Flask(__name__)
DATA_PROJECT_ID = "45926947780"
DATA_PROJECT_NAME = "asperadashboard"
DATASET = "app_statistics"
APPLE_QUERY = ("SELECT LEFT((format_utc_usec(week)),10) as week, installs, provider, apple_identifier FROM (SELECT week, SUM(units) as installs, provider, apple_identifier FROM (SELECT UTC_USEC_TO_WEEK(PARSE_UTC_USEC(date_for_query), 0) as week, apple_identifier, units, provider, product_type_identifier FROM [asperadashboard:app_statistics.appledata]) WHERE (product_type_identifier LIKE '1%') GROUP BY apple_identifier, week, provider ORDER BY apple_identifier, week)")
APPLE_TOTALS_QUERY = ("SELECT apple_identifier, sum(units) as total_units FROM [asperadashboard:app_statistics.applelifetime] where product_type_identifier CONTAINS '1' group by apple_identifier")
ANDROID_QUERY = ("SELECT LEFT((format_utc_usec(week)),10) as week, installs, package_name, placeholder, FROM ( SELECT week, SUM(daily_device_installs) as installs, package_name, package_name as placeholder FROM ( SELECT UTC_USEC_TO_WEEK(PARSE_UTC_USEC(date), 0) as week, package_name, daily_device_installs FROM [asperadashboard:app_statistics.androiddata]) GROUP BY week, package_name, placeholder ORDER BY package_name, week)")
ANDROID_TOTALS_QUERY = ("select t.package_name, t.current_device_installs, t.total_user_installs from [asperadashboard:app_statistics.androiddata] t inner join (select package_name, max(date) as MaxDate from [asperadashboard:app_statistics.androiddata] group by package_name) tm on t.package_name = tm.package_name and t.date = tm.MaxDate")

#empty home page that gets populated later
@app.route('/')
def get():
    return render_template('index.html')


# The ajax script will call post which will be handeled by this post method right here
@app.route('/getdata/', methods=['POST'])
def post():
    # Ajaxdata is the data recieved from the ajax request in the html page
    # The data consists of the common name, ios name, and the android name of each app
    ajaxdata = request.get_json(force=True)
    data = {}

    # OAuth stuff for service account
    scopes = ['https://www.googleapis.com/auth/bigquery']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('asperadashboard-24e526b40f65.json', scopes)
    http = httplib2.Http()
    http = credentials.authorize(http)

    #sets up bigquery client and queries for the data
    bq = bqclient.BigQueryClient(http)
    appledata = query(APPLE_QUERY, bq)
    appletotals = query(APPLE_TOTALS_QUERY, bq)
    androiddata = query(ANDROID_QUERY, bq)
    androidtotals = query(ANDROID_TOTALS_QUERY, bq)

    #sets up the helper to process and format the data. For details how data is processed
    #check the helper method
    helper = helpermethods.DataFormat()

    app_totals = helper.create_totals(appletotals, androidtotals, ajaxdata) #the table of total installs
    aggregate_apps = helper.create_aggregate(appledata, androiddata, ajaxdata) #the actual graph of total installs


    # add everything to the data dictionary as a key-value pair where key = "appname", value is data
    for appinfo in ajaxdata:
        # x is also a dictionary, basically a dict within a dict
        try:
            x = helper.formatData(appinfo, appledata, androiddata)
            data[appinfo["name"]] = x
        except:
            print "There was an error somewhere in formating the data"
    data["Aggregate"] = aggregate_apps
    data["Totals"] = app_totals

    data = json.dumps(data)
    return data

def query(query, bq):
    return bq.Query(query, DATA_PROJECT_ID)

if __name__=="__main__":
    app.run()
