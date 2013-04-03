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
        buildingAbbreviation = item['talk']['building_abbrv']
        print("buildingAbbreviation: %s" % (buildingAbbreviation))
        buildingUrl = item['talk']['building_url']
        print("buildingUrl: %s" % (buildingUrl))
        
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
                                         'locationName': locationName,
                                         'locationRoomNumber': locationRoomNumber,
                                         'buildingAbbreviation': buildingAbbreviation,
                                         'buildingUrl': buildingUrl,
                                         'eventWebsite': eventWebsite,
                                         'timeStampNow': timeStampNow
        }

        try:
            cur.execute("""
                INSERT INTO EVENTS (id, title, startDateTime, endDateTime, speaker, speakerAffiliation, speakerUrl, abstract, bio, locationName, locationRoomNumber, buildingAbbreviation, buildingUrl, eventWebsite, timeStampNow)
                VALUES
                    (%(id)s, %(title)s, %(startDateTime)s, %(endDateTime)s, %(speaker)s, %(speakerAffiliation)s, %(speakerUrl)s, %(abstract)s, %(bio)s, %(locationName)s, %(locationRoomNumber)s, %(buildingAbbreviation)s, %(buildingUrl)s, %(eventWebsite)s, %(timeStampNow)s)
            """, events_dictionary_with_talks_data)

        except:
            print("Error: Inserting data")
        
    conn.commit()  
            
    cur.close()
    conn.close()
        
def scheduleTalksProcess():
    a = 1
    while a is not -1:
        Timer(5, processTalksFeed, ()).start()
        time.sleep(21600) # sleep while time-delay events execute

scheduleTalksProcess()