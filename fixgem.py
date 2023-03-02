#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'David Rankin, davidrankin@email.arizona.edu'

'''
INFORMATION:
Python program for flattening out Gemini North images.
'''

from astropy.io import fits
import glob
import numpy as np
import argparse
import os
import datetime

helptext = ""
parser = argparse.ArgumentParser(description='gemfix', add_help=False)
parser.add_argument('-dir', type=str, required=True, help="The directory with the fits images.")
parser.add_argument('-prefix', type=str, required=True, help="The prefix of the fits images, any length")
args = parser.parse_args()

if not args.dir:
    print("Dir required")
    exit()
if not args.prefix:
    print("Prefix required")
    exit()

dir = args.dir
dirtemp = dir + 'FIXED'

fitsf = glob.glob(dir+args.prefix+"*.fits")

if len(fitsf) == 0:
    print("No fits images found. Exit")
    exit()

print("Processing ", len(fitsf), " fits files")

if not os.path.isdir(dirtemp):
    os.makedirs(dirtemp)

data = np.array([])
offset = 0.164 #SHUTTER DELAY OFFSET

for fn in fitsf:
    fnn = os.path.basename(fn)
    print('Processing ', fnn)
    with fits.open(fn) as hdul:

        #FIX HEADER KEYS. DATE-OBS IS TCS ENTRY OFF BY 2SEC. MUST USE UTSTART
        #UPDATE POSITION TO CHANNEL 6 POSITION
        RA = hdul[6].header["CRVAL1"]
        DEC = hdul[6].header["CRVAL2"]
        dateobs = hdul[0].header['DATE-OBS']
        uttime = hdul[0].header["UTSTART"]
        newdate = dateobs + ' ' + uttime

        datetimeobj = datetime_object = datetime.datetime.strptime(newdate, '%Y-%m-%d %H:%M:%S.%f')
        print(datetimeobj, " before offset")
        datetimeobj = datetimeobj - datetime.timedelta(seconds=offset)
        print(datetimeobj, " after offset")

        newdatestr = datetimeobj.strftime('%Y-%m-%d %H:%M:%S.%f')
        yrstr = newdatestr.split(' ')[0]
        timestr = newdatestr.split(' ')[1]

        #ASSEMBLE IMAGE ALONG WITH GAPS
        empty = np.zeros([2112, 32], dtype='int16')
        for i in range(len(hdul)):
            if i == 0:
                continue
            if i == 1:
                data = hdul[1].data[:, :-32]
                continue
            if (i % 2) == 0:
                # print(i, 'even')
                datat = hdul[i].data[:, 32:]
                data = np.concatenate((data, datat), axis=1)
            else:
                # print(i, 'odd')
                if i == 5 or i == 9:
                    data = np.concatenate((data, empty), axis=1)
                datat = hdul[i].data[:, :-32]
                data = np.concatenate((data, datat), axis=1)

        #CROP EMPTY DATA FROM WINGS, AND TOP BOTTOM A BIT
        data = data[100:-100, 450:-450]

        header = hdul[0].header

        #UPDATE HEADER VALUES
        header.set('RA', RA)
        header.set('DEC', DEC)
        header.set('DATE-OBS', yrstr)
        header.set('TIME-OBS', timestr)

        #WRITE OUT
        fits.writeto(dirtemp + "/" + "fixed-" + fnn, data, header, overwrite=True)

print("Images saved to ", dirtemp)