from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3 as sql
import numpy as np
# import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import math
import itertools
import time

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/createtable', methods=['POST'])
def createtable():
    try:
        connection = sql.connect('database.db')
        # connection.execute('CREATE TABLE "TITANIC" ("PCLASS" INTEGER, "SURVIVED" INTEGER, "NAME" TEXT, "SEX" TEXT, "AGE" NUMERIC, "SIBSP" INTEGER, "PARCH" INTEGER, "TICKET" TEXT, "FARE" REAL, "CABIN" TEXT, "EMBARKED" TEXT, "BOAT" TEXT, "BODY" INTEGER, "HOME.DEST" TEXT)')

        connection.execute('CREATE TABLE "MINNOW" ( "CABINNUM" INTEGER, "FNAME" TEXT, "LNAME" TEXT, "AGE" NUMERIC, "SURVIVED" TEXT, "LAT" REAL, "LONG" REAL, "PICTURECAP" BLOB, "PICTUREPAS" BLOB, "FARE" REAL )')

        connection.close()
        print('Table created')
    except:
        print('some error in table creation')

    # try:
    #     connection = sql.connect('database.db')
    #     try:
    #         df = pandas.read('C://Users//abhis//Desktop//titanic3.csv')
    #     except:
    #         print("oops")
    #     df.to_sql("TITANIC", connection, if_exists='append', index=False)
    #     print('Data inserted')
    # except:
    #     print('insertion error')
        connection.close()
    return render_template('index.html')

@app.route('/kmeans',methods=['POST','GET'])
def kmeans():
    no_of_cluster = request.form['no_of_cluster']
    connection = sql.connect('database.db')
    connection.row_factory = sql.Row
    cur = connection.cursor()
    query = "select * from titanic"
    cur.execute(query)
    rows = cur.fetchall()
    pclass = []
    boat = []
    survival = []
    age = []
    fare = []
    for row in rows:
        pclass.append(row["PCLASS"])
        survival.append(row["SURVIVED"])
        if row["BOAT"] == '':
            boat.append(0)
        else:
            boat.append(row["BOAT"])
        if row["AGE"] == '':
            age.append(0)
        else:
            age.append(row["AGE"])
        if row["FARE"] == '':
            fare.append(0)
        else:
            fare.append(row["FARE"])
    connection.close()
    # print('\nPCLASS --------',pclass)
    # print('\nsurvival --------',survival)
    # print('\nage --------',age)

    X = np.array(list(zip(age[:len(age)-1], fare[:len(fare)-1])))
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
    displaylist = list(zip(age,fare,labels))
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
