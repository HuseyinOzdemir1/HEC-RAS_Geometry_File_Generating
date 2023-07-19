import fiona
import pandas as pd

nameofRiver = "River"

CrossSectionPath = r'Data\CROSS_SECTION.shp'
RiverLinePath = r'Data\RiverLine.shp'
stationElevation = pd.read_csv("Station_Elevation.csv")

stations = stationElevation["PVI Station"].to_list()

elevations = stationElevation["PVI Elevation"].to_list()

culvertSpan = 2
deckHeight = 0.5
total = culvertSpan + deckHeight
culvertThickness = 0.3
topWidth = 4
bankStationLength = 1
n = 0.02

culvertUpstream = culvertThickness + bankStationLength + topWidth/2
culvertDownstream = culvertThickness + bankStationLength + topWidth/2

def getCleanDict(cleanDict, index ):

    itemList = []

    for item in range(len(cleanDict[index])):
            
        cleanDict[index][item] = str(cleanDict[index][item]).replace("(","")
        cleanDict[index][item] = str(cleanDict[index][item]).replace(")","")
        cleanDict[index][item] = str(cleanDict[index][item]).replace(","," ")

        itemList.append(cleanDict[index][item].split())

    cleanDict[index] = itemList

    return cleanDict 

CrossSectionCoordinates = {}

with fiona.open(CrossSectionPath) as CrossSectionfile:

    for index, line in enumerate(CrossSectionfile):

        CrossSectionCoordinates[index] = line['geometry']['coordinates']

        getCleanDict(CrossSectionCoordinates, index)

RiverLineCoordinates = {}

with fiona.open(RiverLinePath) as RiverLinefile:

    for index, line in enumerate(RiverLinefile):

        RiverLineCoordinates[index] = line['geometry']['coordinates']

        getCleanDict(RiverLineCoordinates, index)

        RiverLineBounds = list(RiverLinefile.bounds)

with open(nameofRiver + ".g01","w") as f:
    
    countXS = 0
    
    text = "Geom Title=" + nameofRiver +"\n"
    f.write(text)

    text = "Program Version=6.31\n"
    f.write(text)

    text = "Viewing Rectangle={:12.2f},{:12.2f},{:12.2f},{:12.2f}\n" .format(float(RiverLineBounds[0]), float(RiverLineBounds[2]),
                                                        float(RiverLineBounds[1]+2500), float(RiverLineBounds[3])-2500)
    f.write(text)
    
    f.write("\n")

    text = "River Reach=" + nameofRiver + "," + nameofRiver + "\n"
    f.write(text)

    text = "Reach XY=" + str(len(RiverLineCoordinates[0])) + "\n"
    f.write(text)
    
    if len(RiverLineCoordinates[0]) %2 == 0:

        for index in range(0,len(RiverLineCoordinates[0]),2):

            text = "{:16.2f}{:16.2f}{:16.2f}{:16.2f}\n" .format(float(RiverLineCoordinates[0][index][0]), float(RiverLineCoordinates[0][index][1]),
                                                        float(RiverLineCoordinates[0][index + 1][0]), float(RiverLineCoordinates[0][index + 1][1]))
            f.write(text)
    else:

        for index in range(0,len(RiverLineCoordinates[0]),2):

            if index + 1 == len(RiverLineCoordinates[0]):

                text = "{:16.2f}{:16.2f}\n" .format(float( RiverLineCoordinates[0][index][0]), float(RiverLineCoordinates[0][index][1]))
                f.write(text)
            else:
                text = "{:16.2f}{:16.2f}{:16.2f}{:16.2f}\n" .format(float(RiverLineCoordinates[0][index][0]), float(RiverLineCoordinates[0][index][1]),
                                                        float(RiverLineCoordinates[0][index + 1][0]), float(RiverLineCoordinates[0][index + 1][1]))
                f.write(text)


    text = "Rch Text X Y={:12.2f},{:12.2f} \n".format(float(RiverLineBounds[0]),float(RiverLineBounds[1]))
    f.write(text)

    text = "Reverse River Text= 0 \n"
    f.write(text)

    f.write("\n")

    for i in range(len(stations)-1,0,-1):
        
        bwXS = stations[i] - stations[i-1]
        
        text = "Type RM Length L Ch R = 1 ,{:8.2f},{:7.2f},{:7.2f},{:7.2f}\n".format(stations[i],bwXS,bwXS,bwXS)
        f.write(text)
        
        text = "XS GIS Cut Line=3\n"
        f.write(text)

        text = "{:16.8f}{:16.8f}{:16.8f}{:16.8f}\n".format(float(CrossSectionCoordinates[countXS][0][0]),float(CrossSectionCoordinates[countXS][0][1]),
                                                           float(CrossSectionCoordinates[countXS][1][0]),float(CrossSectionCoordinates[countXS][1][1]))
        f.write(text)
        text = "{:16.8f}{:16.8f}\n".format(float(CrossSectionCoordinates[countXS][2][0]),float(CrossSectionCoordinates[countXS][2][1]))
        f.write(text)
        countXS += 1

        text = "Node Last Edited Time=Apr.28.2023 11:30:53\n"
        f.write(text)

        text = "#Sta/Elev= 6\n"
        f.write(text)

        high = total + elevations[i]
        low = elevations[i]
        stat = bankStationLength + 2 * culvertThickness + topWidth
        text = "{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}\n".format(0,high,bankStationLength,high,bankStationLength,low,stat,low,stat,high,stat + bankStationLength,high)
        f.write(text)

        text = "{:8.3f}{:8.3f}\n".format(stat + bankStationLength,high)
        f.write(text)

        text = "#Mann= 3 ,0,0\n"
        f.write(text)
        
        text = "{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}\n".format(0,n,0,bankStationLength,n,0,stat,n,0)
        f.write(text)
        
        text = "Bank Sta={:8.3f},{:8.3f}\n".format(bankStationLength, stat)
        f.write(text)

        text = "XS Rating Curve= 0 ,0\n"
        f.write(text)

        text = "XS HTab Starting El and Incr={:8.3f},0.14, 20\n".format(elevations[i])
        f.write(text)

        text = "XS HTab Horizontal Distribution= 5 , 5 , 5\n"
        f.write(text)

        text = "Exp/Cntr=0.3,0.1\n"
        f.write(text)

        f.write("\n")

        if (stations[i]-stations[i-1] > 0.11):

            text = "Type RM Length L Ch R = 2 ," + str(round(stations[i] - 0.01,3)) + "  ,,,\n"
            f.write(text)

            text = "Node Last Edited Time=Apr.28.2023 11:30:53\n"
            f.write(text)

            text = "Bridge Culvert--1,0,-1,-1, 0\n"
            f.write(text)

            text = "Deck Dist Width WeirC Skew NumUp NumDn MinLoCord MaxHiCord MaxSubmerge Is_Ogee\n"
            f.write(text)

            text = "0.01," + str(round(stations[i]-stations[i-1]-0.02,3)) + ",1.4,0, 2, 2, , , 0.98, 0, 0,0,,\n"
            f.write(text)

            text = "       0{:8.3f}\n".format(2*bankStationLength + 2*culvertThickness + topWidth)
            f.write(text)

            text = "{:8.3f}{:8.3f}\n".format(total + elevations[i],total + elevations[i])
            f.write(text)

            text = "{:8.3f}{:8.3f}\n".format(elevations[i],elevations[i])
            f.write(text)

            text = "       0{:8.3f}\n".format(2*bankStationLength + 2*culvertThickness + topWidth)
            f.write(text)

            text = "{:8.3f}{:8.3f}\n".format(total + elevations[i-1],total + elevations[i-1])
            f.write(text)

            text = "{:8.3f}{:8.3f}\n".format(elevations[i-1],elevations[i-1])
            f.write(text)

            text = "BR Coef=-1 , 0 , 0 ,, 0 ,,,0.8,-1,,0,\n"
            f.write(text)

            text = "WSPro=,,,, 1 ,,,, 0 ,,,, 0 ,,,,-1 ,-1 ,-1 , 0 , 0 , 0 , 0 , 0\n"
            f.write(text)

            text = "Culvert=2,{},{},{},0.02,0.2,0.5,57,1,{},{},{},{},Culvert #1  , 0 ,0.01\n".format(total - 0.5,topWidth,round(stations[i]-stations[i-1]-0.02,3),elevations[i],culvertUpstream,elevations[i-1],culvertDownstream)
            f.write(text)

            text = "{:8.3f}{:8.3f}\n".format(culvertUpstream,culvertDownstream)
            f.write(text)

            text = "BC Culvert Barrel=1,1,0\n"
            f.write(text)

            text = "Culvert Bottom n=0.02\n"
            f.write(text)

            text = "BC Design=,, 0 ,, 0 ,,,,,,\n"
            f.write(text)

            text = "BC Use User HTab Curves=0\n"
            f.write(text)

            text = "BC User HTab FreeFlow(D)= 0\n"
            f.write(text)

            f.write("\n")

    
    f.write("LCMann Time=Dec.30.1899 00:00:00\n")
    f.write("LCMann Region Time=Dec.30.1899 00:00:00\n")
    f.write("LCMann Table=0\n")
    f.write("Chan Stop Cuts=-1\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("Use User Specified Reach Order=0\n")
    f.write("GIS Units=Meters\n")
    f.write("GIS DTM Type=\n")
    f.write("GIS DTM=\n")
    f.write("GIS Stream Layer=\n")
    f.write("GIS Cross Section Layer=\n")
    f.write("GIS Map Projection=\n")
    f.write("GIS Projection Zone=\n")
    f.write("GIS Datum=\n")
    f.write("GIS Vertical Datum=\n")
    f.write("GIS Data Extents=,,,\n")
    f.write("\n")
    f.write("GIS Ratio Cuts To Invert=-1\n")
    f.write("GIS Limit At Bridges=0\n")
    f.write("Composite Channel Slope=5\n")
