# -*- coding: utf-8 -*-
"""
Created on Tue Nov 01 16:10:24 2016

@author: Peter Eisenschmidt
"""

#%%

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
import re
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

#%% OSM File

OSM_FILE = "Bremen_Germany_Full.osm"

#%% Regular expression

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

def shape_element(element):
    
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
                tmp['value'] = tag.attrib['v']
                if LOWER_COLON.match(tag.attrib['k']):
                    attrib_tmp = tag.attrib['k'].split(':')
                    tmp['type']=attrib_tmp[0]
                    tmp['key'] = tag.attrib['k'].replace(attrib_tmp[0]+':','')
                else:
                    tmp['key'] = tag.attrib['k']
                    tmp['type']='regular'
                tags.append(tmp)
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
                tmp['value'] = tag.attrib['v']
                if LOWER_COLON.match(tag.attrib['k']):
                    attrib_tmp = tag.attrib['k'].split(':')
                    tmp['type']=attrib_tmp[0]
                    tmp['key'] = tag.attrib['k'].replace(attrib_tmp[0]+':','')
                else:
                    tmp['key'] = tag.attrib['k']
                    tmp['type']='regular'
                    
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
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
    
def is_phone_number(elem):
    return (elem.attrib['k'] == "phone")

# Check for known street name endings. If the name consists of two or more words, make sure the type of street is capitalized
street_type_re = re.compile(r'(\bStra\xdfe)$|(\Bstra\xdfe)$|(\bWeg)$|(\Bweg)$|(\bKamp)$|(\Bkamp)$|(\bAllee)$|(\Ballee)$|(\bRing)$|(\Bring)$|(\bPlatz)$|(\Bplatz)$')
    
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type].add(street_name)    
    else:
        street_types['others'].add(street_name)

# check phone numbers for any non-digits except white space or plus (+)
phone_number_re = re.compile(r'^\+\d{2}\s[1-9]{1}[ \d]+')
        
def audit_phone_number(phone_num, phone_number):
    m = phone_number_re.search(phone_number)
    if m:
        if m.group() == phone_number:
            phone_num['correct'].add(phone_number)
        else:
            phone_num['incorrect'].add(phone_number)
    else:
        phone_num['incorrect'].add(phone_number)
            
#%% Parse XML File and audit the data          
street_types = defaultdict(set)
phone_num = defaultdict(set)
    
for element in get_element(OSM_FILE, tags=('node', 'way')):
    el = shape_element(element)
    if el:
        if element.tag == 'node':
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_phone_number(tag):
                    audit_phone_number(phone_num, tag.attrib['v'])

        elif element.tag == 'way':
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_phone_number(tag):
                    audit_phone_number(phone_num, tag.attrib['v'])    

#%% Street name statistics
no_str = len(street_types[u'Stra\xdfe']) + len(street_types[u'stra\xdfe'])
no_weg = len(street_types[u'Weg']) + len(street_types[u'weg'])
no_platz = len(street_types[u'Platz']) + len(street_types[u'platz'])
no_kamp = len(street_types[u'Kamp']) + len(street_types[u'kamp'])
no_allee = len(street_types[u'Allee']) + len(street_types[u'allee'])
no_ring = len(street_types[u'Ring']) + len(street_types[u'ring'])
no_other = len(street_types[u'others'])

print "Total number of streets: ", no_str+no_weg+no_platz+no_kamp+no_allee+no_ring+no_other

# Create pie chart with different street types
labels = [u'Stra\xdfe', u'Weg', u'Platz', u'Kamp', u'Allee', u'Ring', u'Other']  
colors =  ['#4286f4', '#30a00e', '#d89338', '#d6d0c9', '#d15140', '#9b4ece',  '#c8ce4e']
plt.figure(1, figsize=(6,6))
plt.pie([no_str, no_weg, no_platz, no_kamp, no_allee, no_ring, no_other], labels=labels, colors = colors,
                autopct='%1.1f%%', shadow=True, startangle=90)

# regex to check for incorrect spellings
street_type_check = re.compile(r'(Stra\xdfe)|(Strasse)|(kamp)|(Allee)|(Platz)|(Ring)|(Weg)',re.IGNORECASE)

# check 'others' category for incorrect spellings
for sname in street_types['others']:
    if street_type_check.search(sname):  
        print sname
    
#%% Phone number statistics

no_correct = len(phone_num['correct'])                
no_incorrect = len(phone_num['incorrect'])

labels = ['Correct', 'Incorrect']
colors = ['#4286f4', '#db4711']
plt.figure(2, figsize=(6,6))
plt.pie([no_correct, no_incorrect], labels=labels, colors = colors,
                autopct='%1.1f%%', shadow=True, startangle=90)

print "Total number of phone numbers:     ", no_incorrect + no_correct
print "Number of incorrect phone numbers: ", no_incorrect
