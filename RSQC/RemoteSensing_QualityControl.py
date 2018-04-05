# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RSQC
                                 A QGIS plugin
 Quality Control for Remote Sensing
                              -------------------
        begin                : 2017-10-09
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Mark Falkenberg & Andrew Flatman/ SDFE.dk
        email                : mafal@sdfe.dk & anfla@sdfe.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import *
from datetime import datetime
from osgeo import gdal
import re, os, sys, hashlib, getopt
import psycopg2
import gdalhist
import FindUSBname
import subprocess
import socket
import win32api
import math
import glob
# plugin_path = os.path.dirname(os.path.realpath(__file__))
#sys.path.insert(0, plugin_path+'/subscripts')
from subscripts import SubScripts

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from RemoteSensing_QualityControl_dialog import RSQCDialog, RSQCDialogII
import os.path

class WorkThread1(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        # define variables from settings file
        self.ProjectLog, self.MainLog, self.PPC_GSD, self.Sun, self.Tilt, self.CamCal, self.ImageDir, self.DBImageDir, self.DBname, self.DBhost, self.DBport, self.DBuser, self.DBpass, self.DBschema, self.DBtable, self.DB_footprint, self.DB_ppc = self.readSettings2
        self.killed = False
    def __del__(self):
        self.wait()

    @property
    def readSettings2(self):
        settingsFile = os.path.dirname(__file__) + "\\settings.txt"
        ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir = SubScripts.readsettings(settingsFile)
        return (ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir)


    def run(self):
        liste = []
        conn = psycopg2.connect("dbname=" + self.DBname + " user=" + self.DBuser + " host=" + self.DBhost + " password=" + self.DBpass)
        cur = conn.cursor()
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (self.DBtable,))
        if cur.fetchone()[0]:
            dbkald = "SELECT DISTINCT disc_name FROM " + str(self.DBschema) + "." + str(self.DBtable) + " ORDER BY \"disc_name\" DESC"
            cur.execute(dbkald)
            ccdb_svar = cur.fetchall()
            res = list(sorted(ccdb_svar, reverse=True))
            for x in range(0, len(res)):
                liste.append(str(res[x][0]))
        else:
            pass

        dirpath,nextdiskindex = SubScripts.readtxt1()
        patternname = re.compile("[0-9]{4}_[0-9]{3}[A-Z]{1}")
        if nextdiskindex in liste:
            self.emit(QtCore.SIGNAL("update2(QString)"), "Index already in use!. Pick another")
        elif patternname.match(nextdiskindex):
            pass
        else:
            self.emit(QtCore.SIGNAL("update2(QString)"), "Error in Index name: " + nextdiskindex + "\nShould be in the format [year]_[three digget number][Capital A,B or C] Ex:\"2017_001A\"")

        driveletter = dirpath[0:1]
        with open(os.path.dirname(__file__) + "\\" + "tempScript" + ".bat", "a") as bat_file:
            bat_file.write(
                "REM @ECHO OFF\n" + "Title=DiskIndexLabel\n\n" +
                "LABEL " + driveletter + ": " + nextdiskindex + "\n" + "DEL " + "\"" + os.path.dirname(__file__) + "\\tempScript" + ".bat" + "\"")

        os.system(os.path.dirname(__file__) + "\\tempScript" + ".bat")

        conn = psycopg2.connect("dbname=" + self.DBname + " user=" + self.DBuser + " host=" + self.DBhost + " password=" + self.DBpass)
        cur = conn.cursor()
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (self.DBtable,))
        if cur.fetchone()[0]:
            pass
            #QMessageBox.information(None, "General Information", "Database found, continue")
        else:
            QMessageBox.information(None, "General Information", "Database not found, exiting!")

        # ----find last index id
        string1 = "select index_key from " + str(self.DBschema) + "." + str(self.DBtable) + " ORDER BY \"index_key\" DESC"
        cur.execute(string1)
        rows = cur.fetchone()

        if not rows:
            rows = '0'
        last_index_key = int(rows[0])
        # -------------------------

        patternImageIDGeoDK = re.compile("\w{0,1}[0-9]{4}_[0-9]{2}_[0-9]{2}_\d+_[0-9]{4}")
        patternImageIDoblique = re.compile("[0-9]{4}_[0-9]{2}_[0-9]{2}_\d+_[0-9]{4}_[0-9]{8}")
        if last_index_key == 0:
            n = 0
        else:
            n = last_index_key

        pgrnum = 0
        pgrcount = 0
        killed = 'False'


        for root, dirs, files in os.walk(dirpath, topdown=True):
            for name in files:
                pgrnum += 1
        for root, dirs, files in os.walk(dirpath, topdown=True):
            for name in files:
                try:
                    killed = SubScripts.readtxt4()
                    if killed == 'True':
                        break
                except:
                    pass
                try:
                    pgrcount += 1
                    datecreated = ''
                    timecreated = ''
                    size = ''
                    id = ''
                    format = ''
                    upload = ''
                    rollback = ''
                    n += 1
                    index_key = n

                    # print(os.path.join(root, name))
                    FileName = (os.path.join(root, name))

                    hasher = hashlib.md5()
                    with open(str(FileName), 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                    id = name.rstrip()
                    self.ident = id
                    if patternImageIDoblique.match(id):
                        production = 'Oblique'
                        block = id[5:10]
                    elif patternImageIDGeoDK.match(id):
                        production = 'GeoDK'
                        block = id[5:10]
                    else:
                        production = 'NA'
                        block = 'NA'
                    format = name.rstrip().split(".")[-1]
                    dateindexed = str(datetime.now())
                    dateindexed = dateindexed.split(".")[0]
                    file = str(root) + "\\" + str(name)
                    size = os.path.getsize(file)
                    size = float(size) / float(1048576)
                    HD_id = root[0:3]
                    path = str(root)
                    format = str(format)
                    datecreated = time.ctime(os.path.getctime(file))
                    md5hash = hasher.hexdigest()
                    string2 = "insert into " + str(self.DBschema) + "." + str(self.DBtable)
                    conn1 = psycopg2.connect("dbname=" + self.DBname + " user=" + self.DBuser + " host=" + self.DBhost + " password=" + self.DBpass)
                    cur1 = conn1.cursor()
                    cur1.itersize = 10
                    cur1.execute(
                        string2 + """ ("index_key","id","hd_id","disc_name","production","block","path","format","size(MB)","date_created","date_indexed","md5_hash") values(%(int1)s,%(str1)s,%(str2)s,%(str3)s,%(str4)s,%(str5)s,%(str6)s,%(str7)s,%(float1)s,%(str8)s,%(str9)s,%(str10)s) """,
                        {'int1': index_key, 'str1': id, 'str2': HD_id, 'str3': nextdiskindex, 'str4': production, 'str5': block, 'str6': path, 'str7': format, 'float1': size, 'str8': datecreated, 'str9': dateindexed, 'str10': md5hash})
                    conn1.commit()

                    self.emit(QtCore.SIGNAL("update2(QString)"), self.ident)
                    self.completed = float((pgrcount * 100) / pgrnum)
                    self.emit(QtCore.SIGNAL('update1(QString)'), str(self.completed))
                except IndexError:
                    pass
                except psycopg2.IntegrityError as e:
                    QMessageBox.information(None, "General Information", "Unexpected error:", str(e[0]))
                    conn1.rollback()
                    rollback = 'True'

        if rollback == 'True':
            QMessageBox.information(None, "GeoIndex", "commit error - rolling back:\n" + str(e[0]))
        else:
            pass
            #QMessageBox.information(None, "GeoIndex", "Volumne indexed, exiting")
        cur.close()
        conn.close()
        cur1.close()
        conn1.close()

class WorkThread2(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        # define variables from settings file
        self.ProjectLog, self.MainLog, self.PPC_GSD, self.Sun, self.Tilt, self.CamCal, self.ImageDir, self.DBImageDir, self.DBname, self.DBhost, self.DBport, self.DBuser, self.DBpass, self.DBschema, self.DBtable, self.DB_footprint, self.DB_ppc = self.readSettings2
    def __del__(self):
        self.wait()

    @property
    def readSettings2(self):
        settingsFile = os.path.dirname(__file__) + "\\settings.txt"
        ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir = SubScripts.readsettings(settingsFile)
        return (ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir)

    def run(self):
        try:
            DB_schema = self.DBschema
            DB_geom = "geom"
            (DB_name, DB_host, DB_port, DB_user, DB_pass, overwritedata, select, layer1, DB_table) = SubScripts.readtxt2()
            layer = QgsMapLayerRegistry.instance().mapLayersByName(layer1)[0]
            killed = ''

            if select == '1':
               selection = layer.selectedFeatures()
               self.emit(QtCore.SIGNAL('update6(QString)'), str("uploading selected features"))
            elif select == '2':
               selection = layer.getFeatures()
               self.emit(QtCore.SIGNAL('update6(QString)'), str("uploading all features"))
            else:
                pass
            pgrnum =  int(layer.featureCount())

            # DB connection and upload for footprints
            if DB_table == self.DB_footprint:
                conn = psycopg2.connect("dbname=" + DB_name + " user=" + DB_user + " host=" + DB_host + " password=" + DB_pass)
                cur = conn.cursor()
                cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (DB_table,))
                if cur.fetchone()[0]:
                    createtable = '0'
                    self.label2 = 'Footprint database found - uploading'
                else:
                    createtable = '1'
                    cur.execute(
                        "CREATE TABLE " + DB_schema + "." + DB_table + "(imageid TEXT PRIMARY KEY, easting float, northing float, height real,omega real, phi real, kappa real, direction text, timeutc text, cameraid text, "
                                                                       "coneid real, estacc real, height_eli text, timecet text, \"references\" text, producer text, level real, comment_co text, comment_gs text, status text, gsd text, geom geometry)")
                    conn.commit()

                listofattrs = ['ImageID', 'Easting', 'Northing', 'Height', 'Omega', 'Phi', 'Kappa', 'Direction', 'TimeUTC',
                               'CameraID', 'ConeID', 'EstAcc', 'Height_Eli', 'TimeCET', 'ReferenceS', 'Producer', 'Level', 'Comment_Co',
                               'Comment_GS', 'Status', 'GSD']
                obj = {}
                for n in listofattrs:
                    obj[n] = []

                imid = []
                list = []
                for feat in selection:
                    for i in obj.keys():
                        if str(feat[i]) == 'NULL':
                            feat[i] = ''
                        obj[i].append(feat[i])
                    geom = feat.geometry()
                    Geometri = geom.asPolygon()
                    list.append(Geometri)
                    imid.append(feat['ImageID'])

                finallist = []
                for ll in list:
                    finallist.append(str(ll).replace("[", "").replace("]", "").replace(",", " ").replace(")  (", "), (").replace("(", "").replace(")", ""))

                if overwritedata == '1':
                    self.emit(QtCore.SIGNAL('update5(QString)'), 'Overwriting existing data')
                elif overwritedata == '2':
                    self.emit(QtCore.SIGNAL('update5(QString)'), str('Not overwriting existing data, only adding'))

                notupdatedcount = 0
                updatedcount = 0
                insertcount = 0
                notinsertcount = 0
                Imupload = []
                pp = 0

                try:
                    n = 0
                    self.completed = 0
                    cur = conn.cursor()
                    for i in range(0, (len(obj['ImageID']))):
                        n += 1
                        try:
                            killed = SubScripts.readtxt4()
                            if killed == 'True':
                                break
                        except:
                            pass
                        try:
                            if overwritedata == '1':
                                cur.execute("select exists(SELECT imageid FROM " + DB_schema + "." + DB_table + " WHERE imageid = %s)", (obj['ImageID'][i],))
                                if cur.fetchone()[0] is True:
                                    Imupload.append("Updated")
                                    updatedcount = updatedcount + 1
                                    strengen = ("""update """  + DB_schema + "."  + DB_table + """ set imageid = '""" + str(obj['ImageID'][i]) + """',easting = '""" + str(obj['Easting'][i]) + """', northing = '""" + str(obj['Northing'][i]) + """',
                                                height = '""" + str(obj['Height'][i]) + """', omega = '""" + str(obj['Omega'][i]) + """', phi = '""" + str(obj['Phi'][i]) + """', kappa = '""" + str(obj['Kappa'][i]) + """',
                                                timeutc = '""" + str(obj['TimeUTC'][i]) + """', cameraid = '""" + str(obj['CameraID'][i]) + """', height_eli = '""" + str(obj['Height_Eli'][i]) + """',
                                                timecet = '""" + str(obj['TimeCET'][i]) + """', \"references\" = '""" + str(obj['ReferenceS'][i]) + """', producer = '""" + str(obj['Producer'][i]) + """', level = '""" + str(obj['Level'][i]) + """', comment_gs = '""" + str(obj['Comment_GS'][i]) + """', 
                                                comment_co = '""" + str(obj['Comment_Co'][i]) + """', status = '""" + str(obj['Status'][i]) + """', gsd = '""" + str(obj['GSD'][i]) + """' where imageid =""" + """'""" + str(obj['ImageID'][i]) + """'""")
                                    cur.execute(strengen)
                                else:
                                    Imupload.append("Did not exists in table - inserted")
                                    notupdatedcount = notupdatedcount + 1
                                    cur.execute("""INSERT INTO """  + DB_schema + "." + DB_table + """  ("imageid","easting","northing","height","omega","phi","kappa","timeutc","cameraid",
                                                                    "height_eli","timecet",\"references\","producer","level","comment_co","comment_gs","status","gsd","geom") VALUES(%(str1)s,%(float1)s,%(float2)s,%(real3)s,%(str2)s,
                                                                    %(str3)s,%(str4)s,%(str6)s,%(str7)s,%(real5)s,%(str8)s,%(str9)s,%(str10)s,%(str11)s,%(str12)s,%(str13)s,%(str14)s,%(str15)s,ST_GeomFromText(%(str16)s,25832))""",
                                                {'str1': obj['ImageID'][i], 'float1': obj['Easting'][i],
                                                 'float2': obj['Northing'][i],
                                                 'real3': obj['Height'][i],
                                                 'str2': obj['Omega'][i], 'str3': obj['Phi'][i],
                                                 'str4': obj['Kappa'][i],
                                                 'str6': obj['TimeUTC'][i], 'str7': obj['CameraID'][i],
                                                 'real5': str(obj['Height_Eli'][i]), 'str8': obj['TimeCET'][i],
                                                 'str9': obj['ReferenceS'][i], 'str10': obj['Producer'][i],
                                                 'str11': obj['Level'][i],
                                                 'str12': str(obj['Comment_Co'][i]),
                                                 'str13': str(obj['Comment_GS'][i]),
                                                 'str14': str(obj['Status'][i]), 'str15': str(obj['GSD'][i]),
                                                 'str16': str('POLYGON((' + finallist[i] + '))')})
                            elif overwritedata == '2':
                                cur.execute("select exists(SELECT imageid FROM " + DB_schema + "." + DB_table + " WHERE imageid = %s)", (obj['ImageID'][i],))
                                if cur.fetchone()[0] is False:
                                    Imupload.append("Inserted")
                                    insertcount = insertcount + 1
                                    cur.execute("""INSERT INTO """  + DB_schema + "." + DB_table + """  ("imageid","easting","northing","height","omega","phi","kappa","timeutc","cameraid",
                                                                    "height_eli","timecet",\"references\","producer","level","comment_co","comment_gs","status","gsd","geom") VALUES(%(str1)s,%(float1)s,%(float2)s,%(real3)s,%(str2)s,
                                                                    %(str3)s,%(str4)s,%(str6)s,%(str7)s,%(real5)s,%(str8)s,%(str9)s,%(str10)s,%(str11)s,%(str12)s,%(str13)s,%(str14)s,%(str15)s,ST_GeomFromText(%(str16)s,25832))""",
                                                {'str1': obj['ImageID'][i], 'float1': obj['Easting'][i],
                                                 'float2': obj['Northing'][i],
                                                 'real3': obj['Height'][i],
                                                 'str2': obj['Omega'][i], 'str3': obj['Phi'][i],
                                                 'str4': obj['Kappa'][i],
                                                 'str6': obj['TimeUTC'][i], 'str7': obj['CameraID'][i],
                                                 'real5': str(obj['Height_Eli'][i]), 'str8': obj['TimeCET'][i],
                                                 'str9': obj['ReferenceS'][i], 'str10': obj['Producer'][i],
                                                 'str11': obj['Level'][i],
                                                 'str12': str(obj['Comment_Co'][i]),
                                                 'str13': str(obj['Comment_GS'][i]),
                                                 'str14': str(obj['Status'][i]), 'str15': str(obj['GSD'][i]),
                                                 'str16': str('POLYGON((' + finallist[i] + '))')})
                                else:
                                    Imupload.append(" Not inserted - already exists")
                                    notinsertcount = notinsertcount + 1
                                    print "Not inserted - already exists!"
                                    pass
                        except  Exception, e:
                            QMessageBox.information(None, "General Info", 'ERROR:'+ e[0])
                        self.completed = ((n * 100) / (len(obj['ImageID'])))
                        self.emit(QtCore.SIGNAL('update4(QString)'), str(imid[i]))
                        self.emit(QtCore.SIGNAL('update3(QString)'), str(self.completed))
                    conn.commit()
                    rapporten = "Upload of: \n" + layer1 + "\n \nINFO: \n"

                    if createtable == '1':
                        rapporten = rapporten + 'Table '+ self.DB_footprint + ' created - this is the first entry\n'
                    if overwritedata == '1':
                        if updatedcount != 0:
                            rapporten = rapporten + str(updatedcount) + ' Footprints updated \n'
                        elif notupdatedcount != 0:
                            rapporten = rapporten + str(notupdatedcount) + 'Footprints did not exsist in table - inserted \n'
                    elif overwritedata == '2':
                        if insertcount != 0:
                            rapporten = rapporten + str(insertcount) + ' Footprints inserted \n'
                        elif notinsertcount != 0:
                            rapporten = rapporten + str(notinsertcount) + ' Footprints exists in table - not inserted \n'

                except Exception, e:
                    QMessageBox.information(None, "General Info", 'ERROR: ' + str(e[0]))

            elif DB_table == self.DB_ppc:
                try:
                    conn = psycopg2.connect("dbname=" + DB_name + " user=" + DB_user + " host=" + DB_host + " password=" + DB_pass)
                    cur = conn.cursor()
                    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (DB_table,))
                    if cur.fetchone()[0]:
                        createtable = '0'
                        self.label2 = 'PPC database found - uploading'
                    else:
                        createtable = '1'
                        cur.execute(
                            "CREATE TABLE " + DB_schema + "." + DB_table + "(imageid TEXT PRIMARY KEY, easting float, northing float, height real,omega real, phi real, kappa real, timeutc text, cameraid text, "
                                                                           "height_eli text, timecet text, \"references\" text, producer text, level real, comment_co text, comment_gs text, status text, gsd text, geom geometry)")
                        conn.commit()

                    listofattrs = ['ImageID', 'Easting', 'Northing', 'Height', 'Omega', 'Phi', 'Kappa', 'TimeUTC',
                                   'CameraID', 'Height_Eli', 'TimeCET', 'ReferenceS', 'Producer', 'Level', 'Comment_co',
                                   'Comment_GS', 'Status', 'GSD']
                    obj = {}
                    for n in listofattrs:
                        obj[n] = []

                    list = []
                    imid =[]
                    for feat in selection:
                        for i in obj.keys():
                            if str(feat[i])=='NULL':
                                feat[i]=''
                            obj[i].append(feat[i])
                        geom = feat.geometry()
                        Geometri = geom.asPoint()
                        list.append(Geometri)
                        imid.append(feat['ImageID'])

                    finallist = []
                    for ll in list:
                        finallist.append(str(ll).replace("[", "").replace("]", "").replace(",", " ").replace(")  (", "), (").replace("(", "").replace(")", ""))

                except Exception, e:
                    QMessageBox.information(None, "General Info", 'ERROR1: '+ e[0])

                if overwritedata == '1':
                    self.emit(QtCore.SIGNAL('update5(QString)'), 'Overwriting existing data')
                elif overwritedata == '2':
                    self.emit(QtCore.SIGNAL('update5(QString)'), str('Not overwriting existing data, only adding'))

                notupdatedcount = 0
                updatedcount = 0
                notinsertcount = 0
                insertcount = 0
                Imupload=[]
                try:
                    n=0
                    self.completed = 0
                    cur=conn.cursor()
                    for i in range(0, (len(obj['ImageID']))):
                        n += 1
                        try:
                            killed = SubScripts.readtxt4()
                            if killed == 'True':
                                break
                        except:
                            pass
                        try:
                            if overwritedata == '1':
                                cur.execute("select exists(SELECT imageid FROM "+ DB_schema + "." + DB_table + " WHERE imageid = %s)",(obj['ImageID'][i],))
                                if cur.fetchone()[0] is True:
                                    Imupload.append("Updated")
                                    updatedcount = updatedcount + 1
                                    strengen = ("""update """+ DB_schema + "." + DB_table + """ set imageid = '""" + str(obj['ImageID'][i]) + """',easting = '""" + str(obj['Easting'][i]) + """', northing = '""" + str(obj['Northing'][i]) + """',
                                                height = '""" + str(obj['Height'][i]) + """', omega = '""" + str(obj['Omega'][i]) + """', phi = '""" + str(obj['Phi'][i]) + """', kappa = '""" + str(obj['Kappa'][i]) + """',
                                                timeutc = '""" + str(obj['TimeUTC'][i]) + """', cameraid = '""" + str(obj['CameraID'][i]) + """', height_eli = '""" + str(obj['Height_Eli'][i]) + """',
                                                timecet = '""" + str(obj['TimeCET'][i]) + """', \"references\" = '""" + str(obj['ReferenceS'][i]) + """', producer = '""" + str(obj['Producer'][i]) + """', level = '""" + str(obj['Level'][i]) + """', comment_gs = '""" + str(obj['Comment_GS'][i]) + """', 
                                                comment_co = '""" + str(obj['Comment_co'][i]) + """', status = '""" + str(obj['Status'][i]) + """', gsd = '""" + str(obj['GSD'][i]) + """' where imageid =""" + """'""" + str(obj['ImageID'][i]) + """'""")
                                    cur.execute(strengen)
                                else:
                                    Imupload.append("Did not exists in table - inserted")
                                    notupdatedcount = notupdatedcount + 1
                                    cur.execute("""INSERT INTO """ + DB_schema + "." + DB_table + """  ("imageid","easting","northing","height","omega","phi","kappa","timeutc","cameraid",
                                                                "height_eli","timecet",\"references\","producer","level","comment_co","comment_gs","status","gsd","geom") VALUES(%(str1)s,%(float1)s,%(float2)s,%(real3)s,%(str2)s,
                                                                %(str3)s,%(str4)s,%(str6)s,%(str7)s,%(real5)s,%(str8)s,%(str9)s,%(str10)s,%(str11)s,%(str12)s,%(str13)s,%(str14)s,%(str15)s,ST_GeomFromText(%(str16)s,25832))""",
                                                {'str1': obj['ImageID'][i], 'float1': obj['Easting'][i],
                                                 'float2': obj['Northing'][i],
                                                 'real3': obj['Height'][i],
                                                 'str2': obj['Omega'][i], 'str3': obj['Phi'][i],
                                                 'str4': obj['Kappa'][i],
                                                 'str6': obj['TimeUTC'][i], 'str7': obj['CameraID'][i],
                                                 'real5': str(obj['Height_Eli'][i]), 'str8': obj['TimeCET'][i],
                                                 'str9': obj['ReferenceS'][i], 'str10': obj['Producer'][i],
                                                 'str11': obj['Level'][i],
                                                 'str12': str(obj['Comment_co'][i]),
                                                 'str13': str(obj['Comment_GS'][i]),
                                                 'str14': str(obj['Status'][i]), 'str15': str(obj['GSD'][i]),
                                                 'str16': str('POINT(' + finallist[i] + ')')})

                            elif overwritedata == '2':
                                cur.execute("select exists(SELECT imageid FROM " +  DB_schema + "." + DB_table + " WHERE imageid = %s)",(obj['ImageID'][i],))
                                if cur.fetchone()[0] is False:
                                    Imupload.append("Inserted")
                                    insertcount = insertcount + 1
                                    cur.execute("""INSERT INTO """ + DB_schema + "." + DB_table + """  ("imageid","easting","northing","height","omega","phi","kappa","timeutc","cameraid",
                                                                "height_eli","timecet",\"references\","producer","level","comment_co","comment_gs","status","gsd","geom") VALUES(%(str1)s,%(float1)s,%(float2)s,%(real3)s,%(str2)s,
                                                                %(str3)s,%(str4)s,%(str6)s,%(str7)s,%(real5)s,%(str8)s,%(str9)s,%(str10)s,%(str11)s,%(str12)s,%(str13)s,%(str14)s,%(str15)s,ST_GeomFromText(%(str16)s,25832))""",
                                                {'str1': obj['ImageID'][i], 'float1': obj['Easting'][i],
                                                 'float2': obj['Northing'][i],
                                                 'real3': obj['Height'][i],
                                                 'str2': obj['Omega'][i], 'str3': obj['Phi'][i],
                                                 'str4': obj['Kappa'][i],
                                                 'str6': obj['TimeUTC'][i], 'str7': obj['CameraID'][i],
                                                 'real5': str(obj['Height_Eli'][i]), 'str8': obj['TimeCET'][i],
                                                 'str9': obj['ReferenceS'][i], 'str10': obj['Producer'][i],
                                                 'str11': obj['Level'][i],
                                                 'str12': str(obj['Comment_co'][i]),
                                                 'str13': str(obj['Comment_GS'][i]),
                                                 'str14': str(obj['Status'][i]), 'str15': str(obj['GSD'][i]),
                                                 'str16': str('POINT(' + finallist[i] + ')')})
                                else:
                                    Imupload.append(" Not inserted - already exists")
                                    notinsertcount = notinsertcount + 1
                                    pass
                            self.completed = ((n * 100) / (len(obj['ImageID'])))
                            self.emit(QtCore.SIGNAL('update4(QString)'), str(imid[i]))
                            self.emit(QtCore.SIGNAL('update3(QString)'), str(self.completed))
                        except psycopg2.IntegrityError:
                            conn.rollback()
                            print 'commit error - rolling back'
                    conn.commit()
                    rapporten = "Upload of: \n" + layer1 + "\n \nINFO: \n Total number of PPC/Footprints: "+str(len(obj['ImageID']))+ "\n \n"

                    if createtable == '1':
                        rapporten = rapporten + 'Table '+ self.DB_ppc + ' created - this is the first entry\n'
                    if overwritedata == '1':
                        if updatedcount != 0:
                            rapporten = rapporten + str(updatedcount) + ' PPCs updated \n'
                        elif notupdatedcount != 0:
                            rapporten = rapporten + str(notupdatedcount) + ' PPCs did not exsist in table - inserted \n'
                    elif overwritedata == '2':
                        if insertcount != 0:
                            rapporten = rapporten + str(insertcount) + ' PPCs inserted \n'
                        elif notinsertcount != 0:
                            rapporten = rapporten + str(notinsertcount) + ' PPCs exists in table - not inserted \n'

                except Exception, e:
                    QMessageBox.information(None, "General Info", 'ERROR:', e[0])

            #conn.commit()
            #QMessageBox.information(None, "Upload-DB", rapporten)
        except Exception, e:
            QMessageBox.information(None, "General Info", 'ERROR:', e[0])

        if killed == 'True':
            rapporten = rapporten + "\n See rapport file for specifics - pending"
            self.emit(QtCore.SIGNAL('update7(QString)'), rapporten)
        else:
            rapporten = rapporten + "\n See rapport file for specifics - pending"
            self.emit(QtCore.SIGNAL('update8(QString)'), rapporten)

class WorkThread3(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        # define variables from settings file
        self.ProjectLog, self.MainLog, self.PPC_GSD, self.Sun, self.Tilt, self.CamCal, self.ImageDir, self.DBImageDir, self.DBname, self.DBhost, self.DBport, self.DBuser, self.DBpass, self.DBschema, self.DBtable, self.DB_footprint, self.DB_ppc = self.readSettings2
    def __del__(self):
        self.wait()

    @property
    def readSettings2(self):
        settingsFile = os.path.dirname(__file__) + "\\settings.txt"
        ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir = SubScripts.readsettings(settingsFile)
        return (ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir)

    def check_hist(filen):
        print "test"
        filstat = gdalhist.main(['', '-hist', filen])

        lowerlim = 999
        upperlim = 999

        for i in filstat:
            if i[0] != 'value' and lowerlim == 999 and i[2] > 0.01 and i[4] > 0.01 and i[6] > 0.01:
                lowerlim = i[0]
            if i[0] != 'value' and upperlim == 999 and i[2] > 0.99 and i[4] > 0.99 and i[6] > 0.99:
                upperlim = i[0]

        # print str(lowerlim) + " " + str(upperlim)
        return (lowerlim, upperlim)

    def run(self):
        (overwritedata, select, path, drevnavn, DB_table) = SubScripts.readtxt3()
        try:
            path = path.replace('\\','\\\\')
            skipfactor = 1
            filantal = 0
            if DB_table == self.DB_footprint:
                production = 3
            else:
                production = 1
        except:
            print "running on local settings"

        conn = psycopg2.connect("dbname=" + self.DBname + " user=" + self.DBuser + " host=" + self.DBhost + " password=" + self.DBpass)
        cur = conn.cursor()

        #jobnavn = str(win32api.GetVolumeInformation(os.path.splitdrive(path)[0])[0])
        jobnavn = str(os.path.splitdrive(path)[0])
        tiftest = []
        jpgtest = []
        imtemp = []
        imfiles = []


        if production == 3:
            imtemp = glob.glob(path+"\\**\\**\\*.jpg")
            for i in imtemp:
                imfiles.append(i.replace('\\','\\\\'))
        else:
            try:
                # list both tiff or jpeg imagery
                tiftest = glob.glob(path+"\\*.tif")
                jpgtest = glob.glob(path+"\\*.jpg")
            except:
                print self.emit(QtCore.SIGNAL('update2(QString)'), "Error: Maybe production is oblique")
        if tiftest:
            for i in tiftest:
                imfiles.append(i.replace('\\','\\\\'))
        elif jpgtest:
            for i in jpgtest:
                imfiles.append(i.replace('\\','\\\\'))
        else:
            pass

        #subprocess.call(["cmd", "/c", "dir " + path + "\\*.tif /s /b >" + dirfile])
        #self.emit(QtCore.SIGNAL('update2(QString)'), str(dirfile))
        drevnavn = FindUSBname.getusbname(os.path.splitdrive(path)[0])
        nowreadingnr = 0.0
        filantal = len(imfiles)


        for line in imfiles:
            try:
                killed = SubScripts.readtxt4()
                if killed == 'True':
                    break
            except:
                pass
            line = line.replace('\\', '/')
            line = line.replace('//', '/')
            filnavn = os.path.basename(line)
            filnavn = (os.path.splitext(filnavn)[0])
            if production == 1:
                filnavn = filnavn[0:18]
            elif production == 2:
                filnavn = filnavn[0:18]
            elif production == 3:
                filnavn = filnavn[0:26]
            #self.emit(QtCore.SIGNAL('update2(QString)'), str(filnavn))

            dbkald = "update " + self.DBschema + "." + DB_table + " set \"path\" = \'"+ line +"\' WHERE imageid = \'" + str(filnavn)+"\'"
            cur.execute(dbkald)
            dbkald = "update " + self.DBschema + "." + DB_table + " set \"drive\" = \'" + drevnavn + "\' WHERE imageid = \'" + str(filnavn) + "\'"
            cur.execute(dbkald)
            rowtal = cur.rowcount



            if rowtal == 1:
                decimalnow = (nowreadingnr / skipfactor)
                if str(decimalnow - int(decimalnow))[1:] == '.0':
                    try:
                        filstat = gdalhist.main(['', '-hist', line])
                        lowerlim = 999
                        upperlim = 999

                        for i in filstat:
                            if i[0] != 'value' and lowerlim == 999 and i[2] > 0.01 and i[4] > 0.01 and i[6] > 0.01:
                                lowerlim = i[0]
                            if i[0] != 'value' and upperlim == 999 and i[2] > 0.99 and i[4] > 0.99 and i[6] > 0.99:
                                upperlim = i[0]
                    except:
                        lowerlim = 999
                        upperlim = 999

                    self.emit(QtCore.SIGNAL('update2(QString)'), "Arbejder på: \n"+str(filnavn) + ": hist low-" + str(lowerlim) + " & hist high-" + str(upperlim))
                    dbkald = "update " + self.DBschema + "." + DB_table + " set \"hist_low\" = \'" + str(lowerlim) + "\' WHERE imageid = \'" + str(filnavn) + "\'"
                    cur.execute(dbkald)
                    dbkald = "update " + self.DBschema + "." + DB_table + " set \"hist_high\" = \'" + str(upperlim) + "\' WHERE imageid = \'" + str(filnavn) + "\'"
                    cur.execute(dbkald)

                nowreadingnr = nowreadingnr + 1
            else:
                self.emit(QtCore.SIGNAL('update2(QString)'), 'cannot find foto in DB')
                break
            conn.commit()
            pdone = int(float(nowreadingnr) / float(filantal) * 100)
            self.emit(QtCore.SIGNAL('update1(QString)'), str(pdone))
            if int((math.modf(pdone / 1))[0] * 100) == 0:
                propath = "F:\\GEO\\DATA\\RemoteSensing\\Drift\\Processing\\"
                maskinenavn = (socket.gethostname())
                with open(propath + maskinenavn + ".html", "w") as text_file:
                    text_file.write("<!DOCTYPE html>" + " \n")
                    text_file.write("<html>" + " \n")
                    text_file.write("<title>GEO Processing</title>" + " \n")
                    text_file.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">" + " \n")
                    text_file.write("<link rel=\"stylesheet\" href=\"https://www.w3schools.com/w3css/4/w3.css\">" + " \n")
                    text_file.write("<body>" + " \n")
                    text_file.write("<div class=\"w3-container\">" + " \n")
                    text_file.write("  <button type=\"button\" class=\"btn btn-info\" onclick=\"InfoFunction()\" >Info</button> \n")
                    if int(pdone) >= 100:
                        text_file.write("  <h7>" + maskinenavn + " is idle</h7>" + " \n")
                        text_file.write("  <div class=\"w3-light-grey w3-small w3-border w3-round-large\">" + " \n")
                        text_file.write("    <div class=\"w3-container w3-green w3-center w3-round-large\" style=\"width:100%\">All done</div>" + " \n")
                        text_file.write("  </div>" + " \n")
                    else:
                        text_file.write("  <h7>" + maskinenavn + " running " + drevnavn + "</h7>" + " \n")
                        text_file.write("  <div class=\"w3-light-grey w3-small w3-border w3-round-large\">" + " \n")
                        text_file.write("    <div class=\"w3-container w3-blue w3-center w3-round-large\" style=\"width:" + str(pdone) + "%\">" + str(pdone) + "%</div>" + " \n")
                        text_file.write("  </div>" + " \n")
                    text_file.write("" + " \n")
                    text_file.write("<script>" + " \n")
                    text_file.write("function InfoFunction() {" + " \n")
                    text_file.write("    alert(\"Hist high: "+str(upperlim)+" \& Hist low: "+str(lowerlim)+"\");" + " \n")
                    text_file.write("}" + " \n")
                    text_file.write("</script>" + " \n")
                    text_file.write("</div>" + " \n")
                    text_file.write("</body>" + " \n")
                    text_file.write("</html>" + " \n")
                    text_file.close()

class MyApp(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #make gui attributes

        self.runButton = QtGui.QPushButton("Upload")
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.pgr = QtGui.QProgressBar(self)
        self.label = QtGui.QLabel()
        self.label2 = QtGui.QLabel()
        #set gui layout
        self.layout = QtGui.QGridLayout(self)
        self.layout.setSpacing(10)
        self.runButton.setMaximumSize(75, 23)
        self.cancelButton.setMaximumSize(75, 23)
        self.layout.addWidget(self.runButton, 0,9,2,9, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.pgr,1,0,2,0)
        self.layout.addWidget(self.label,0,1,2,1)
        self.layout.addWidget(self.label2,0,2,5,1)
        #set connections
        self.connect(self.runButton, QtCore.SIGNAL("released()"), self.test)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.cancel)
        #self.cancelButton.clicked.connect(WorkThread1.kill(self))
        #misc
        self.setGeometry(300, 300, 500, 130)
        self.setWindowTitle('Index')

    def add1(self, text):
        num = int(float(text))
        self.pgr.setValue(num)
        if num == 100:
            self.label.setText("Upload done!")

    def add2(self, text):
        try:
            self.layout.removeWidget(self.runButton)
            self.runButton.deleteLater()
            self.runButton = None
        except AttributeError as e:
            pass
        stext = str(text)
        self.label.setText(stext)

    def test(self):
        self.pgr.setValue(0)
        self.workThread = WorkThread1()
        self.connect(self.workThread, QtCore.SIGNAL("update2(QString)"), self.add2)
        self.connect(self.workThread, QtCore.SIGNAL("update1(QString)"), self.add1)
        self.workThread.start()

    def cancel(self):
        file = open(os.path.dirname(__file__) + "\\subscripts\\" + "kill.txt", "w")
        file.write('True')
        file.close()
        self.layout.removeWidget(self.cancelButton)
        self.cancelButton.deleteLater()
        self.cancelButton = None
        self.cancelButton = QtGui.QPushButton("Quit")
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.quit)

    def quit(self):
        self.close()

class MyAppII(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #make gui attributes

        self.runButton = QtGui.QPushButton("Upload")
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.pgr = QtGui.QProgressBar(self)
        self.wk2label = QtGui.QLabel()
        self.wk2label2 = QtGui.QLabel()
        self.wk2label3 = QtGui.QLabel()
        #set gui layout
        self.layout = QtGui.QGridLayout(self)
        self.layout.setSpacing(10)
        self.runButton.setMaximumSize(75, 23)
        self.cancelButton.setMaximumSize(75, 23)
        self.layout.addWidget(self.runButton, 0,9,2,9, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.pgr,1,0,2,0)
        self.layout.addWidget(self.wk2label,0,2,2,1)
        self.layout.addWidget(self.wk2label2, 0, 0)
        self.layout.addWidget(self.wk2label3, 1, 0)
        #set connections
        self.connect(self.runButton, QtCore.SIGNAL("released()"), self.test)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.cancel)
        #misc
        self.setGeometry(300, 300, 500, 130)
        self.setWindowTitle('DB upload')

    def add1(self, text):
        num = int(float(text))
        self.pgr.setValue(num)
        if num == 100:
            self.wk2label.setText("Upload done!")

    def add2(self, text):
        try:
            self.layout.removeWidget(self.runButton)
            self.runButton.deleteLater()
            self.runButton = None
        except AttributeError as e:
            pass
        stext = str(text)
        self.wk2label.setText(stext)

    def add3(self, text):
        tt = "INFO: "+str(text)
        self.wk2label2.setText(tt)

    def add4(self, text):
        tt = str(text)
        self.wk2label3.setText(tt)
        self.layout.removeWidget(self.runButton)
        self.runButton.deleteLater()
        self.runButton = None

    def add5(self, text):
        tt = str(text)
        self.wk2label3.hide()
        self.wk2label3.setText(tt)

    def add6(self, text):
        tt = str(text)
        self.wk2label3.setText(tt)
        self.layout.removeWidget(self.pgr)
        self.pgr.deleteLater()
        self.pgr = None
        self.layout.removeWidget(self.cancelButton)
        self.cancelButton.deleteLater()
        self.cancelButton = None
        self.layout.removeWidget(self.wk2label)
        self.wk2label.deleteLater()
        self.wk2label = None
        self.layout.removeWidget(self.wk2label2)
        self.wk2label2.deleteLater()
        self.wk2label2 = None
        self.cancelButton = QtGui.QPushButton("Quit")
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.quit4real)

    def test(self):
        self.pgr.setValue(0)
        self.workThread2 = WorkThread2()
        self.connect(self.workThread2, QtCore.SIGNAL("update4(QString)"), self.add2)
        self.connect(self.workThread2, QtCore.SIGNAL("update3(QString)"), self.add1)
        self.connect(self.workThread2, QtCore.SIGNAL("update5(QString)"), self.add3)
        self.connect(self.workThread2, QtCore.SIGNAL("update6(QString)"), self.add4)
        self.connect(self.workThread2, QtCore.SIGNAL("update7(QString)"), self.add5)
        self.connect(self.workThread2, QtCore.SIGNAL("update8(QString)"), self.add6)
        self.workThread2.start()

    def cancel(self):
        file = open(os.path.dirname(__file__) + "\\subscripts\\" + "kill.txt", "w")
        file.write('True')
        file.close()
        self.layout.removeWidget(self.cancelButton)
        self.cancelButton.deleteLater()
        self.cancelButton = None
        self.cancelButton = QtGui.QPushButton("Show Results")
        self.layout.addWidget(self.cancelButton, 0, 11, 2, 11, QtCore.Qt.AlignRight)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.quit)

    def quit(self):
        self.wk2label3.show()
        self.layout.removeWidget(self.pgr)
        self.pgr.deleteLater()
        self.pgr = None
        self.layout.removeWidget(self.cancelButton)
        self.cancelButton.deleteLater()
        self.cancelButton = None
        self.layout.removeWidget(self.wk2label)
        self.wk2label.deleteLater()
        self.wk2label = None
        self.layout.removeWidget(self.wk2label2)
        self.wk2label2.deleteLater()
        self.wk2label2 = None
        self.cancelButton = QtGui.QPushButton("Quit")
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.quit4real)

    def quit4real(self):
        self.close()

class MyAppIII(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #make gui attributes

        self.runButton = QtGui.QPushButton("Run")
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.pgr = QtGui.QProgressBar(self)
        self.label = QtGui.QLabel()
        self.label2 = QtGui.QLabel()
        #set gui layout
        self.layout = QtGui.QGridLayout(self)
        self.layout.setSpacing(10)
        self.runButton.setMaximumSize(75, 23)
        self.cancelButton.setMaximumSize(75, 23)
        self.layout.addWidget(self.runButton, 0,9,2,9, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.pgr,1,0,2,0)
        self.layout.addWidget(self.label,0,1,2,1)
        self.layout.addWidget(self.label2,0,2,5,1)
        #set connections
        self.connect(self.runButton, QtCore.SIGNAL("released()"), self.test)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.cancel)
        #misc
        self.setGeometry(300, 300, 500, 130)
        self.setWindowTitle('Hist')

    def add1(self, text):
        num = int(float(text))
        self.pgr.setValue(num)
        if num == 100:
            self.label.setText("Hist mining done!")

    def add2(self, text):
        try:
            self.layout.removeWidget(self.runButton)
            self.runButton.deleteLater()
            self.runButton = None
        except AttributeError as e:
            pass
        stext = str(text)
        self.label.setText(stext)

    def test(self):
        self.pgr.setValue(0)
        self.workThread = WorkThread3()
        self.connect(self.workThread, QtCore.SIGNAL("update2(QString)"), self.add2)
        self.connect(self.workThread, QtCore.SIGNAL("update1(QString)"), self.add1)
        self.workThread.start()

    def cancel(self):
        file = open(os.path.dirname(__file__) + "\\subscripts\\" + "kill.txt", "w")
        file.write('True')
        file.close()
        self.layout.removeWidget(self.cancelButton)
        self.cancelButton.deleteLater()
        self.cancelButton = None
        self.cancelButton = QtGui.QPushButton("Quit")
        self.layout.addWidget(self.cancelButton,0,11,2,11, QtCore.Qt.AlignRight)
        self.connect(self.cancelButton, QtCore.SIGNAL("released()"), self.quit)

    def quit(self):
        self.close()


class RSQC:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RSQC_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = RSQCDialog()
        #Plugin window stays on top
        #self.dlg.setWindowFlags(self.dlg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RS QC')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RSQC')
        self.toolbar.setObjectName(u'RSQC')

        #define variables from settings file
        self.ProjectLog, self.MainLog, self.PPC_GSD, self.Sun, self.Tilt, self.CamCal, self.ImageDir, self.DBImageDir, self.DBname, self.DBhost, self.DBport, self.DBuser, self.DBpass, self.DBschema, self.DBtable, self.DB_footprint, self.DB_ppc = self.readSettings
        #self.DBname1, self.DBhost1, self.DBport1, self.DBuser1, self.DBpass1, self.DBschema1, self.DBtable1 = self.readSettings1

        #Define Button connections
        self.dlg.pushButton_path.clicked.connect(self.showFileSelectDialogInput)
        self.dlg.pushButton_index1.clicked.connect(self.getIndexes)
        self.dlg.pushButton_InputDB.clicked.connect(self.showFileSelectDialogInputDB)
        self.dlg.pushButton_InputPPC.clicked.connect(self.showFileSelectDialogInputPPC)
        self.dlg.pushButton_InputImageDir.clicked.connect(self.showFileSelectDialogInputImageDir)
        self.dlg.radioButtonPPC_ob.toggled.connect(self.radio1_ob_clicked)
        self.dlg.radioButtonPPC_Nadir.toggled.connect(self.radio1_Nadir_clicked)

        #define pre defined variables
        self.dlg.lineEditCamDir.setText('F:\\GEO\\DATA\\RemoteSensing\\Drift\\CameraCalibrations')
        self.dlg.checkBoxPic.setChecked(True)
        self.dlg.checkBoxGSD.setChecked(True)
        self.dlg.lineEditGSD.setText(self.PPC_GSD)
        self.dlg.checkBoxSun.setChecked(True)
        self.dlg.lineEditSUN.setText(self.Sun)
        self.dlg.checkBoxFile.setChecked(True)
        self.dlg.checkBoxFormat.setChecked(True)
        self.dlg.checkBoxTilt.setChecked(True)
        self.dlg.lineEditTilt.setText(self.Tilt)
        self.dlg.checkBoxRef.setChecked(True)
        self.dlg.lineEditRef.setText('ETRS89,UTM32N,DVR90')
        #temp
        self.dlg.lineEditImageDir.setText('D:\\Image_tiffjpeg_test\\Image_JPEG')
        #temp
        self.dlg.radioButtonPPC_ob.setChecked(True)
        self.dlg.radioButtonPPC_Nadir.setChecked(True)
        self.dlg.radioButtonDB_Nadir.setChecked(True)
        self.dlg.radioButtonDBQC_Nadir.setChecked(True)
        self.dlg.radioButtonDB_Nadir_2.setChecked(True)
        self.dlg.db_name.setText(self.DBname)
        self.dlg.db_host.setText(self.DBhost)
        self.dlg.db_port.setText(self.DBport)
        self.dlg.db_user.setText(self.DBuser)
        self.dlg.db_password.setText(self.DBpass)
        self.dlg.db_name_2.setText(self.DBname)
        self.dlg.db_host_2.setText(self.DBhost)
        self.dlg.db_port_2.setText(self.DBport)
        self.dlg.db_user_2.setText(self.DBuser)
        self.dlg.db_password_2.setText(self.DBpass)
        self.dlg.db_name_3.setText(self.DBname)
        self.dlg.db_host_3.setText(self.DBhost)
        self.dlg.db_port_3.setText(self.DBport)
        self.dlg.db_user_3.setText(self.DBuser)
        self.dlg.db_password_3.setText(self.DBpass)


        # set values from settings file
        self.dlg.label_15.setText('Index name in DB ('+self.DBtable+')')
        self.dlg.radioButtonDB_ob.setText('Oblique ( '+self.DB_footprint +' )')
        self.dlg.radioButtonDB_Nadir.setText('Nadir ( '+self.DB_ppc +' )')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RSQC', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RSQC/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PPC & Footprint QualityControl'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&RS QC'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    @property
    def readSettings(self):
        settingsFile = os.path.dirname(__file__) + "\\settings.txt"
        ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir = SubScripts.readsettings(settingsFile)
        return (ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir)


    def showFileSelectDialogInput(self):
        global fname1
        fname1 = QFileDialog.getExistingDirectory( None, 'Open camera calibration directory', os.path.dirname(__file__))
        self.dlg.lineEdit.setText(str(fname1))

    def showFileSelectDialogInputDB(self):
       fname = QFileDialog.getExistingDirectory( None, 'Open image directory', os.path.dirname(__file__))
       self.dlg.lineEditDBImageDir.setText(fname)

    def showFileSelectDialogInputPPC(self):
        fname = QFileDialog.getExistingDirectory(None, 'Open camera calibration directory', os.path.dirname(os.path.realpath(__file__)))
        fname = string.replace(fname, '\\', '/')
        self.dlg.lineEditCamDir.setText(fname)

    def showFileSelectDialogInputImageDir(self):
        fname = QFileDialog.getExistingDirectory(None, 'Open camera calibration directory', os.path.dirname(os.path.realpath(__file__)))
        fname = string.replace(fname, '\\', '/')
        self.dlg.lineEditImageDir.setText(fname)

    def radio1_ob_clicked(self, enabled):
        if enabled:
            self.dlg.lineEditGSD.setText('0.10')
            self.dlg.lineEditSUN.setText('15')
            self.dlg.checkBoxVoids.setChecked(True)

    def radio1_Nadir_clicked(self, enabled):
        if enabled:
            self.dlg.lineEditGSD.setText('0.15')
            self.dlg.lineEditSUN.setText('25')
            self.dlg.checkBoxVoids.setChecked(False)

    def getIndexes(self):
        self.dlg.label_27.setText("Privious Index Examples: (most recent on top)")
        conn = psycopg2.connect("dbname=" + self.DBname + " user=" + self.DBuser + " host=" + self.DBhost + " password=" + self.DBpass)
        cur = conn.cursor()
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (self.DBtable,))
        if cur.fetchmany(10)[0]:
            dbkald = "SELECT DISTINCT disc_name FROM " + str(self.DBschema) + "." + str(self.DBtable) + " ORDER BY \"disc_name\" DESC"
            cur.execute(dbkald)
            ccdb_svar = cur.fetchall()
            res = list(sorted(ccdb_svar,reverse=True))
            if not res:
                self.dlg.listWidget1.addItem('None')
            else:
                for x in range(0,len(res)):
                    itm = QListWidgetItem(str(res[x][0]))
                    self.dlg.listWidget1.addItem(itm)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.setWindowTitle(self.tr("Quality Control"))
        # populate layer list
        mapCanvas = self.iface.mapCanvas()
        lyrs = self.iface.legendInterface().layers()
        DB_list = [self.DB_ppc, self.DB_footprint]
        lyr_list = []
        for layer in lyrs:
            lyr_list.append(layer.name())
        self.dlg.inShapeAPPC.clear()
        self.dlg.inShapeAPPC.addItems(lyr_list)
        self.dlg.inShapeAImage.clear()
        self.dlg.inShapeAImage.addItems(DB_list)
        self.dlg.inShapeDB.clear()
        self.dlg.inShapeDB.addItems(lyr_list)
        result = self.dlg.exec_()
        currentIndex = self.dlg.tabWidget.currentIndex()
        # When OK is pressed
        if result:
            if str(currentIndex) == "0":
                file = open(os.path.dirname(__file__) + "\\subscripts\\"+"nextindex.txt", "w")
                file.write(self.dlg.lineEdit_3.text())
                file.close()
                file = open(os.path.dirname(__file__) + "\\subscripts\\" + "dir.txt", "w")
                file.write(self.dlg.lineEdit.text())
                file.close()
                self.window = MyApp()
                self.window.show()

            if str(currentIndex) == "1":
                import subprocess
                inputLayer = unicode(self.dlg.inShapeAPPC.currentText())
                WantedCamPath = str(self.dlg.lineEditCamDir.text())
                caminfo = SubScripts.readCameras(self, WantedCamPath)
                inputFilNavn = self.dlg.inShapeAPPC.currentText()
                canvas = self.iface.mapCanvas()
                allLayers = canvas.layers()

                try:
                    count = 0
                    for i in allLayers:
                        if(i.name() == inputFilNavn):
                            layer=i
                            # Check if layer attributes list contains values according to SDFE standard.
                            if self.dlg.checkBoxFile.isChecked():
                                #Pipe layer attributes into list
                                AttributesList = SubScripts.format1(self, layer)
                                #Create list of attributes to check for. Both for oblique and nadir
                                if self.dlg.radioButtonPPC_ob.isChecked():
                                    PossibleValues = ['ImageID','Easting','Northing','Height','Omega','Phi','Kappa','Direction','TimeUTC','CameraID','ConeID','EstAcc','Height_Eli','TimeCET','ReferenceS','Producer','Level','Comment_Co','Comment_GS','Status','GSD']
                                elif self.dlg.radioButtonPPC_Nadir.isChecked():
                                    PossibleValues = ['ImageID','Easting','Northing','Height','Omega','Phi','Kappa','TimeUTC','CameraID','Height_Eli','TimeCET','ReferenceS','Producer','Level','Comment_Co','Comment_GS','Status','GSD']

                                #Find number of values in attributes list that conform with SDFE's standard(ld1) and number of those that do not(ld1-ld2).
                                ld1,ld2 = SubScripts.format2(self, PossibleValues, AttributesList)

                                # Set number of failed format counts for both oblique and nadir
                                if self.dlg.radioButtonPPC_ob.isChecked():
                                    if ld1 == 21:
                                        NameFailCount = 0
                                    elif ld1 < 21:
                                        QMessageBox.information(None, "status", "Files is missing some attributes. \n Check that the following fields are pressent in the attributes table header: \n 'ImageID','Easting','Northing','Height','Omega','Phi','Kappa','Direction','TimeUTC','CameraID','ConeID','EstAcc','Height_Eli',\n'TimeCET','ReferenceS','Producer','Level','Comment_Co','Comment_GS','Status','GSD'" )
                                elif self.dlg.radioButtonPPC_Nadir.isChecked():
                                    if ld1 == 18:
                                        NameFailCount = 0
                                    elif ld1 < 18:
                                        QMessageBox.information(None, "status", "Files is missing some attributes. \n Check that the following fields are pressent in the attributes table header: \n 'ImageID','Easting','Northing','Height','Omega','Phi','Kappa','TimeUTC','CameraID','Height_Eli',\n'TimeCET','ReferenceS','Producer','Level','Comment_Co','Comment_GS','Status'")

                            # start looping through layer
                            # create virtual layer for displaying results of  check.
                            vl = QgsVectorLayer("Point", "RSQC-check: " + str(inputFilNavn), "memory")
                            pr = vl.dataProvider()
                            # Define features for name-format checker
                            commentCount = 0
                            GSDfailCount = 0
                            SUNfailCount = 0
                            TILTfailCount = 0
                            REFfailCount = 0
                            FeatFailCount = 0
                            FeatOrientationFail = 0
                            fiveinarow = 0
                            kappacount = 0
                            nn=0
                            # add fields
                            pr.addAttributes([QgsField("ImageID", QVariant.String),
                                              QgsField("GSD", QVariant.String),
                                              QgsField("SunCheck", QVariant.String),
                                              QgsField("SunAngle", QVariant.String),
                                              QgsField("Overlap", QVariant.String),
                                              QgsField("Tilt", QVariant.String),
                                              QgsField("RefSys", QVariant.String),
                                              QgsField("NameFormat", QVariant.String),
                                              QgsField("Kappa", QVariant.String)])

                            if self.dlg.useSelectedAPPC.isChecked():
                                selection = layer.selectedFeatures()
                            else:
                                selection = layer.getFeatures()
                            cc=0
                            for feat in selection:
                                cc+=1

                            if self.dlg.useSelectedAPPC.isChecked():
                                selection = layer.selectedFeatures()
                                QMessageBox.information(None, "status", "checking selected features")
                            else:
                                selection = layer.getFeatures()
                                QMessageBox.information(None, "status", "checking all features")


                            # Loop through features in selected layer
                            for feat in selection:
                                nn+=1
                                geom = feat.geometry().centroid()
                                Geometri = geom.asPoint()
                                ImageID = feat['ImageID']

                                # General checks
                                producent = str(feat['Producer'])
                                kommentar = str(feat['COMMENT_CO'])
                                Kamera = feat['CameraID']
                                fundet = False
                                for kam in caminfo:
                                    if kam[0] == Kamera:
                                        CAM_ID = kam[0]
                                        PIXEL_SIZE = kam[1]
                                        PRINCIPAL_DISTANCE = kam[2]
                                        fundet = True
                                if fundet == False:
                                    QMessageBox.information(None, "General Error", "Camera ["+Kamera+"] not found in calibration folder, exiting!")
                                    return

                                # log number of comments by producer
                                if (len(kommentar)>4):
                                    commentCount = commentCount + 1

                                # Check GSD
                                GSDpass = 'Not validated'
                                if self.dlg.checkBoxGSD.isChecked():
                                    try:
                                        Ele = float(feat['Height'])
                                        WantedGSD = float(self.dlg.lineEditGSD.text())
                                        calculatedGSD = ((float(Ele)*float(PIXEL_SIZE))/float(PRINCIPAL_DISTANCE)/1000)-0.01
                                        if WantedGSD<calculatedGSD:
                                            GSDpass = 'Failed'
                                            GSDfailCount = GSDfailCount + 1
                                        else:
                                            GSDpass = "OK"
                                    except (RuntimeError, TypeError, NameError, ValueError) as e:
                                        QMessageBox.information(None, "Gennerel Error","GSDFormat Error: \n" +  str(e))

                                #Check Sun Angle
                                SUNpass = 'Not validated'
                                solVinkelen = []
                                if (self.dlg.checkBoxSun.isChecked()):
                                    try:
                                        Zon = 32
                                        posX = feat['Easting']
                                        posY = feat['Northing']
                                        datotiden = feat['TimeUTC'].replace('T', ' ').replace('60', '59')

                                        lati = SubScripts.utmToLatLng(Zon, posX, posY, True)[0]
                                        longi = SubScripts.utmToLatLng(Zon, posX, posY, True)[1]

                                        solVinkelen = SubScripts.sunAngle(datotiden, lati, longi)
                                        WantedSUN = float(self.dlg.lineEditSUN.text())

                                        if (solVinkelen < WantedSUN):
                                            SUNpass = 'Failed'
                                            SUNfailCount = SUNfailCount + 1
                                        else:
                                            SUNpass = 'OK'
                                    except (RuntimeError, TypeError, NameError, ValueError) as e:
                                        QMessageBox.information(None, "General Error","SunAngleFormat Error: \n" + str(e))
                                        return

                                #Check Overlap  -- feature pending --
                                #if (self.dlg.checkBoxOverlap.isChecked()):
                                    #doo something
                                #    OLAPfailCount = 0

                                #check name format
                                NameFormat = 'Not Checked'
                                Orientation = ''
                                if (self.dlg.checkBoxFormat.isChecked()):
                                    try:
                                        kappa = feat['Kappa']
                                        Time1 = feat['TimeUTC']
                                        Time2 = feat['TimeCET']
                                        ImageID = feat['ImageID']
                                        camid = feat['CameraID']
                                        if self.dlg.radioButtonPPC_Nadir.isChecked():
                                            kk='0'
                                        elif self.dlg.radioButtonPPC_ob.isChecked():
                                            kk='1'
                                        if self.dlg.checkBoxPic.isChecked():
                                            # check image ID format
                                            NameFormat1, FeatIIDFailCount = SubScripts.format3(kk,ImageID)
                                        else:
                                            NameFormat1 = '  ImageID-not checked  '

                                        #Check timestamp format
                                        NameFormat2,FeatTimeFailCount = SubScripts.format4(Time1,Time2)

                                        #Check footprint/ppc cameraID matches cameraID from cam-file
                                        NameFormat3, FeatCamFailCount = SubScripts.format5(camid,CAM_ID)

                                        #Check if there has been more than 5 i-a-row of kappa's ending with a zero (as these might be truncated)
                                        if kappacount > 5:
                                            fiveinarow = 1
                                        else: pass

                                        #Check Kappa values format
                                        NameFormat4, kappacount = SubScripts.format6(kappa)
                                    except (RuntimeError, TypeError, NameError, ValueError) as e:
                                        QMessageBox.information(None, "General Error", "KappaFormat Error: \n" +  str(e))
                                        return
                                    FeatFailCount = FeatIIDFailCount + FeatTimeFailCount + FeatCamFailCount
                                    NameFormat = NameFormat1 + NameFormat2 + NameFormat3
                                    Orientation = NameFormat4

                                #Check Reference system
                                REFpass = 'Not validated'
                                if (self.dlg.checkBoxRef.isChecked()):
                                    try:
                                        RefS = feat['ReferenceS']
                                        WantedREF1 = self.dlg.lineEditRef.text()
                                        REFpass,REFfailCount = SubScripts.refs(RefS,WantedREF1)

                                    except (RuntimeError, TypeError, NameError, ValueError) as e:
                                        QMessageBox.information(None, "General Error", "ReferenceSystemFormat Error: \n" +str(e))
                                        return

                                    # Check Tilt angles
                                    TILTpass = 'Not validated'
                                    if (self.dlg.checkBoxTilt.isChecked()):
                                        Omega = feat['Omega']
                                        Phi = feat['Phi']
                                        MaxAcceptedTilt = float(self.dlg.lineEditTilt.text())
                                        Level = int(feat['Level'])
                                        try:
                                            if (self.dlg.radioButtonPPC_ob.isChecked()):
                                                Dir = str(feat['Direction'])
                                                if Dir == "T":
                                                    TILTpass, TILTfailCount = SubScripts.tilt(Omega, Phi, MaxAcceptedTilt, Level)
                                                else:
                                                    pass
                                            elif (self.dlg.radioButtonPPC_Nadir.isChecked()):
                                                TILTpass, TILTfailCount = SubScripts.tilt(Omega, Phi, MaxAcceptedTilt, Level)
                                        except (RuntimeError, TypeError, NameError, ValueError) as e:
                                            QMessageBox.information(None, "General Error", "TiltFormat Error: \n" + str(e))

                                    # Check for voids
                                    if (self.dlg.checkBoxVoids.isChecked()):
                                        if self.dlg.radioButtonPPC_Nadir.isChecked():
                                            QMessageBox.information(None, "General Error", "Void-check option is only for Oblique!")
                                            break
                                        elif self.dlg.radioButtonPPC_ob.isChecked():
                                            try:
                                                SubScripts.void(nn,cc,inputLayer)
                                            except(RuntimeError, TypeError, NameError, ValueError) as e:
                                                QMessageBox.information(None, "General Error", "VoidCheck Error: \n" + str(e))

                                # add a feature
                                newfeat = QgsFeature()
                                newfeat.setGeometry(QgsGeometry.fromPoint(Geometri))
                                try:
                                    newfeat.setAttributes([ImageID,GSDpass,SUNpass,solVinkelen,'Feature pending',TILTpass,REFpass,NameFormat,kappa])
                                except (RuntimeError, TypeError, NameError, ValueError) as e:
                                    QMessageBox.information(None, "General Error", "General Format errors found, exiting!: \n" + str(e))
                                pr.addFeatures([newfeat])

                            # update layer's extent when new features have been added
                            # because change of extent in provider is not propagated to the layer
                            vl.updateExtents()
                            vl.updateFields()
                            QgsMapLayerRegistry.instance().addMapLayer(vl)

                            #Compile report over all the checks
                            rapporten = "Check of: \n" + inputFilNavn + "\n \nThere was found: \n"
                            if (self.dlg.checkBoxGSD.isChecked()):
                                rapporten = rapporten + str(GSDfailCount) + " GSD errors, \n"
                            else:
                                rapporten = rapporten + "GSD not checked \n"

                            if (self.dlg.checkBoxSun.isChecked()):
                                rapporten = rapporten + str(SUNfailCount) + " sun angle errors \n"
                            else:
                                rapporten = rapporten + "sun angle not checked \n"

                            # if (self.dlg.checkBoxOverlap.isChecked()):
                            #    rapporten = rapporten + "overlap check not available \n"
                            # else:
                            #    rapporten = rapporten + "overlap check not available \n"

                            if (self.dlg.checkBoxTilt.isChecked()):
                                rapporten = rapporten + str(TILTfailCount) + " tilt angle errors \n"
                            else:
                                rapporten = rapporten + "tilt angle not checked \n"

                            if (self.dlg.checkBoxRef.isChecked()):
                                rapporten = rapporten + str(REFfailCount) + " reference errors \n"
                            else:
                                rapporten = rapporten + "reference system not checked \n"

                            if (self.dlg.checkBoxFormat.isChecked()):
                                rapporten = rapporten + str(FeatFailCount) + " name format errors \n"
                            else:
                                rapporten = rapporten + "name format not checked \n"

                            if (self.dlg.checkBoxFormat.isChecked()):
                                if fiveinarow == 1:
                                    rapporten = rapporten + str(FeatOrientationFail) + " suspect orientation formats \n OBS - 5 suspect kappa formats in a row \n"
                                else:
                                    rapporten = rapporten + str(FeatOrientationFail) + " suspect orientation formats \n"
                            else:
                                rapporten = rapporten + "name format not checked \n"

                            rapporten = rapporten + str(commentCount) + " comments from " + producent

                            if GSDfailCount + SUNfailCount + TILTfailCount + REFfailCount + FeatFailCount == 0:
                                QMessageBox.information(self.iface.mainWindow(), 'PPC check', rapporten)
                            else:
                                QMessageBox.critical(self.iface.mainWindow(), 'PPC check', rapporten)
                            self.dlg.close()
                            return
                except (RuntimeError, TypeError, NameError):  # , ValueError): #
                    QMessageBox.information(None, "General Error", "General file error, please check that you have choosen the correct PPC file")

            elif str(currentIndex) == "2":
                inputFilNavn = self.dlg.inShapeDB.currentText()
                canvas = self.iface.mapCanvas()
                allLayers = canvas.layers()

                for i in allLayers:
                    if (i.name() == inputFilNavn):
                        #QMessageBox.information(None, "status", i.name())
                        if self.dlg.useSelectedDB.isChecked():
                            select = 1
                        else:
                            select = 2
                        if self.dlg.OverwriteDB.isChecked():
                            overwritedata = 1
                        else:
                            overwritedata = 2
                        if self.dlg.radioButtonDB_ob.isChecked():
                            file = open(os.path.dirname(__file__) + "\\subscripts\\" + "DBinfo.txt", "w")
                            file.write(self.dlg.db_name.text())
                            file.write('\n')
                            file.write(self.dlg.db_host.text())
                            file.write('\n')
                            file.write(self.dlg.db_port.text())
                            file.write('\n')
                            file.write(self.dlg.db_user.text())
                            file.write('\n')
                            file.write(self.dlg.db_password.text())
                            file.write('\n')
                            file.write(str(overwritedata))
                            file.write('\n')
                            file.write(str(select))
                            file.write('\n')
                            file.write(str(i.name()))
                            file.write('\n')
                            file.write(self.DB_footprint)
                            file.close()
                            self.window = MyAppII()
                            self.window.show()
                        elif self.dlg.radioButtonDB_Nadir.isChecked():
                            file = open(os.path.dirname(__file__) + "\\subscripts\\" + "DBinfo.txt", "w")
                            file.write(self.dlg.db_name.text())
                            file.write('\n')
                            file.write(self.dlg.db_host.text())
                            file.write('\n')
                            file.write(self.dlg.db_port.text())
                            file.write('\n')
                            file.write(self.dlg.db_user.text())
                            file.write('\n')
                            file.write(self.dlg.db_password.text())
                            file.write('\n')
                            file.write(str(overwritedata))
                            file.write('\n')
                            file.write(str(select))
                            file.write('\n')
                            file.write(str(i.name()))
                            file.write('\n')
                            file.write(self.DB_ppc)
                            file.close()
                            self.window = MyAppII()
                            self.window.show()

            elif str(currentIndex) == "3":
                path = self.dlg.lineEditImageDir.text()
                drevnavn = FindUSBname.getusbname(os.path.splitdrive(path)[0])
                if self.dlg.useSelectedDB_2.isChecked():
                    select = 1
                else:
                    select = 2
                if self.dlg.OverwriteDB_2.isChecked():
                    overwritedata = 1
                else:
                    overwritedata = 2
                if self.dlg.radioButtonDB_ob_2.isChecked():
                    file = open(os.path.dirname(__file__) + "\\subscripts\\" + "DBinfo2.txt", "w")
                    file.write(str(overwritedata))
                    file.write('\n')
                    file.write(str(select))
                    file.write('\n')
                    file.write(str(path))
                    file.write('\n')
                    file.write(str(drevnavn))
                    file.write('\n')
                    file.write(self.DB_footprint)
                    file.close()
                    self.window = MyAppIII()
                    self.window.show()
                elif self.dlg.radioButtonDB_Nadir_2.isChecked():
                    file = open(os.path.dirname(__file__) + "\\subscripts\\" + "DBinfo2.txt", "w")
                    file.write(str(overwritedata))
                    file.write('\n')
                    file.write(str(select))
                    file.write('\n')
                    file.write(str(path))
                    file.write('\n')
                    file.write(str(drevnavn))
                    file.write('\n')
                    file.write(self.DB_ppc)
                    file.close()
                    self.window = MyAppIII()
                    self.window.show()

            elif str(currentIndex) == "4":
                try:
                    import subprocess
                    inputLayer = unicode(self.dlg.inShapeAImage.currentText())
                    ImageDirPath = str(self.dlg.lineEditDBImageDir.text())
                    ImageDirPath = ImageDirPath.replace("\\", "/")
                    inputFilNavn = self.dlg.inShapeAImage.currentText()
                    basename=[]
                    ImageID = []
                    ImageNames = []

                    if self.dlg.radioButtonDBQC_ob.isChecked():
                        for dirpath, dirnames, filenames in os.walk(ImageDirPath):
                            for filename in [f for f in filenames if f.endswith(".jpg")]:
                                ImageNames.append(filename)
                            for filename in [f for f in filenames if f.endswith(".tif")]:
                                ImageNames.append(filename)
                    elif self.dlg.radioButtonDBQC_Nadir.isChecked():
                        ImageNames = glob.glob(ImageDirPath +"\\*.jpg")
                        if not ImageNames:
                            ImageNames = glob.glob(ImageDirPath+"\\*.tif")

                    for i in ImageNames:
                        name = os.path.basename(os.path.normpath(i))
                        basename.append(os.path.splitext(os.path.normpath(i))[0])
                        if self.dlg.radioButtonDBQC_ob.isChecked():
                            ImageID.append(name[0:26])
                        elif self.dlg.radioButtonDBQC_Nadir.isChecked():
                            ImageID.append(name[0:18])

                    blok = ImageID[0][5:10]

                    for i in ImageID:
                        print i

                    # Herunder skabes link til database
                    DB_name = self.dlg.db_name_2.text()
                    DB_host = self.dlg.db_host_2.text()
                    DB_port = self.dlg.db_port_2.text()
                    DB_user = self.dlg.db_user_2.text()
                    DB_pass = self.dlg.db_password_2.text()
                    # Herunder opsttes tabellen der skal bruges. Findes tabellen ikke allerede opretts den
                    DB_schema = self.DBschema
                    if self.dlg.radioButtonDBQC_ob.isChecked():
                        DB_table = self.DB_footprint
                    elif self.dlg.radioButtonDBQC_Nadir.isChecked():
                        DB_table = self.DB_ppc

                    conn = psycopg2.connect("dbname=" + DB_name + " user=" + DB_user + " host=" + DB_host + " password=" + DB_pass)
                    cur = conn.cursor()

                    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (DB_table,))
                    if cur.fetchone()[0]:
                        QMessageBox.information(None, "General Info", 'Database: ' + DB_table + ' found \n Checking...')
                    else:
                        QMessageBox.information(None, "General Info", 'Database: ' + DB_table + ' not found ')

                    foundcount = 0
                    notfoundcount = 0

                    for names in ImageID:
                        cur.execute("select exists(select from " + DB_schema + '.' + DB_table + " where imageID=%s)", (names,))
                        if cur.fetchone()[0]:
                            foundcount += 1
                        else:
                            notfoundcount += 1

                    cur.execute('SELECT * from ' + DB_schema + '.' + DB_table + ' WHERE imageid LIKE ' + '\'%' + blok + '%\'')
                    rows = cur.fetchall()
                    PPCFPcount = len(rows)
                    noPPCFPcount = PPCFPcount - foundcount

                except Exception, e:
                    QMessageBox.information(None, "General Info", 'ERROR:', e[0])

                if self.dlg.radioButtonDBQC_ob.isChecked():
                    rapportenI = "Check of: \n" + ImageDirPath + "\n " + 'Against blok \'' + blok + '\' footprints in DB' + "\n \nThere was found: \n" + str(notfoundcount) + " Images without associated Footprint \n"
                    rapportenI = rapportenI + str(noPPCFPcount) + " Footprints without associated Image \n \n Images:\n" + str(foundcount) + " of " + str(len(basename)) + " - OK\n"
                    rapportenI = rapportenI + str(notfoundcount) + " of " + str(len(basename)) + " - Fail"
                    if notfoundcount + noPPCFPcount == 0:
                        QMessageBox.information(self.iface.mainWindow(), 'PPC check', rapportenI)
                    else:
                        QMessageBox.critical(self.iface.mainWindow(), 'PPC check', rapportenI)
                elif self.dlg.radioButtonDBQC_Nadir.isChecked():
                    rapportenI = "Check of: \n" + ImageDirPath + "\n " + 'Against blok \'' + blok + '\' PPCs in DB' + "\n \nThere was found: \n" + str(notfoundcount) + " Images without associated PPC \n"
                    rapportenI = rapportenI + str(noPPCFPcount) + " PPCs without associated Image \n \n Images:\n" + str(foundcount) + " of " + str(len(basename)) + " - OK\n"
                    rapportenI = rapportenI + str(notfoundcount) + " of " + str(len(basename)) + " - Fail"
                    if notfoundcount + noPPCFPcount == 0:
                        QMessageBox.information(self.iface.mainWindow(), 'PPC check', rapportenI)
                    else:
                        QMessageBox.critical(self.iface.mainWindow(), 'PPC check', rapportenI)