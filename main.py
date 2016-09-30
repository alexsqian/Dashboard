import os
import bqclient
import helpermethods
import webapp2
# import logging
import json
import datetime
import httplib2
import collections
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import CredentialsModel
from oauth2client.appengine import StorageByKeyName
from google.appengine.api import users

from gviz_data_table import encode
from gviz_data_table import Table

# [START cached-decor]
# To Access and query from Bigquery, you need a google account and be authorized by OAuth
# The decorator helps speed that along.
from google.appengine.api import memcache
from google.appengine.ext.webapp.template import render

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
SCOPES = [
    'https://www.googleapis.com/auth/bigquery'
]

decorator = OAuth2Decorator(
    client_id='45926947780-2ferjddc81cb0q11686em4m2089v7s0i.apps.googleusercontent.com',
    client_secret="fAZMuZysMn1vtykElXkAFviL",
    approval_prompt='force',
    scope=SCOPES)



# Necessary variables to access Bigquery. These can all be found on the online dashbaord as well
# The Queries organize the dates by week, sums up the # of installs per week, and gives out the associate data
# Apple query returns week, # of installs during that week, provider (filler space to replace with android), and the app name
# Android query returns week, # of installs during that week, and name of the app
DATA_PROJECT_ID = "45926947780"
DATA_PROJECT_NAME = "asperadashboard"
DATASET = "app_statistics"
APPLE_QUERY = ("SELECT LEFT((format_utc_usec(week)),10) as week, installs, provider, apple_identifier FROM (SELECT week, SUM(units) as installs, provider, apple_identifier FROM (SELECT UTC_USEC_TO_WEEK(PARSE_UTC_USEC(date_for_query), 0) as week, apple_identifier, units, provider, product_type_identifier FROM [asperadashboard:app_statistics.appledata]) WHERE (product_type_identifier LIKE '1%') GROUP BY apple_identifier, week, provider ORDER BY apple_identifier, week)")
APPLE_TOTALS_QUERY = ("SELECT apple_identifier, sum(units) as total_units FROM [asperadashboard:app_statistics.applelifetime] where product_type_identifier CONTAINS '1' group by apple_identifier")
ANDROID_QUERY = ("SELECT LEFT((format_utc_usec(week)),10) as week, installs, package_name, FROM ( SELECT week, SUM(daily_device_installs) as installs, package_name FROM ( SELECT UTC_USEC_TO_WEEK(PARSE_UTC_USEC(date), 0) as week, package_name, daily_device_installs FROM [asperadashboard:app_statistics.androiddata]) GROUP BY week, package_name ORDER BY package_name, week )")
ANDROID_TOTALS_QUERY = ("select t.package_name, t.current_device_installs, t.total_user_installs from [asperadashboard:app_statistics.androiddata] t inner join (select package_name, max(date) as MaxDate from [asperadashboard:app_statistics.androiddata] group by package_name) tm on t.package_name = tm.package_name and t.date = tm.MaxDate")

class MainPage(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        data = {'name', "name"}
        template = os.path.join(os.path.dirname(__file__), 'static/html/index.html')
        self.response.out.write(render(template, data))

class GetData(webapp2.RequestHandler):


    # The ajax script will call post which will be handeled by this post method right here
    def post(self):
        ajaxdata = json.loads(self.request.body)
        data = {}

        # OAuth stuff
        current_user = users.get_current_user()
        credentials = StorageByKeyName(CredentialsModel, current_user.user_id(), 'credentials').get()
        http = credentials.authorize(httplib2.Http())

        #sets up bigquery client and queries for the data
        bq = bqclient.BigQueryClient(decorator, http)
        appledata = self.query(APPLE_QUERY, bq)
        appletotals = self.query(APPLE_TOTALS_QUERY, bq)
        androiddata = self.query(ANDROID_QUERY, bq)
        androidtotals = self.query(ANDROID_TOTALS_QUERY, bq)


        # Recieve the data from the index.html javascript file
        # The data consists of the common name, ios name, and the android name of each app
        # For app name this method is called seperately, so this code is applied to each app name one at a time
        helper = helpermethods.DataFormat()
        aggregate_apps = helper.create_aggregate(appledata, androiddata, ajaxdata)
        app_totals = helper.create_totals(appletotals, androidtotals, ajaxdata)

        print app_totals

        for appinfo in ajaxdata:
            # x is also a dictionary
            x = helper.formatData(appinfo, appledata, androiddata)
            data[appinfo["name"]] = x
        data["Aggregate"] = aggregate_apps
        data["Totals"] = app_totals

        data = json.dumps(data)
        self.response.out.write(data)

    @decorator.oauth_aware
    def query(self, query, bq):
        if decorator.has_credentials():
            return bq.Query(query, DATA_PROJECT_ID)
        else:
            decorator.authorize_url()

#Recieves the requests from html page
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/getdata/', GetData),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)
