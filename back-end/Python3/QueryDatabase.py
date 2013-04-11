#!/usr/bin/env python
import pymysql 
import json
import simplejson
import io
import cgitb #This activates a special exception handler that will display detailed reports in the Web browser if any errors occur.
cgitb.enable() #This activates a special exception handler that will display detailed reports in the Web browser if any errors occur.

# Connect
conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
cursor = conn.cursor ()

# Get the names of all possible locations
cursor.execute("""SELECT DISTINCT locationName from EVENTS""")
locationNames = [item[0] for item in cursor.fetchall()];

# Query the database
query = ('id', 'categories','title', 'description','audience', 'locationName')
cursor.execute('SELECT %s,%s,%s,%s,%s FROM EVENTS WHERE %s = "School of Public Health";' % query)
#cursor.execute("""SELECT * FROM EVENTS""")
rows = cursor.fetchall()

# Get the column names and results in a list
columns = [desc[0] for desc in cursor.description]
result = []
for row in rows:
    d = dict(zip(columns, row))
    result.append(d)

# Get results in json object
retrieved = json.dumps(result, indent=4, separators=(',', ': '))

# Finish up
cursor.close()
conn.close()

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title></title>"
print "</head>"
print "<body>"
print locationNames
print "<br /><br /><br />"
print json.dumps(result, indent=4)
print "</body>"
print "</html>"
