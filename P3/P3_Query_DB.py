# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 17:30:30 2016

@author: Peter Eisenschmidt
"""

import sqlite3
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#%% Open database

db = sqlite3.connect("P3_Bremen.db")
c = db.cursor()

#%% Database queries

# Number of unique users
Q = '''
SELECT COUNT(*)          
FROM (SELECT uid FROM nodes GROUP BY uid UNION ALL SELECT uid FROM ways GROUP BY uid);
'''
c.execute(Q)
rows = c.fetchall()
no_uid = rows[0][0]
print "Number of unique users: ", no_uid

# Top 10 users
Q = '''
SELECT user, uid, count(uid) 
FROM nodes GROUP BY uid UNION ALL SELECT user, uid, count(uid) FROM ways GROUP BY uid  
ORDER BY count(uid) DESC LIMIT 10;
'''
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)

print df

# Total number of ways
Q = '''
SELECT COUNT(*) FROM ways;
'''
c.execute(Q)
rows = c.fetchall()
no_ways = rows[0][0]
print "Number of ways:         ", no_ways

# Number of nodes
Q = '''
SELECT COUNT(*) FROM nodes;
'''
c.execute(Q)
rows = c.fetchall()
no_nodes = rows[0][0]
print "Number of nodes:        ", no_nodes

# Number of postcodes
q = '''
SELECT count(*)
FROM (SELECT value FROM nodes_tags WHERE key=='postcode' GROUP BY value);
'''
c.execute(q)
rows = c.fetchall()
no_pc = rows[0][0]
print "Number of postcodes:    ", no_pc

#%% Investigate bus stops

# select all nodes
QUERY = "SELECT lat, lon FROM nodes;" 

# select only nodes where the key is public_transport
Q1 = "SELECT nodes.lat, nodes.lon FROM nodes, nodes_tags WHERE nodes_tags.key == 'public_transport' AND nodes.id==nodes_tags.id;"

# select only nodes where the value is bus_stop
Q2 = "SELECT nodes.lat, nodes.lon FROM nodes, nodes_tags WHERE nodes_tags.value == 'bus_stop' AND nodes.id==nodes_tags.id;"

c.execute(QUERY)
rows = c.fetchall()
df = pd.DataFrame(rows)

c.execute(Q1)
rows = c.fetchall()
df1 = pd.DataFrame(rows)

c.execute(Q2)
rows = c.fetchall()
df2 = pd.DataFrame(rows)

# This query extracts the boundary of the federal state. This is used in the map plot later.
q_boundary = '''
SELECT ways_tags.id, nodes.lat, nodes.lon FROM nodes, ways_tags, ways_nodes
WHERE ways_tags.key == 'admin_level' AND ways_tags.value==4
AND ways_tags.id = ways_nodes.id
AND nodes.id == ways_nodes.node_id;
'''

c.execute(q_boundary)
rows = c.fetchall()
df_bd = pd.DataFrame(rows, columns=['id','lat','lon'])

#%% Plot map data and bus stop/public transport nodes

# color map for plot
cmap = matplotlib.cm.get_cmap('afmhot_r')
sns.set(palette="afmhot_r", rc={'axes.facecolor': cmap(.95)})

plt.figure(1, figsize=(20,40))
plt.plot(df[1],df[0],'.', alpha = .2, color = cmap(.4))    # plot map data (all nodes)
plt.plot(df1[1],df1[0],'o', alpha = .2, color = 'red')     # plot public_transport nodes
plt.plot(df2[1],df2[0],'s', alpha = .2, color = '#0b8c18') # plot bus_stop nodes

for i in np.unique(df_bd['id']): # iteration through individual state boundary ways
    df_tmp = df_bd.loc[df_bd['id']== i]
    plt.plot(df_tmp.lon,df_tmp.lat, color='#f2f0c9', linewidth=2.5) # plot state boundaries
plt.ylim([min(df[0]), max(df[0])])
plt.xlim([min(df[1]), max(df[1])])
plt.xlabel('Longitude / deg')
plt.ylabel('Latitude / deg')
plt.show()

#%% Identify number of incorrectly tagged nodes

q1 = '''
SELECT count(*) FROM nodes_tags as a, nodes_tags as b 
WHERE a.id == b.id AND a.key == 'public_transport' 
AND b.value=='bus_stop';
'''
c.execute(q1)
no_bus_stops_pt = c.fetchall()[0][0]

q2 = "SELECT count(*) FROM nodes_tags WHERE nodes_tags.value=='bus_stop';"
c.execute(q2)
no_bus_stops = c.fetchall()[0][0]

print "Number of bus stops:                                ", no_bus_stops
print "Number of bus stops including public_transport tag: ", no_bus_stops_pt
print "Number of bus stops without public_transport tag:   ", no_bus_stops - no_bus_stops_pt