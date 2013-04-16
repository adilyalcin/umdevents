#!/usr/bin/env python
import pymysql 
import json
import simplejson
import io
import datetime
import time
import cgi
import cgitb #This activates a special exception handler that will display detailed reports in the Web browser if any errors occur.
cgitb.enable() #This activates a special exception handler that will display detailed reports in the Web browser if any errors occur.

# The following code is to facilitate conversion of time format in json
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
	if isinstance(obj, datetime.datetime):
	    # Time format is Month/Date/Year Hour:minute:sec
	    return time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(time.mktime(obj.timetuple())))
	return json.JSONEncoder.default(self, obj)

# Get the parameters passed to this file
param = cgi.FieldStorage()
paramFieldList = param.keys()
numfields = len(paramFieldList)

# Connect
conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
cursor = conn.cursor ()

# Construct the query 
# Field names to be outputted
outputFields = ('id', 'title', 'description', 'startDateTime','endDateTime', 'audience', 'locationName', 'locationRoomNumber', 'categories', 'liked');
queryVariables = outputFields
for field in paramFieldList:
    valuelist = (param[field].value).split("-") # Get a list of all values
    for val in valuelist:
	val = '\"'+val+'\"'
        queryVariables = queryVariables + (field, val)

# Query the database
sql = 'SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM EVENTS'
# If atleast one parameter is specified
if(numfields>0):
	sql = sql + ' WHERE '
	#sql1 = sql + ' facilId=162 AND audience=\"Public\"'
	
	# Process the options for facilty id and categories: these have to be matched exactly
	facilityCategory =[]
	if("facilId" in paramFieldList):
	    facilityCategory.append("facilId")
	if("categories" in paramFieldList):
	    facilityCategory.append("categories")
	for field in facilityCategory:
	    numvals = len((param[field].value).split("-")) # Get number of values specified for this field
	    sql = sql + ' ( '
	    for i in range(0,numvals):
		sql = sql + ' %s=%s OR '
	    sql = sql[:-4] # Get rid of last OR
	    sql = sql + ') AND '
	sql = sql[:-5] # Get rid of last AND

#cursor.execute(sql1 % (outputFields))
cursor.execute(sql % (queryVariables))
rows = cursor.fetchall()

# Get the column names and results in a list
columns = [desc[0] for desc in cursor.description]
result = []
for row in rows:
    d = dict(zip(columns, row))
    # Following four lines are there because UI needs date and time separately
    d['startDate'] = time.strftime("%m/%d/%Y", time.gmtime(time.mktime(d['startDateTime'].timetuple())))
    d['startTime'] = time.strftime("%H:%M:%S", time.gmtime(time.mktime(d['startDateTime'].timetuple())))
    d['endDate'] = time.strftime("%m/%d/%Y", time.gmtime(time.mktime(d['endDateTime'].timetuple())))
    d['endTime'] = time.strftime("%H:%M:%S", time.gmtime(time.mktime(d['endDateTime'].timetuple())))
    result.append(d)

numrows=len(result)
# Get results in json object
#retrieved = json.dumps(result, cls=MyEncoder, sort_keys=True, encoding="utf-8", ensure_ascii=False)

# Finish up
cursor.close()
conn.close()

# Write to a file
with open('/home/snigdha/Documents/Classes/ContextClass/ClassProject/umdevents/json/events.json','wt') as outfile:
    json.dump(result, outfile, cls=MyEncoder, sort_keys=True, indent=4, encoding="utf-8", ensure_ascii=False)

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title></title>"
print "</head>"
print "<body>"
print paramFieldList
print "<br /><br /><br />"
print queryVariables
print "<br /><br /><br />"
print sql
print "<br /><br /><br />"
print numrows
print "</body>"
print "</html>"
