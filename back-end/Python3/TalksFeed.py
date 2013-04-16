import urllib, json
from html.parser import HTMLParser
from threading import Timer
import time
from urllib.request import urlopen
from datetime import datetime
import pymysql

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def processTalksFeed():
    
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
    cur = conn.cursor()
            
    url = 'https://talks.cs.umd.edu/talks.json'
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    data = (response.read().decode('utf-8'))
    jsonDict = json.loads(data)
        
    for item in jsonDict:
        id = '777'
        id += str(item['talk']['id'])
        print("id: %s" % (id))
        speaker = item['talk']['speaker']
        print("speaker: %s" % (speaker))
        speakerAffiliation = item['talk']['speaker_affiliation']
        print("speakerAffiliation: %s" % (speakerAffiliation))
        speakerUrl = item['talk']['speaker_url']
        print("speakerUrl: %s" % (speakerUrl))
        dtSt = str(item['talk']['start_time']).split('T')
        dtSta = dtSt[1].split('-')
        dtStart = dtSta[0]
        startDateTime = dtSt[0] + ' ' + dtStart
        startDateTime = datetime.strptime(startDateTime, '%Y-%m-%d %H:%M:%S')
        print("startDateTime: %s" % (startDateTime))
        dtE = str(item['talk']['end_time']).split('T')
        dtEn = dtE[1].split('-')
        dtEnd= dtEn[0]
        endDateTime = dtE[0] + ' ' + dtEnd
        endDateTime = datetime.strptime(endDateTime, '%Y-%m-%d %H:%M:%S')
        print("endDateTime: %s" % (endDateTime))
        abstr = item['talk']['abstract']
        abstract = strip_tags(abstr)
        abstract = abstract.rstrip()
        print("abstract: %s" % (abstract))
        biog = item['talk']['bio']
        bio = strip_tags(biog)
        bio = bio.rstrip()
        print("bio: %s" % (bio))
        locationRoomNumber = item['talk']['room']
        print("locationRoomNumber: %s" % (locationRoomNumber))
        eventWebsite = item['talk']['url']
        print("eventWebsite: %s" % (eventWebsite))
        title = item['talk']['title']
        print("title: %s" % (title))
        locationName = item['talk']['building']
        print("locationName: %s" % (locationName))
        facilId = handleFacilId(locationName)
        print("facilId: %s" % (facilId))        
        buildingAbbreviation = item['talk']['building_abbrv']
        print("buildingAbbreviation: %s" % (buildingAbbreviation))
        buildingUrl = item['talk']['building_url']
        print("buildingUrl: %s" % (buildingUrl))
        categories = str(7)
        print("categories: %s" % (categories))
        
        timeStampNow = str(datetime.now()).split('.')
        timeStampNow = datetime.strptime(timeStampNow[0], '%Y-%m-%d %H:%M:%S')
        print("timeStamp: %s" % (timeStampNow))
        
        events_dictionary_with_talks_data = {
                                         'id': id,
                                         'title': title,
                                         'startDateTime': startDateTime,
                                         'endDateTime': endDateTime,
                                         'speaker': speaker,
                                         'speakerAffiliation': speakerAffiliation,
                                         'speakerUrl': speakerUrl,
                                         'abstract': abstract,
                                         'bio': bio,
                                         'categories': categories,
                                         'locationName': locationName,
                                         'facilId': facilId,
                                         'locationRoomNumber': locationRoomNumber,
                                         'buildingAbbreviation': buildingAbbreviation,
                                         'buildingUrl': buildingUrl,
                                         'eventWebsite': eventWebsite,
                                         'timeStampNow': timeStampNow
        }

        try:
            cur.execute("""
                INSERT INTO EVENTS (id, title, startDateTime, endDateTime, speaker, speakerAffiliation, speakerUrl, abstract, bio, categories, locationName, facilId, locationRoomNumber, buildingAbbreviation, buildingUrl, eventWebsite, timeStampNow)
                VALUES
                    (%(id)s, %(title)s, %(startDateTime)s, %(endDateTime)s, %(speaker)s, %(speakerAffiliation)s, %(speakerUrl)s, %(abstract)s, %(bio)s, %(categories)s, %(locationName)s, %(facilId)s, %(locationRoomNumber)s, %(buildingAbbreviation)s, %(buildingUrl)s, %(eventWebsite)s, %(timeStampNow)s)
            """, events_dictionary_with_talks_data)

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
        
def scheduleTalksProcess():
    a = 1
    while a is not -1:
        Timer(5, processTalksFeed, ()).start()
        time.sleep(86400) # sleep while time-delay events execute

scheduleTalksProcess()