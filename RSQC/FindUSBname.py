#import pythoncom
import win32com.client as client

#pythoncom.CoInitialize()

def getusbname(driveletter):
    DiskDrive_DeviceID = []
    DiskDrive_Caption = []
    DiskPartition_DeviceID = []
    LogicalDisk_DeviceID =[]
    drivename = 'local folder'

    strComputer = "."
    objWMIService = client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

    # 1. Win32_DiskDrive
    colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_DiskDrive WHERE InterfaceType = \"USB\"")
    for i in range(0,len(colItems)):
        DiskDrive_DeviceID.append(colItems[i].DeviceID.replace('\\', '').replace('.', ''))
        DiskDrive_Caption.append(colItems[i].Caption)

    # 2. Win32_DiskDriveToDiskPartition
    colItems = objSWbemServices.ExecQuery("SELECT * from Win32_DiskDriveToDiskPartition")
    for objItem in colItems:
        for i in range(0,len(DiskDrive_DeviceID)):
            if DiskDrive_DeviceID[i] in str(objItem.Antecedent):
                DiskPartition_DeviceID.append(objItem.Dependent.split('=')[1].replace('"', ''))

    # 3. Win32_LogicalDiskToPartition
    colItems = objSWbemServices.ExecQuery("SELECT * from Win32_LogicalDiskToPartition")
    for objItem in colItems:
        for i in range(0,len(DiskPartition_DeviceID)):
            if DiskPartition_DeviceID[i] in str(objItem.Antecedent):
                LogicalDisk_DeviceID.append(objItem.Dependent.split('=')[1].replace('"', ''))

    # 4. Win32_LogicalDisk
    for i in range(0,len(LogicalDisk_DeviceID)):
        colItems = objSWbemServices.ExecQuery("SELECT * from Win32_LogicalDisk WHERE DeviceID=\"" + LogicalDisk_DeviceID[i] + "\"")
        #print 'LogicalDisk ', i, ' VolumeName:', colItems[0].VolumeName, '(' + LogicalDisk_DeviceID[i] + ')'
        if str(LogicalDisk_DeviceID[i]) == driveletter:
            drivename = colItems[0].VolumeName

    return drivename

#print getusbname('D:')