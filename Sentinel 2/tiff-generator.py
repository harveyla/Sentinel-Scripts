import sys
import subprocess
#sys.path.append('Scripts/')
import Scripts.gdal_merge as gdal_merge
import zipfile
import os
import time
from pyreadline import Readline
import glob
from pathlib import Path

os.environ['PROJ_LIB'] += '\proj'

readline = Readline()

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def generate_geotiffs(inputProductPath, outputPath):

    basename =  os.path.basename(inputProductPath)
    if os.path.isdir(outputPath + basename[:-3] + "SAFE") :
        print('Already extracted')
    else:
        zip = zipfile.ZipFile(inputProductPath)
        zip.extractall(outputPath)
        print("Extracting Done")


    directoryName = outputPath + basename[:-3] + "SAFE/GRANULE"

    productName = os.path.basename(inputProductPath)[:-4]
    outputPathSubdirectory = outputPath + productName + "_PROCESSED"

    if not os.path.exists(outputPathSubdirectory):
        os.makedirs(outputPathSubdirectory)

    subDirectorys = get_immediate_subdirectories(directoryName)

    results = []

    for granule in subDirectorys:
        unprocessedBandPath = outputPath + productName + ".SAFE/GRANULE/" + granule + "/" + "IMG_DATA/"
        #print(unprocessedBandPath)
        results.append(generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory))

    #gdal_merge.py -n 0 -a_nodata 0 -of GTiff -o /home/daire/Desktop/merged.tif /home/daire/Desktop/aa.tif /home/daire/Desktop/rgbTiff-16Bit-AllBands.tif
    merged = outputPathSubdirectory + "/merged.tif"
    params = ['',"-of", "GTiff", "-o", merged]

    for granule in results:
        params.append(granule)

    gdal_merge.main(params)


def generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory):

    granuleBandTemplate =  granule[:-6]
    granpart_1 = unprocessedBandPath.split(".SAFE")[0][-22:-16]
    granule_2 = unprocessedBandPath.split(".SAFE")[0][-49:-34]

    granuleBandTemplate = granpart_1 + "_" + granule_2 + "_"
    #sys.exit()

    outputPathSubdirectory = outputPathSubdirectory
    if not os.path.exists(outputPathSubdirectory+ "/IMAGE_DATA"):
        os.makedirs(outputPathSubdirectory+ "/IMAGE_DATA")

    outPutTiff = '/'+granule[:-6]+'16Bit-AllBands.tif'
    outPutVRT = '/'+granule[:-6]+'16Bit-AllBands.vrt'

    outPutFullPath = outputPathSubdirectory + "/IMAGE_DATA/" + outPutTiff
    outPutFullVrt = outputPathSubdirectory + "/IMAGE_DATA/" + outPutVRT
    inputPath = unprocessedBandPath #+ granuleBandTemplate

    #print("\n\t" + inputPath)

    # bands = {"band_AOT" :  inputPath + "R10m/" + granuleBandTemplate +  "AOT_10m.jp2",
    # "band_02" :  inputPath + "R10m/" + granuleBandTemplate +  "B02_10m.jp2",
    # "band_03" :  inputPath + "R10m/" + granuleBandTemplate +  "B03_10m.jp2",
    # "band_04" :  inputPath + "R10m/" + granuleBandTemplate +  "B04_10m.jp2",
    # "band_05" :  inputPath + "R20m/" + granuleBandTemplate +  "B05_20m.jp2",
    # "band_06" :  inputPath + "R20m/" + granuleBandTemplate +  "B06_20m.jp2",
    # "band_07" :  inputPath + "R20m/" + granuleBandTemplate +  "B07_20m.jp2",
    # "band_08" :  inputPath + "R10m/" + granuleBandTemplate +  "B08_10m.jp2",
    # "band_8A" :  inputPath + "R20m/" + granuleBandTemplate +  "B8A_20m.jp2",
    # "band_09" :  inputPath + "R60m/" + granuleBandTemplate +  "B09_60m.jp2",
    # "band_WVP" :  inputPath + "R10m/" + granuleBandTemplate +  "WVP_10m.jp2",
    # "band_11" :  inputPath + "R20m/" + granuleBandTemplate +  "B11_20m.jp2",
    # "band_12" :  inputPath + "R20m/" + granuleBandTemplate +  "B12_20m.jp2"}

    # 1C product
    bands = {"band_01" :  inputPath + granuleBandTemplate +  "B01.jp2",
    "band_02" :  inputPath + granuleBandTemplate +  "B02.jp2",
    "band_03" :  inputPath + granuleBandTemplate +  "B03.jp2",
    "band_04" :  inputPath + granuleBandTemplate +  "B04.jp2",
    "band_05" :  inputPath + granuleBandTemplate +  "B05.jp2",
    "band_06" :  inputPath + granuleBandTemplate +  "B06.jp2",
    "band_07" :  inputPath + granuleBandTemplate +  "B07.jp2",
    "band_08" :  inputPath + granuleBandTemplate +  "B08.jp2",
    "band_8A" :  inputPath + granuleBandTemplate +  "B8A.jp2",
    "band_09" :  inputPath + granuleBandTemplate +  "B09.jp2",
    "band_10" :  inputPath + granuleBandTemplate +  "B10.jp2",
    "band_11" :  inputPath + granuleBandTemplate +  "B11.jp2",
    "band_12" :  inputPath + granuleBandTemplate +  "B12.jp2"}

    # 10m resolution and bilinear resampling method
    cmd = ['gdalbuildvrt', '-resolution', 'user', '-tr' ,'10', '10', '-separate', '-r', 'bilinear' ,outPutFullVrt]

    for band in sorted(bands.values()):
        cmd.append(band)

    my_file = Path(outPutFullVrt)
    if not my_file.is_file():
        # file exists
        subprocess.call(cmd)

    #, '-a_srs', 'EPSG:3857'
    cmd = ['gdal_translate', '-of' ,'GTiff', outPutFullVrt, outPutFullPath]

    my_file = Path(outPutTiff)
    if not my_file.is_file():
        # file exists
        subprocess.call(cmd)

    #params = ['', '-o', outPutFullPath, '-separate', band_01, band_02, band_03, band_04, band_05, band_06, band_07, band_08, band_8A, band_09, band_10, band_11, band_12]

    #gdal_merge.main(params)

    return(outPutFullPath)

#outputPath = '../Output/'
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)
inputPath = sys.argv[1]
outputPath = sys.argv[2]
# inputPath = input("Input Path? ")

start_time = time.time()

generate_geotiffs(inputPath, outputPath)

print("--- %s seconds ---" % (time.time() - start_time))
