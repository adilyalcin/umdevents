#!/usr/bin/env python
import math
import pymysql 
import json
import simplejson
import io
import datetime
import time
import cgi
import cgitb #This activates a special exception handler that will display detailed reports in the Web browser if any errors occur.
cgitb.enable() #This activates a special exception handler that will display detailed reports in the Web browser if any errors occur.

#Note: in buildings table, yCentCoord is latitude and xCentCoord is longitude
def GetCloseFacilIds(currlat, currlong, sqdist_in_km):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
    cursor = conn.cursor ()
    # Get all facilId within the specified euclidean distance
    # x = R cos lat cos long and y = R cos lat sin long
    R = 6371; # radius of earth in kms
    currx = R*math.cos(currlat*0.0174532925)*math.cos(currlong*0.0174532925); # convert the latitude and longitude to degrees
    curry = R*math.cos(currlat*0.0174532925)*math.sin(currlong*0.0174532925);
    cursor.execute('SELECT facilityId from BUILDINGS where (( POW(((6371*COS(yCentCoord*0.0174532925)*COS(xCentCoord*0.0174532925))-%s), 2) + POW(((6371*COS(yCentCoord*0.0174532925)*SIN(xCentCoord*0.0174532925))-%s), 2) )<=%s)' % (currx, curry, sqdist_in_km));
#    cursor.execute('SELECT bldgName, ( POW(((6371*COS(yCentCoord*0.0174532925)*COS(xCentCoord*0.0174532925))-%s), 2) + POW(((6371*COS(yCentCoord*0.0174532925)*SIN(xCentCoord*0.0174532925))-%s), 2) ) as dist from BUILDINGS where (( POW(((6371*COS(yCentCoord*0.0174532925)*COS(xCentCoord*0.0174532925))-%s), 2) + POW(((6371*COS(yCentCoord*0.0174532925)*SIN(xCentCoord*0.0174532925))-%s), 2) )<=%s)' % (currx, curry, currx, curry, sqdist_in_km));
#    cursor.execute('SELECT bldgName, ( POW(((6371*COS(yCentCoord*0.0174532925)*COS(xCentCoord*0.0174532925))-%s), 2) + POW(((6371*COS(yCentCoord*0.0174532925)*SIN(xCentCoord*0.0174532925))-%s), 2) ) AS dist from BUILDINGS where ' % (currx, curry));
    rows = cursor.fetchall();
    columns = [desc[0] for desc in cursor.description]
    result = []
    for row in rows:
        d = dict(zip(columns, row))
        result.append(str(d["facilityId"]))
    cursor.close()
    conn.close()
    return result;

# The following code is to facilitate conversion of time format in json
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
	if isinstance(obj, datetime.datetime):
	    # Time format is Month/Date/Year Hour:minute:sec
	    return time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(time.mktime(obj.timetuple())))
	return json.JSONEncoder.default(self, obj)

# Get the parameters passed to this file
param = cgi.FieldStorage()
paramFieldList = param.keys()
numfields = len(paramFieldList)

# Connect
conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
cursor = conn.cursor ()

# Handle distance feature
additionalFacilIdList = [];
if("distance" in paramFieldList and "facilId" in paramFieldList):
    sqdist_in_km = math.pow((float(param["distance"].value)*0.0003048),2);
    valuelist = (param["facilId"].value).split("-") # Get a list of buildings specified
    for building in valuelist:
	# Get the lat-long for this building
	cursor.execute('SELECT xCentCoord,yCentCoord from BUILDINGS where facilityId = %s' % (building));
	row = cursor.fetchone();
	columns = [desc[0] for desc in cursor.description]
	buildingDetails = dict(zip(columns, row));
	currlat=buildingDetails["yCentCoord"];
	currlong=buildingDetails["xCentCoord"];
	# Get the list of nearby buildings
	additionalFacilIdList.extend(GetCloseFacilIds(currlat, currlong, sqdist_in_km));
	if(building in additionalFacilIdList): # the reference building must have been inserted in this list. Remove it
	    additionalFacilIdList.remove(building);

if("nearme" in paramFieldList and "lat" in paramFieldList and "long" in paramFieldList):
    sqdist_in_km = math.pow((float(param["nearme"].value)*0.0003048),2);
    currlat=float(param["lat"].value);
    currlong=float(param["long"].value);
    # Get the list of nearby buildings
    additionalFacilIdList.extend(GetCloseFacilIds(currlat, currlong, sqdist_in_km));

# Construct the query 
# Field names to be outputted
outputFields = ('id', 'facilId','title', 'description', 'startDateTime','endDateTime', 'audience', 'locationName', 'locationRoomNumber', 'categories', 'liked');
queryVariables = outputFields;
if("categories" in paramFieldList):
    valuelist = (param["categories"].value).split("-") # Get a list of all values
    for val in valuelist:
	val = '\"%,'+val+',%\"';
        queryVariables = queryVariables + ("categories", val);
if("facilId" in paramFieldList):
    valuelist = (param["facilId"].value).split("-") # Get a list of all values
    for val in valuelist:
        queryVariables = queryVariables + ("facilId", val)

# Add the additional buildings list to the query variables
for buildId in additionalFacilIdList:
    queryVariables = queryVariables + ("facilId", buildId);

if("text" in paramFieldList):
    val = param["text"].value.strip();
    queryVariables = queryVariables + (val, val);

# Is there a time query?
if("fromnow" in paramFieldList):
    offset = int(param["fromnow"].value) *3600;
    queryVariables = queryVariables + (offset,offset);
if("begindate" in paramFieldList and "enddate" in paramFieldList):
    val1 = '\"'+param["begindate"].value+'\"';
    val2 = '\"'+param["enddate"].value+'\"';
    queryVariables = queryVariables + (val1,val2);
cursor.execute('set time_zone = \'+00:00\''); ####### For some reason, mysql doesn't return correct current time. This line fixes that

# Query the database
sql = 'SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM EVENTS'
# If atleast one parameter is specified
if(numfields>0):
	sql = sql + ' WHERE '
	sql1 = sql + ' facilId=162 AND audience=\"Public\"'
	
	# Process the options for categories: these have to be matched partially
	if("categories" in paramFieldList):
	    numvals = len((param["categories"].value).split("-")) # Get number of values specified for this field
	    sql = sql + ' ( '
	    for i in range(0,numvals):
		sql = sql + ' %s LIKE %s OR '
	    sql = sql[:-4] # Get rid of last OR
	    sql = sql + ') AND'

	# Process the options for facility Ids: these have to be matched exactly
	if("facilId" in paramFieldList or len(additionalFacilIdList)>0):
	    # Get number of values specified for this field
	    numvals = len(additionalFacilIdList);
	    if("facilId" in paramFieldList):
   	        numvals = numvals + len((param["facilId"].value).split("-"));
	    sql = sql + ' ( '
	    for i in range(0,numvals):
	        sql = sql + ' %s=%s OR '
	    sql = sql[:-4] # Get rid of last OR
	    sql = sql + ') AND'
	
	if("text" in paramFieldList):
	    sql = sql + '( title REGEXP \'[[:<:]]%s[[:>:]]\' = 1 OR description REGEXP \'[[:<:]]%s[[:>:]]\' = 1) AND';

	# Process the options for time
	if("future" in paramFieldList):
	    sql = sql + ' ( UNIX_TIMESTAMP(startDateTime) > UNIX_TIMESTAMP(CURRENT_TIMESTAMP)) AND';
	if("now" in paramFieldList):
	    sql = sql + ' ( UNIX_TIMESTAMP(startDateTime) <= UNIX_TIMESTAMP(CURRENT_TIMESTAMP) AND UNIX_TIMESTAMP(endDateTime) >= UNIX_TIMESTAMP(CURRENT_TIMESTAMP)) AND';
	if("fromnow" in paramFieldList):
	    sql = sql + ' ( UNIX_TIMESTAMP(startDateTime) <= UNIX_TIMESTAMP(CURRENT_TIMESTAMP) + %d AND UNIX_TIMESTAMP(endDateTime) >= UNIX_TIMESTAMP(CURRENT_TIMESTAMP) + %d) AND';
	if("begindate" in paramFieldList and "enddate" in paramFieldList):
	    sql = sql + ' ( UNIX_TIMESTAMP(startDateTime) >= UNIX_TIMESTAMP(%s)  AND UNIX_TIMESTAMP(endDateTime) <= (UNIX_TIMESTAMP(%s)+86400)) AND';
	
	sql = sql[:-4] # Get rid of last AND
	    
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
    #d['categories'] = d['categories'].split(','); 
    # Following four lines are there because UI needs date and time separately
    d['startmilli'] = time.mktime(d['startDateTime'].timetuple()); 
    d['endmilli'] = time.mktime(d['endDateTime'].timetuple()); 
    d['startDate'] = time.strftime("%m/%d/%Y", time.localtime(time.mktime(d['startDateTime'].timetuple())))
    d['startTime'] = time.strftime("%H:%M:%S", time.localtime(time.mktime(d['startDateTime'].timetuple())))
    d['endDate'] = time.strftime("%m/%d/%Y", time.localtime(time.mktime(d['endDateTime'].timetuple())))
    d['endTime'] = time.strftime("%H:%M:%S", time.localtime(time.mktime(d['endDateTime'].timetuple())))
    result.append(d)

numrows=len(result)
# Get results in json object
retrieved = json.dumps(result, cls=MyEncoder, sort_keys=True, encoding="latin-1", ensure_ascii=False)

# Finish up
cursor.close()
conn.close()

print "Content-type:application/json\r\n\r\n"
print retrieved.encode('latin-1','ignore')
'''
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title></title>"
print "</head>"
print "<body>"
print "<br /><br /><br />"
print queryVariables
print "<br /><br /><br />"
print sql
print "<br /><br /><br />"
print numrows
print "<br /><br /><br />"
print retrieved 
print "<br /><br /><br />"
print d['categories']
#print "<br /><br /><br />"
#print sqdist_in_km
print "</body>"
print "</html>"
'''

