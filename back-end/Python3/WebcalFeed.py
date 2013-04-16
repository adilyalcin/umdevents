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
            facilId = handleFacilId(locationName)
            print("facilId: %s" % (facilId))      
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
                                         'facilId': facilId,
                                         'locationRoomNumber': locationRoomNumber, 
                                         'allDay': allDay, 
                                         'summary': summary, 
                                         'modDt': modDt,
                                         'sequence': sequence,
                                         'timeStampNow': timeStampNow          
        }

        try:    
            cur.execute("""
                INSERT INTO EVENTS (id, title, startDateTime, endDateTime, locationName, facilId, locationRoomNumber, allDay, summary, modDt, sequence, timeStampNow) 
                VALUES 
                    (%(id)s, %(title)s, %(startDateTime)s, %(endDateTime)s, %(locationName)s, %(facilId)s, %(locationRoomNumber)s, %(allDay)s, %(summary)s, %(modDt)s, %(sequence)s, %(timeStampNow)s)
            """, events_dictionary_with_webcal_data)
        except:
            print("Info: Event is already in the database")


    conn.commit()

    cur.close()
    conn.close()    

def handleFacilId(bldgNam):
    if 'energy plant' in bldgNam.lower(): 
        return 1
    elif 'memorial' in bldgNam.lower():
        return 9
    elif 'patuxent' in bldgNam.lower():
        return 10
    elif 'south campus' in bldgNam.lower():
        return 26
    elif 'jimenez' in bldgNam.lower():
        return 34
    elif 'mckeldin' in bldgNam.lower():
        return 35
    elif 'plant sciences' in bldgNam.lower():
        return 36
    elif 'shoemaker' in bldgNam.lower():
        return 37
    elif 'van munching' in bldgNam.lower():
        return 39
    elif 'skinner' in bldgNam.lower():
        return 44
    elif 'marie mount' in bldgNam.lower():
        return 46
    elif 'woods' in bldgNam.lower():
        return 47
    elif 'francis' in bldgNam.lower():
        return 48
    elif 'mitchell' in bldgNam.lower():
        return 52
    elif 'eppley' in bldgNam.lower():
        return 68
    elif 'math' in bldgNam.lower():
        return 82
    elif 'physics building' in bldgNam.lower():
        return 84
    elif 'martin' in bldgNam.lower():
        return 88
    elif 'engineering laboratory' in bldgNam.lower():
        return 89
    elif 'chemistry' in bldgNam.lower():
        return 91
    elif 'williams' in bldgNam.lower():
        return 115
    elif 'health center' in bldgNam.lower():
        return 140
    elif 'tawes' in bldgNam.lower():
        return 141
    elif 'art-sociology' in bldgNam.lower():
        return 146
    elif 'hornbake' in bldgNam.lower():
        return 147
    elif 'arboretum' in bldgNam.lower():
        return 156
    elif 'cole' in bldgNam.lower():
        return 162
    elif 'stamp' in bldgNam.lower():
        return 163
    elif 'computer & space' in bldgNam.lower():
        return 224
    elif 'kim' in bldgNam.lower():
        return 225
    elif 'jull' in bldgNam.lower():
        return 227
    elif 'nyumburu' in bldgNam.lower():
        return 232
    elif 'public health' in bldgNam.lower():
        return 255
    elif 'north' in bldgNam.lower():
        return 295
    elif 'young children' in bldgNam.lower():
        return 381
    elif 'clarice' in bldgNam.lower():
        return 386
    elif 'computer science instructional' in bldgNam.lower():
        return 406
    elif 'csic' in bldgNam.lower():
        return 406
    elif 'riggs' in bldgNam.lower():
        return 407
    elif 'knight' in bldgNam.lower():
        return 417
    elif 'research park building' in bldgNam.lower():
        return 807
    else:
        return 19191919
        
def scheduleWebcalProcess():
    a = 1
    while a is not -1:
        Timer(5, processWebcalFeed, ()).start()
        time.sleep(86400)  # sleep while time-delay events execute

scheduleWebcalProcess()