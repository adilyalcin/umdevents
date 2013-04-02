import urllib, json
from threading import Timer
import time
from urllib.request import urlopen
from datetime import datetime
import pymysql

def tStampToDateTime(ts):
    dt = datetime.fromtimestamp(ts)
    return dt

def processWebcalFeed():  
        
    url = 'http://www.cs.umd.edu/webcal/webcal_dept.json'
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    data = (response.read().decode('utf-8'))
    jsonDict = json.loads(data)
    
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
    cur = conn.cursor()   
    
    for item in jsonDict:       
        
        locationName = ''
        locationRoomNumber = ''
        sequence = 0
        summary = ''
        allDay = ''
                                         
        if 'id' in item:
            id = '999'
            id += str(item['id'])
            print("id: %s" % (id)) 
        if 'start' in item:
            ts = item['start']   
            startDateTime = str(tStampToDateTime(ts))
            startDateTime = datetime.strptime(startDateTime, '%Y-%m-%d %H:%M:%S')
            print("startDateTime: %s" % (startDateTime)) 
        if 'allDay' in item:
            allDay = item['allDay']
            print("allDay: %s" % (allDay)) 
        if 'title' in item:
            title = item['title']
            print("title: %s" % (title)) 
        if 'location' in item:
            location = str(item['location'])
            if '.' in location:
                location = location.split('.')
                locationName = location[0]
                locationRoomNumber = location[1]
                print("locationName: %s" % (locationName)) 
                print("locationRoomNumber: %s" % (locationRoomNumber)) 
            else:
                locationName = location
                print("locationName: %s" % (locationName)) 
        if 'summary' in item:
            summary = item['summary']
            print("summary: %s" % (summary)) 
        if 'mod_dt' in item:
            modDt = item['mod_dt']
            modDt = datetime.strptime(modDt, '%Y-%m-%d %H:%M:%S')
            print("modDt: %s" % (modDt))
        if 'sequence' in item:
            sequence = item['sequence']
            print("sequence: %s" % (sequence))
        if 'end' in item:
            endDateTime = item['end']
            endDateTime = str(tStampToDateTime(endDateTime))
            endDateTime = datetime.strptime(endDateTime, '%Y-%m-%d %H:%M:%S')
            print("endDateTime: %s" % (endDateTime))
        
        timeStampNow = str(datetime.now()).split('.')
        timeStampNow = datetime.strptime(timeStampNow[0], '%Y-%m-%d %H:%M:%S')
        print("timeStamp: %s" % (timeStampNow))
        
        events_dictionary_with_webcal_data = {
                                         'id': id,
                                         'title': title,
                                         'startDateTime': startDateTime, 
                                         'endDateTime': endDateTime, 
                                         'locationName': locationName,
                                         'locationRoomNumber': locationRoomNumber, 
                                         'allDay': allDay, 
                                         'summary': summary, 
                                         'modDt': modDt,
                                         'sequence': sequence,
                                         'timeStampNow': timeStampNow          
        }

        try:
            
            cur.execute("SELECT * FROM EVENTS WHERE id = '%(id)s'")
        
            numrows = int(cur.rowcount)
            print('number of rows is ' + numrows)

            if numrows == 0:
                cur.execute("""
                    INSERT INTO EVENTS (id, title, startDateTime, endDateTime, locationName, locationRoomNumber, allDay, summary, modDt, sequence, timeStampNow) 
                    VALUES 
                        (%(id)s, %(title)s, %(startDateTime)s, %(endDateTime)s, %(locationName)s, %(locationRoomNumber)s, %(allDay)s, %(summary)s, %(modDt)s, %(sequence)s, %(timeStampNow)s)
                """, events_dictionary_with_webcal_data)
        except:
            print("Error: Inserting data")     

        conn.commit()

        cur.close()
        conn.close()    
    
        
def scheduleWebcalProcess():
    a = 1
    while a is not -1:
        Timer(5, processWebcalFeed, ()).start()
        time.sleep(21600)  # sleep while time-delay events execute

scheduleWebcalProcess()