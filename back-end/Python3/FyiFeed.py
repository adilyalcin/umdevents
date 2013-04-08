from xml.dom.minidom import parseString, Node
import re
from threading import Timer
import time
#from urllib.request import urlopen # For python 3
import urllib # For python 2.7
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
                                         'locationRoomNumber': locationRoomNumber, 
                                         'categories': categories, 
                                         'eventWebsite': eventWebsite, 
                                         'announcementDate': announcementDate,
                                         'timeStampNow': timeStampNow          
        }

        try:
            cur.execute("""
                INSERT INTO EVENTS (id, title, description, startDateTime, endDateTime, audience, locationName, locationRoomNumber, categories, eventWebsite, announcementDate, timeStampNow) 
                VALUES 
                    (%(id)s, %(title)s, %(description)s, %(startDateTime)s, %(endDateTime)s, %(audience)s, %(locationName)s, %(locationRoomNumber)s, %(categories)s, %(eventWebsite)s, %(announcementDate)s, %(timeStampNow)s)
            """, events_dictionary_with_fyi_data)

        except:
            print("Error: Inserting data")
            
        conn.commit()

        cur.close()
        conn.close()          

    def handleCategories(self, node):
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName == 'category':
                category = self.gettext([node])
        print("category: %s" % (category))

def processFyiFeed():
    file = urllib.urlopen('http://www.umd.edu/fyi/eventFeed/') # For python 2.7
    #file = urlopen('http://www.umd.edu/fyi/eventFeed/') # For python 3
    data = file.read()
    file.close()
    doc = parseString(data)
    SampleScanner(doc) 
        
def scheduleFyiProcess():
    a = 1
    while a is not -1:
        Timer(5, processFyiFeed, ()).start()
        time.sleep(21600)  # sleep while time-delay events execute

scheduleFyiProcess()
