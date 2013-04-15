import pymysql 
import json
import simplejson
import io

# For converting date time to a nice format
def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis

# Connect
conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
cursor = conn.cursor ()

# Query the database
query = ('id', 'locationName')
cursor.execute('SELECT %s,%s FROM EVENTS;' % query)
#cursor.execute("""SELECT * FROM EVENTS""")
rows = cursor.fetchall()

# Get the column names and results in a list
columns = [desc[0] for desc in cursor.description]
result = []
for row in rows:
    d = dict(zip(columns, row))
    result.append(d)

# Get results in json object
retrieved = json.dumps(result, indent=4)
print retrieved

# Write to file
#with open('../../json/events.json', 'w') as f:
#   json.dump(result, f, indent=4, default=default) 
  #f.write(unicode(json.dumps(retrieved, ensure_ascii=False)))
#f.close()

# Finish up
cursor.close()
conn.close()
print "done"
