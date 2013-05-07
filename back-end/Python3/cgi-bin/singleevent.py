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

# Connect
conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
cursor = conn.cursor ()

# Construct the query 
outputFields = ('id','facilId', 'title', 'description', 'eventWebsite','startDateTime','endDateTime', 'audience', 'locationName', 'locationRoomNumber', 'categories', 'liked');
queryVariables = outputFields + ('id', param['id'].value);

# Query the database
sql = 'SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM EVENTS WHERE %s = %s'


#cursor.execute(sql1 % (outputFields))
cursor.execute(sql % (queryVariables))
rows = cursor.fetchall()

# Get the column names and results in a list
columns = [desc[0] for desc in cursor.description]
result = []
for row in rows:
    d = dict(zip(columns, row))
    if(d['categories'] is not None):
        d['categories'] = d['categories'].strip(',').split(',');
    # Following four lines are there because UI needs date and time separately
    d['startDate'] = time.strftime("%m/%d/%Y", time.gmtime(time.mktime(d['startDateTime'].timetuple())))
    d['startTime'] = time.strftime("%H:%M:%S", time.gmtime(time.mktime(d['startDateTime'].timetuple())))
    d['endDate'] = time.strftime("%m/%d/%Y", time.gmtime(time.mktime(d['endDateTime'].timetuple())))
    d['endTime'] = time.strftime("%H:%M:%S", time.gmtime(time.mktime(d['endDateTime'].timetuple())))
    result.append(d)

numrows=len(result)
# Get results in json object
retrieved = json.dumps(result[0], cls=MyEncoder, sort_keys=True, encoding="latin-1", ensure_ascii=False)

# Finish up
cursor.close()
conn.close()

print "Content-type:application/json\r\n\r\n"
print retrieved.encode('latin-1','ignore')

