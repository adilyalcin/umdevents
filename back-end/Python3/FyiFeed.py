from xml.dom.minidom import parseString, Node
import re
from threading import Timer
import time
from urllib.request import urlopen
from datetime import datetime
import pymysql 

class SampleScanner:
    def __init__(self, doc):
        for child in doc.childNodes:
            if child.nodeType == Node.ELEMENT_NODE and child.tagName == 'fyi':
                self.handleFyi(child)

    def gettext(self, nodelist):
        retlist = []
        for node in nodelist:
            if node.nodeType == Node.TEXT_NODE or node.nodeType == Node.CDATA_SECTION_NODE:
                retlist.append(node.wholeText)
            elif node.hasChildNodes:
                retlist.append(self.gettext(node.childNodes))

        return re.sub('\s+', ' ', ''.join(retlist))

    def handleFyi(self, node):
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName == 'event':
                self.handleEvent(child)

    def handleEvent(self, node):
        if node.nodeType == Node.ELEMENT_NODE: 
                self.handleElem(node)
                
    def handleElem(self, node):
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='umdevents', passwd='umdevents', db='UMDEVENTS')
        cur = conn.cursor()        
        
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName == 'id':
                id = self.gettext([child])
                print("id: %s" % (id))              
            if child.tagName == 'title':
                title = self.gettext([child])
                print("title: %s" % (title))
            if child.tagName == 'description':
                description = self.gettext([child])
                print("description: %s" % (description))
            if child.tagName == 'startDateTime':
                startDateTime = self.gettext([child])
                startDateTime = startDateTime.replace('/', '-')
                startDateTime = datetime.strptime(startDateTime, '%m-%d-%Y %H:%M:%S')
                print("startDateTime: %s" % (startDateTime))                    
            if child.tagName == 'endDateTime':
                endDateTime = self.gettext([child])
                endDateTime = endDateTime.replace('/', '-')
                endDateTime = datetime.strptime(endDateTime, '%m-%d-%Y %H:%M:%S')
                print("endDateTime: %s" % (endDateTime))                         
            if child.tagName == 'audience':
                audience = self.gettext([child])
                print("audience: %s" % (audience))               
            if child.tagName == 'locationName':
                locationName = self.gettext([child])
                print("locationName: %s" % (locationName))           
                facilId = self.handleFacilId(locationName)
                print("facilId: %s" % (facilId))  
            if child.tagName == 'locationRoomNumber':
                locationRoomNumber = self.gettext([child])
                print("locationRoomNumber: %s" % (locationRoomNumber))                
            if child.tagName == 'categories':
                categories = self.handleCategories(child)
                print("categories: %s" % (categories)) 
            if child.tagName == 'eventWebsite':
                eventWebsite = self.gettext([child])
                print("eventWebsite: %s" % (eventWebsite))  
            if child.tagName == 'announcementDate':
                announcementDate = self.gettext([child])
                announcementDate = announcementDate.replace('/', '-')   
                print("announcementDate: %s" % (announcementDate))
                
        timeStampNow = str(datetime.now()).split('.')
        timeStampNow = datetime.strptime(timeStampNow[0], '%Y-%m-%d %H:%M:%S')
        print("timeStamp: %s" % (timeStampNow))
        
        events_dictionary_with_fyi_data = {
                                         'id': id,
                                         'title': title,
                                         'description': description, 
                                         'startDateTime': startDateTime, 
                                         'endDateTime': endDateTime, 
                                         'audience': audience,
                                         'locationName': locationName,
                                         'facilId': facilId,
                                         'locationRoomNumber': locationRoomNumber, 
                                         'categories': categories, 
                                         'eventWebsite': eventWebsite, 
                                         'announcementDate': announcementDate,
                                         'timeStampNow': timeStampNow          
        }

        try:
            cur.execute("""
                INSERT INTO EVENTS (id, title, description, startDateTime, endDateTime, audience, locationName, facilId, locationRoomNumber, categories, eventWebsite, announcementDate, timeStampNow) 
                VALUES 
                    (%(id)s, %(title)s, %(description)s, %(startDateTime)s, %(endDateTime)s, %(audience)s, %(locationName)s, %(facilId)s, %(locationRoomNumber)s, %(categories)s, %(eventWebsite)s, %(announcementDate)s, %(timeStampNow)s)
            """, events_dictionary_with_fyi_data)

        except:
            print("Info: Event is already in the database")
            
        conn.commit()

        cur.close()
        conn.close()          

    def handleCategories(self, node):
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName == 'category':
                category =  self.gettext([node])
#                print("category: %s" % (category)) 
                categId = self.handleCategId(category)
                categId = str(categId)
#                print("categId: %s" % (categId))  
        return categId.lstrip(' ')
    
    def handleFacilId(self, bldgNam):
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
        elif 'riggs' in bldgNam.lower():
            return 407
        elif 'knight' in bldgNam.lower():
            return 417
        elif 'research park building' in bldgNam.lower():
            return 807
        else:
            return 19191919
        
    def handleCategId(self, categNam):
        if 'other' in categNam.lower(): 
            return 1
        elif 'art' in categNam.lower():
            return 2
        elif 'athletics' in categNam.lower():
            return 3
        elif 'colloquium' in categNam.lower():
            return 4
        elif 'community' in categNam.lower():
            return 5
        elif 'concert' in categNam.lower():
            return 6
        elif 'conference' in categNam.lower():
            return 7
        elif 'dance' in categNam.lower():
            return 8
        elif 'performance' in categNam.lower():
            return 9
        elif 'diversity' in categNam.lower():
            return 10
        elif 'forum' in categNam.lower():
            return 11
        elif 'health' in categNam.lower():
            return 12
        elif 'lecture' in categNam.lower():
            return 13
        elif 'training' in categNam.lower():
            return 14
        elif 'mce' in categNam.lower():
            return 15
        elif 'meeting' in categNam.lower():
            return 16
        elif 'movie' in categNam.lower():
            return 17
        elif 'recreation' in categNam.lower():
            return 18
        elif 'seminar' in categNam.lower():
            return 19
        elif 'special' in categNam.lower():
            return 20
        elif 'theatre' in categNam.lower():
            return 21                     
        else:
            return 29292929

def processFyiFeed():
    file = urlopen('http://www.umd.edu/fyi/eventFeed/')
    data = file.read()
    file.close()
    doc = parseString(data)
    SampleScanner(doc) 
        
def scheduleFyiProcess():
    a = 1
    while a is not -1:
        Timer(5, processFyiFeed, ()).start()
        time.sleep(86400)  # sleep while time-delay events execute

scheduleFyiProcess()
