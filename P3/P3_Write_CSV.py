# -*- coding: utf-8 -*-
"""
Created on Tue Nov 01 16:10:24 2016

@author: Peter Eisenschmidt
"""

#%%

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
import re
import codecs
import csv
import sqlite3
from collections import defaultdict
import phonenumbers

#%% OSM File
OSM_FILE = "Bremen_Germany_Full.osm"


#%%
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

#%% Helper functions

# mapping to replace incorrect streetnames
mapping = {u"Langl\xfctjenstra\xdfe / Burhaver": u"Burhaver Stra\xdfe",
           u"FIXME Eisenacher Straße??" :  "Altenburger Straße"}
           
def update_name(name, mapping):
    """ Update names manually """
    try:
        name = mapping[name]
    except KeyError:
            pass
    
    return name     

def is_phone_number(key):
    """ Check if tag is a phone number """ 
    return (key == "phone")      

def update_phone_number(phone_number):
    """ 
    This functions checks phone numbers and reformats them in the international format. Some phone numbers 
    are corrected manually as it is not possible to correct them automatically (e.g. email adress instead
    of phone number)
    """
    
    # Manual check
    if phone_number == 'vegesack@bremer-baeder.de':
        phone_number = '+49 421 691510'
    
    try:
        # Parse phone number; country code by default is DE for Germany
        x = phonenumbers.parse(phone_number, 'DE')    
        phone_number = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        tmp_num = []
        # check for multiple entries and combine corrected number is in a single list
        for match in phonenumbers.PhoneNumberMatcher(phone_number, "DE"):
            tmp_num.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
        
        # convert list to string and remove list characters. Replace , with ; to separate values
        tmp_num = str(tmp_num).replace('[','')
        tmp_num = str(tmp_num).replace(']','')
        tmp_num = tmp_num.replace("u'","")
        tmp_num = tmp_num.replace("'","")
        tmp_num = str(tmp_num).replace(',',';')
        
        if len(tmp_num) > 0:
            phone_number=str(tmp_num)    
        else:
            try:
                phone_number = re.sub('[^0-9]','', phone_number)
                phone_number = re.sub('^[4]','+4', phone_number)
                x = phonenumbers.parse(phone_number, 'DE')    
                phone_number = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except:
                print phone_number

    return phone_number
    
def shape_element(element):
    """ 
    Reformat element tags and assign them to a dictionary that can be written to csv
    """
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        node_attribs['id'] = element.attrib['id']
        if node_attribs.has_key('user'):
            node_attribs['user'] = element.attrib['user']
            node_attribs['uid'] = element.attrib['uid']
        else:
            node_attribs['user'] = 'NaN'
            node_attribs['uid'] = 9999999999999999
        node_attribs['changeset'] = element.attrib['changeset']
        node_attribs['lat'] = element.attrib['lat']
        node_attribs['lon'] = element.attrib['lon']
        node_attribs['timestamp'] = element.attrib['timestamp']
        node_attribs['version'] = element.attrib['version']

        

        for tag in element.iter('tag'):
            m = PROBLEMCHARS.match(tag.attrib['k'])
            if m:
                pass
            else:
                tmp = {}
                tmp['id'] = element.attrib['id']
                
                if LOWER_COLON.match(tag.attrib['k']):
                    attrib_tmp = tag.attrib['k'].split(':')
                    tmp['type']=attrib_tmp[0]
                    tmp['key'] = tag.attrib['k'].replace(attrib_tmp[0]+':','')
                else:
                    tmp['key'] = tag.attrib['k']
                    tmp['type']='regular'
                tags.append(tmp)
                
                # update phone numbers
                if is_phone_number(tmp['key']):
                    tag.attrib['v'] = update_phone_number(tag.attrib['v'])
                tmp['value'] = update_name(tag.attrib['v'].strip(), mapping)
       
                
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        way_attribs['id'] = element.attrib['id']
        way_attribs['user'] = element.attrib['user']
        way_attribs['uid'] = element.attrib['uid']
        way_attribs['changeset'] = element.attrib['changeset']
        way_attribs['timestamp'] = element.attrib['timestamp']
        way_attribs['version'] = element.attrib['version']
        for tag in element.iter('tag'):
            m = PROBLEMCHARS.match(tag.attrib['k'])
            if m:
                pass
            else:
                tmp = {}
                tmp['id'] = element.attrib['id']
                    
                if LOWER_COLON.match(tag.attrib['k']):
                    attrib_tmp = tag.attrib['k'].split(':')
                    tmp['type']=attrib_tmp[0]
                    tmp['key'] = tag.attrib['k'].replace(attrib_tmp[0]+':','')
                else:
                    tmp['key'] = tag.attrib['k']
                    tmp['type']='regular'

                # update phone numbers
                if is_phone_number(tmp['key']):
                    tag.attrib['v'] = update_phone_number(tag.attrib['v'])
                    
                tmp['value'] = update_name(tag.attrib['v'].strip(), mapping)
                    
                tags.append(tmp)        
        
                
        for i, nd in enumerate(element.iter('nd')):
            nd_tmp = {}
            nd_tmp['id'] = element.attrib['id']
            nd_tmp['node_id']=nd.attrib['ref']
            nd_tmp['position'] = i
            way_nodes.append(nd_tmp)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()    

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)            

            
#%% Parse XML File and write CSV            
    
with codecs.open(NODES_PATH, 'w') as nodes_file, \
     codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
     codecs.open(WAYS_PATH, 'w') as ways_file, \
     codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
     codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:    
        
    nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
    node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
    ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
    way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
    way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

    nodes_writer.writeheader()
    node_tags_writer.writeheader()
    ways_writer.writeheader()
    way_nodes_writer.writeheader()
    way_tags_writer.writeheader()     
    
    street_types = defaultdict(set)

    for element in get_element(OSM_FILE, tags=('node', 'way')):
        el = shape_element(element)
        if el:
            if element.tag == 'node':
                nodes_writer.writerow(el['node'])
                node_tags_writer.writerows(el['node_tags'])
            elif element.tag == 'way':
                ways_writer.writerow(el['way'])
                way_nodes_writer.writerows(el['way_nodes'])
                way_tags_writer.writerows(el['way_tags'])    
    
                
#%% Create database

sqlite_file = 'P3_Bremen.db'                

db = sqlite3.connect(sqlite_file)
cur = db.cursor()

cur.execute('''CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT)
''')

cur.execute('''CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id))
''')

cur.execute('''CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT)
''')

cur.execute('''CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id))
''')

cur.execute('''CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id))
''')

with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['lat'],i['lon'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]

cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
db.commit()

with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db=[(i['id'].decode("utf-8"),i['key'].decode("utf-8"),i['value'].decode("utf-8"),i['type'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
db.commit()    

with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
db.commit()   

with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db=[(i['id'].decode("utf-8"),i['key'].decode("utf-8"),i['value'].decode("utf-8"),i['type'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
db.commit() 

with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db=[(i['id'].decode("utf-8"),i['node_id'].decode("utf-8"),i['position'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)
db.commit()       

db.close()
    