from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3 as sql
import numpy as np
# import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import csv
import math
import itertools
import time
import pyodbc

server = 'abhisheksql.database.windows.net'
database = 'database'
username = 'abhishek'
password = 'Sql#2018'
driver= '{ODBC Driver 13 for SQL Server}'
connection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = connection.cursor()

@app.route('/bulkinsert',  methods=['POST','GET'])
def bulkinsert():
    query = "INSERT INTO dbo.EARTHQUAKE (TIME,LATITUDE,LONGITUDE,DEPTH,MAG,MAGTYPE,NST,GAP,DMIN,RMS,NET,ID,UPDATED,PLACE,TYPE,HORIZONTALERROR,DEPTHERROR,MAGERROR,MAGNST,STATUS,LOCATIONSOURCE,MAGSOURCE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    with open('all_month.csv',newline='') as csvfile:
          next(csvfile)
          reader = csv.reader(csvfile, delimiter=',')
          print(reader)
          for row in reader:
              print('\nrow :',row)
              cursor.execute(query,row)

          connection.commit()
    return render_template('index.html')


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/magcase',methods=['POST','GET'])
def magcase():
    starttime = time.time()
    ip1 = request.form['ip1']
    ip2 = request.form['ip2']
    ip3 = request.form['ip3']

    ip1 = round(float(ip1),1)
    ip2 = round(float(ip2),1)
    ip3 = round(float(ip3),1)
    casestr = ""
    i = ip1
    while i<ip2:
        casestr = casestr+"when MAG between "+str(i)+" and "+str(i+ip3)+" then '"+str(i)+" and "+str(i+ip3)+"' \n"
        i = i+ip3

    print(casestr)

    query = "SELECT CASE "+casestr+" END AS MAG1,COUNT(*) AS A from all_month WHERE MAG>="+str(ip1)+" and MAG<="+str(ip2)+" GROUP BY case "+casestr+" END;"
    cursor.execute(query)
    rows=cursor.fetchall()

    data = []
    for i in rows:
        data.append({'MAG1':i[0],'COUNT':i[1]})
    print(data)
    endtime = time.time()
    totaltime = endtime - starttime
    return render_template('tp.html',data=data)


@app.route('/kmeans',methods=['POST','GET'])
def kmeans():
    no_of_cluster = request.form['ip1']
    query = "select latitude, longitude from all_month"
    cursor.execute(query)
    rows = cursor.fetchall()

    x_ip = []
    y_ip = []
    # pclass = []
    # boat = []
    # survival = []
    # age = []
    # fare = []
    for row in rows:
        x_ip.append(row[0])
        y_ip.append(row[1])
    
    # print('\nPCLASS --------',pclass)
    # print('\nsurvival --------',survival)
    # print('\nage --------',age)

    X = np.array(list(zip(x_ip[:len(x_ip)], y_ip[:len(y_ip)])))
    print('\n\n X -------------------------------------',X)

    km = KMeans(n_clusters=int(no_of_cluster))
    km.fit(X)
    centroids = km.cluster_centers_
    labels = km.labels_
    print(centroids)
    print(labels)
    # colors = ["g.","r.","b.","y." "c.", "m.", "k.", "w."]

    # for i in range(len(X)):
    #     plt.plot(X[i][0], X[i][1], colors[labels[i]], markersize = 10)
    # plt.scatter(centroids[:,0],centroids[:,1],marker = "x", s = 150, linewidths=5, zorder = 10)
    displaylist = list(zip(x_ip,y_ip,labels))
    # print('\n\nDisplay List------------------------------------', displaylist)
    dist_list = []
    for i in range(0,len(centroids)-1):
        for j in range(i+1,len(centroids)):
            # print(centroids[i],centroids[j])
            x1 = centroids[i][0]
            x2 = centroids[j][0]
            y1 = centroids[i][1]
            y2 = centroids[j][1]
            temp = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
            dist = math.sqrt(temp)
            print(dist)
            dist_list.append(list(zip(centroids[i][:], centroids[j][:], itertools.repeat(dist))))

    print(dist_list)
    dist_len = len(dist_list)


    #   Storing in dict as (key)label: (value)all x,y's of that label
    label_n_values = {i: X[np.where(labels == i)] for i in range(km.n_clusters)}
    print(label_n_values)
    length_label = len(label_n_values)      #    same as No of clusters
    len_values = []                         #   count of all values of single single label's
    # eg:len_values = [[32],[10],[4],[70]]    ...i.e lengths of 4 labels

    for i in range(len(label_n_values)):
       len_values.append(len(label_n_values[i]))
    # plt.show()

    return render_template('clustering.html', allrows = displaylist, distances = dist_list, dist_length=dist_len, length_label = length_label, len_values = len_values, label_n_values = label_n_values)

if __name__ == '__main__':
   app.run(debug = True)
