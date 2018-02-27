# -*- coding: utf-8 -*-
import qgis
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
import psycopg2
from qgis.utils import iface
from processing.core.Processing import Processing
from processing.tools import *
#sys.path.insert(0, 'C:/Users/b020736/.qgis2/python/plugins/RSQC')
#from RemoteSensing_QualityControl_dialog import RSQCDialogII
#import RemoteSensing_QualityControl
import os,re,hashlib,datetime





def readCameras(self, camdir):
    caminfo = []
    for camfile in os.listdir(camdir):
        if camfile.endswith(".cam"):
            with open(camdir + '\\' + camfile) as openfileobject:
                try:
                    for line in openfileobject:
                        SplitLine = line.split(" ")
                        if SplitLine[0] == "CAM_ID:":
                            CAM_ID = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "PIXEL_SIZE:":
                            PIXEL_SIZE = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "PRINCIPAL_DISTANCE:":
                            PRINCIPAL_DISTANCE = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "PRINCIPAL_POINT_X:":
                            PRINCIPAL_POINT_X = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "PRINCIPAL_POINT_Y:":
                            PRINCIPAL_POINT_Y = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "SENSOR_AREA_WIDTH:":
                            SENSOR_AREA_WIDTH = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "SENSOR_AREA_WIDTH_PIX:":
                            SENSOR_AREA_WIDTH = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "SENSOR_AREA_HEIGHT:":
                            SENSOR_AREA_HEIGHT = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "SENSOR_AREA_HEIGHT_PIX:":
                            SENSOR_AREA_HEIGHT = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "ROTATION:":
                            ROTATION = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "CALIBRATIONDATE:":
                            CALIBRATIONDATE = SplitLine[1].rstrip('\r\n')
                        elif SplitLine[0] == "OWNER:":
                            OWNER = SplitLine[1].rstrip('\r\n')
                except (RuntimeError, TypeError, NameError, IndexError):
                    self.dlg.setWindowFlags(self.dlg.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
                    QMessageBox.information(None, "General Error", "General runtime error - Check camfile: " + str(CAM_ID) + ".cam")
                    self.dlg.setWindowFlags(self.dlg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                    self.dlg.show()
                    return
            caminfo.append([CAM_ID, PIXEL_SIZE, PRINCIPAL_DISTANCE, PRINCIPAL_POINT_X, PRINCIPAL_POINT_Y, SENSOR_AREA_WIDTH, SENSOR_AREA_HEIGHT, ROTATION, CALIBRATIONDATE, OWNER])
        else:
            continue
    return caminfo


def sunAngle(datotiden, lati, longi):
    import math
    import datetime
    datotiden = datotiden.replace('-', ':')
    patterndatetime1 = re.compile("[0-9]{4}:[0-9]{2}:[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{0,3}")
    if patterndatetime1.match(datotiden):
        DateTime = datetime.datetime.strptime(datotiden, '%Y:%m:%d %H:%M:%S.%f')
    else:
        DateTime = datetime.datetime.strptime(datotiden, '%Y:%m:%d %H:%M:%S')

    dayOfYear = DateTime.timetuple().tm_yday
    hour = DateTime.hour
    mins = DateTime.minute
    sec = DateTime.second
    timeZone = 0

    gamma = (2 * math.pi / 365) * ((dayOfYear + 1) + (hour - 12) / 24)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma) - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma))
    declin = 0.006918 - (0.399912 * math.cos(gamma)) + 0.070257 * math.sin(gamma) - 0.006758 * math.cos(2 * gamma) + 0.000907 * math.sin(2 * gamma) - 0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma)
    tOffset = eqtime - 4 * longi + 60 * timeZone
    tst = hour * 60 + mins + sec / 60 + tOffset
    sh = (tst / 4) - 180
    zenit = math.degrees(math.acos(((math.sin(math.radians(lati)) * math.sin(declin)) + (math.cos(math.radians(lati)) * math.cos(declin) * math.cos(math.radians(sh))))))
    sunVinkel = 90 - zenit

    return sunVinkel

def utmToLatLng(zone, easting, northing, northernHemisphere=True):
        import math
        if not northernHemisphere:
            northing = 10000000 - northing

        a = 6378137
        e = 0.081819191
        e1sq = 0.006739497
        k0 = 0.9996

        arc = northing / k0
        mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))
        ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

        ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0
        cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
        cc = 151 * math.pow(ei, 3) / 96
        cd = 1097 * math.pow(ei, 4) / 512
        phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

        n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

        r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
        fact1 = n0 * math.tan(phi1) / r0

        _a1 = 500000 - easting
        dd0 = _a1 / (n0 * k0)
        fact2 = dd0 * dd0 / 2

        t0 = math.pow(math.tan(phi1), 2)
        Q0 = e1sq * math.pow(math.cos(phi1), 2)
        fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

        fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

        lof1 = _a1 / (n0 * k0)
        lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
        lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
        _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
        _a3 = _a2 * 180 / math.pi

        latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

        if not northernHemisphere:
            latitude = -latitude

        longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

        if (zone > 29):
            longitude = longitude * (-1)

        return (latitude, longitude)

def readsettings(settingsFile):
    with open(settingsFile) as openfileobject:
        for line in openfileobject:
            SplitLine = line.split(" ")
            if SplitLine[0] == "UserID:":
                UserID = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "Project:":
                Project = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "ProjectLog:":
                ProjectLog = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "MainLog:":
                MainLog = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "GSD:":
                PPC_GSD = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "Sun:":
                Sun = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "Tilt:":
                Tilt = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "CamCal:":
                CamCal = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "ImageDir:":
                ImageDir = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DBImageDir:":
                DBImageDir = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_n:":
                DBname = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_h:":
                DBhost = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_po:":
                DBport = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_u:":
                DBuser = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_pa:":
                DBpass = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_s:":
                DBsch = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_t:":
                DBtab = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_ob:":
                DB_ob = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_nadir:":
                DB_nadir = SplitLine[1].rstrip('\r\n')
    return (ProjectLog, MainLog, PPC_GSD, Sun, Tilt, CamCal, ImageDir, DBImageDir, DBname, DBhost, DBport, DBuser, DBpass, DBsch, DBtab, DB_ob, DB_nadir)

def readsettings1(settingsFile):
    with open(settingsFile) as openfileobject:
        for line in openfileobject:
            SplitLine = line.split(" ")
            if SplitLine[0] == "DB_n:":
                DBname1 = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_h:":
                DBhost1 = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_po:":
                DBport1 = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_u:":
                DBuser1 = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_pa:":
                DBpass1 = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_s:":
                DBschema1 = SplitLine[1].rstrip('\r\n')
            elif SplitLine[0] == "DB_t:":
                DBtable1 = SplitLine[1].rstrip('\r\n')
    return (DBname1, DBhost1, DBport1, DBuser1, DBpass1, DBschema1, DBtable1)

def format1(self, layer):
    n = 0
    features = layer.getFeatures()
    f = features.next()
    AttributesList = [c.name() for c in f.fields().toList()]
    return AttributesList

def format2(self, PossibleValues, AttributesList):
    n = 0
    AttList =[]
    for s in AttributesList:
        AttList.append(s.lower())
    for s in PossibleValues:
        if s.lower() in AttList:
            n = n + 1
    ld1 = n
    ld2 = len(AttributesList)
    return ld1, ld2

def format3(kk,ImageID):
    FeatIIDFailCount = 0
    #GeoDK
    if kk == '0':
        patternImageID = re.compile("\w{0,1}[0-9]{4}_[0-9]{2}_[0-9]{2}_\d+_[0-9]{4}")
    #Oblique
    elif kk == '1':
        patternImageID = re.compile("[0-9]{4}_[0-9]{2}_[0-9]{2}_\d+_[0-9]{4}_[0-9]{8}")

    if patternImageID.match(ImageID):
        NameFormat1 = '  ImageID-OK  '
    else:
        FeatIIDFailCount = FeatIIDFailCount + 1
        NameFormat1 = '  ImageID-Fail  '
    return NameFormat1, FeatIIDFailCount

def format4(Time1, Time2):
    FeatTimeFailCount = 0
    patternTime = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.{0,1}[0-9]{0,3}")
    if patternTime.match(str(Time1)):
        if patternTime.match(str(Time2)):
            NameFormat2 = '  TimeCET,TimeUTC-OK  '
        else:
            FeatTimeFailCount = FeatTimeFailCount + 1
            NameFormat2 = '  TimeCET-Fail,TimeUTC-OK  '
    else:
        if patternTime.match(Time2):
            FeatTimeFailCount = FeatTimeFailCount + 1
            NameFormat2 = '  TimeCET-OK,TimeUTC-Fail  '
        else:
            FeatTimeFailCount = FeatTimeFailCount + 2
            NameFormat2 = '  TimeCET,TimeUTC-Fail  '
    return NameFormat2, FeatTimeFailCount

def format5(camid,CAM_ID):
    FeatCamFailCount = 0
    if CAM_ID == camid:
        NameFormat3 = '  CameraID-OK  '
    else:
        FeatCamFailCount = FeatCamFailCount + 1
        NameFormat3 = '  CameraID-Fail  '
    return NameFormat3, FeatCamFailCount

def format6(kappa):
    FeatOrientationFail = 0
    kappacount = 0
    patternKappa = re.compile("-?[\d]+.[0-9]{3}[0]")
    if ((str(kappa) == "NULL") or (str(kappa) == "")):
        NameFormat4 = ' '
        kappacount = 0
        pass
    elif len(str(kappa)) >= 9:
        kappa = "%.4f" % float(kappa)
        if patternKappa.match(kappa):
            FeatOrientationFail = FeatOrientationFail + 1
            kappacount = kappacount + 1
            NameFormat4 = '  Kappa - suspicious length:  '
        else:
            NameFormat4 = 'Kappa '
            kappacount = 0
    else:
        kappa = "%.4f" % float(kappa)
        if patternKappa.match(kappa):
            FeatOrientationFail = FeatOrientationFail + 1
            kappacount = kappacount + 1
            NameFormat4 = '  Kappa - maybe truncated:  '
        else:
            NameFormat4 = 'Kappa '
            kappacount = 0
    return NameFormat4,kappacount

def refs(RefS,WantedREF1):
    REFfailCount = 0
    if (RefS != WantedREF1):
        REFpass = 'Failed'
        REFfailCount = REFfailCount + 1
    else:
        REFpass = 'OK'
    return REFpass, REFfailCount

def tilt(Omega, Phi, MaxAcceptedTilt, Level):
    TILTfailCount = 0
    if ((str(Omega) == "NULL") or (str(Phi) == "NULL")):
        TILTpass = 'no info'
        if (Level > 1):
            TILTfailCount = TILTfailCount + 1
    elif ((Omega > MaxAcceptedTilt) or (Phi > MaxAcceptedTilt)):
        TILTpass = 'Failed'
        TILTfailCount = TILTfailCount + 1
    else:
        TILTpass = 'Nadir - OK'
    return TILTpass, TILTfailCount

def void(nn,cc,inputLayer):
    if nn == cc:
        fname = inputLayer
        localpath = os.getcwd()
        if os.path.exists(localpath + '\\dissolved_lyr.shp'):
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(lyr1)
            except:
                pass
            QgsVectorFileWriter.deleteShapeFile(localpath + '\\dissolved_lyr.shp')
        if os.path.exists(localpath + '\\err_lyr.shp'):
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(err_layer)
            except:
                pass
            QgsVectorFileWriter.deleteShapeFile(localpath + '\\err_lyr.shp')

        lyr = QgsVectorLayer(fname, 'Footprints', 'ogr')
        general.runalg("qgis:dissolve", lyr, "False", "Direction",localpath + '\\dissolved_lyr.shp')
        lyr1 = QgsVectorLayer(localpath + '\\dissolved_lyr.shp', 'dissolved_layer', 'ogr')
        landuse = {"N": ("yellow", "North"), "S": ("darkcyan", "South"),
                   "E": ("green", "East"),
                   "W": ("blue", "West"), "T": ("red", "Nadir")}

        categories = []
        for NSEW, (color, label) in landuse.items():
            sym = QgsSymbolV2.defaultSymbol(lyr1.geometryType())
            sym.setColor(QColor(color))
            category = QgsRendererCategoryV2(NSEW, sym, label)
            categories.append(category)

        field = "Direction"
        renderer = QgsCategorizedSymbolRendererV2(field, categories)
        lyr1.setRendererV2(renderer)
        crs = lyr1.crs()
        crs.createFromId(25832)
        lyr1.setCrs(crs)
        QgsMapLayerRegistry.instance().addMapLayer(lyr1)
        #            crs = self.utils.iface.activeLayer().crs().authid()
        features = lyr1.getFeatures()
        layer1 = QgsVectorLayer('Polygon', 'poly1', "memory")
        layer2 = QgsVectorLayer('Polygon', 'poly2', "memory")
        pr1 = layer1.dataProvider()
        pr2 = layer2.dataProvider()
        poly1 = QgsFeature()
        poly2 = QgsFeature()
        #QgsMapLayerRegistry.instance().addMapLayers([layer1])
        #QgsMapLayerRegistry.instance().addMapLayers([layer2])

        for f in features:
            vertices = f.geometry().asPolygon()
            dir = f.attribute("Direction")
            n = len(vertices)
            if n == 2:
                poly1.setGeometry(QgsGeometry.fromPolygon([vertices[0]]))
                poly2.setGeometry(QgsGeometry.fromPolygon([vertices[1]]))
                pr1.addFeatures([poly1])
                pr2.addFeatures([poly2])
                layer1.updateExtents()
                layer2.updateExtents()
                QgsMapLayerRegistry.instance().addMapLayers([layer2])

        general.runalg('qgis:addfieldtoattributestable', layer2, 'Direction', 2, 10, 7,'err_lyr.shp')
        err_layer = QgsVectorLayer(localpath + '\\err_lyr.shp', 'Error_layer', 'ogr')
        # --------------------------------------------------------------------------
        # only applicable for test case footprint file should be in crs 25832
        # crs = err_layer.crs()
        # crs.createFromId(4326)
        # err_layer.setCrs(crs)
        # --------------------------------------------------------------------------
        QgsMapLayerRegistry.instance().addMapLayers([err_layer])
        QgsMapLayerRegistry.instance().removeMapLayer(layer2)

        num = 0
        features = lyr1.getFeatures()
        for f in features:
            vertices = f.geometry().asPolygon()
            dir = f.attribute("Direction")
            n = len(vertices)
            if n == 2:
                num = num + 1
                # print dir,n,num
                err_layer.startEditing()
                err_layer.changeAttributeValue((num - 1), 0, dir)
                err_layer.commitChanges()
        rapp = "<center>Check Complete:<center>\n" + "\n Errors, if there are any, are in the \"Error_layer\"\n with their layer orientation in the attribute table\n"
        QMessageBox.information(None, 'Footprint_Void_Check', str(rapp))

def DB1(DB_name,DB_host,DB_port,DB_user,DB_pass,selection):
    DB_schema = "public"
    DB_geom = "geom"
    DB_table = 'footprint2017_test'

    # DB_table = 'oblique_2017_check_table'
    conn = psycopg2.connect("dbname=" + DB_name + " user=" + DB_user + " host=" + DB_host + " password=" + DB_pass)
    cur = conn.cursor()

    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (DB_table,))
    if cur.fetchone()[0]:
        pass
        #QMessageBox.information(None, "General Info", 'Database found - uploading')
    else:
        QMessageBox.information(None, "General Info", 'Creating database ' + DB_table)
        cur.execute(
            "CREATE TABLE " + DB_schema + "." + DB_table + "(imageid TEXT PRIMARY KEY, easting float, northing float, height real,omega real, phi real, kappa real, direction text, timeutc text, cameraid text, "
                                                           "coneid real, estacc real, height_eli text, timecet text, \"references\" text, producer text, level real, comment_co text, comment_gs text, status text, gsd text, geom geometry)")
        conn.commit()

    listofattrs = ['ImageID', 'Easting', 'Northing', 'Height', 'Omega', 'Phi', 'Kappa', 'Direction', 'TimeUTC',
                   'CameraID', 'ConeID', 'EstAcc', 'Height_Eli', 'TimeCET', 'ReferenceS', 'Producer', 'Level', 'Comment_co',
                   'Comment_GS', 'Status', 'GSD']
    obj = {}
    for n in listofattrs:
        obj[n] = []

    list = []
    for feat in selection:
        for i in obj.keys():
            obj[i].append(feat[i])
        geom = feat.geometry()
        Geometri = geom.asPolygon()
        list.append(Geometri)

    finallist = []
    for ll in list:
        finallist.append(str(ll).replace("[", "").replace("]", "").replace(",", " ").replace(")  (", "), (").replace("(", "").replace(")", ""))
    return finallist,obj

def DB3(DB_name,DB_host,DB_port,DB_user,DB_pass,selection,Imupload,insertcount,overwritedata):
    import psycopg2
    self.pgr.progressBar.setValue(self.completed)
    DB_table = 'footprint2017_test'
    conn = psycopg2.connect("dbname=" + DB_name + " user=" + DB_user + " host=" + DB_host + " password=" + DB_pass)
    cur = conn.cursor()
    if overwritedata == 1:
        pass
    elif overwritedata == 2:
        cur.execute("select exists(SELECT imageid FROM " + DB_table + " WHERE imageid = %s)", (obj['ImageID'][i],))
        #if cur.fetchone()[0] is False:

def md5(fname):
    hash_md5 = hashlib.md5()
    try:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        pass

def readtxt1():
    file1 = open(os.path.dirname(__file__) + "\\" + "dir.txt", "r")
    dirpath = file1.read()
    file1.close()
    os.remove(os.path.dirname(__file__) + "\\" + "dir.txt")
    file2 = open(os.path.dirname(__file__) + "\\" + "nextindex.txt", "r")
    nextdiskindex = file2.read()
    file2.close()
    os.remove(os.path.dirname(__file__) + "\\" + "nextindex.txt")
    return(dirpath,nextdiskindex)

def readtxt2():
    file1 = open(os.path.dirname(__file__) + "\\" + "DBinfo.txt", "r")
    DB_name = file1.readline()
    DB_name = DB_name.rstrip()
    DB_host = file1.readline()
    DB_host = DB_host.rstrip()
    DB_port = file1.readline()
    DB_port = DB_port.rstrip()
    DB_user = file1.readline()
    DB_user = DB_user.rstrip()
    DB_pass = file1.readline()
    DB_pass = DB_pass.rstrip()
    overwritedata = file1.readline()
    overwritedata = overwritedata.rstrip()
    select = file1.readline()
    select = select.rstrip()
    layer1 = file1.readline()
    layer1 = layer1.rstrip()
    DB_table = file1.readline()
    DB_table = DB_table.rstrip()
    file1.close()
    os.remove(os.path.dirname(__file__) + "\\" + "DBinfo.txt")
    return(DB_name, DB_host, DB_port, DB_user, DB_pass, overwritedata, select, layer1, DB_table)

def readtxt3():
    file1 = open(os.path.dirname(__file__) + "\\" + "DBinfo.txt", "r")
    DB_name = file1.read()
    file1.close()
    os.remove(os.path.dirname(__file__) + "\\" + "DBinfo.txt")
    return(DB_name)