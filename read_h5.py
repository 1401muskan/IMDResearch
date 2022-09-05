#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 13:02:03 2022

@author: pywrk
"""
import sys
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt

def applyLUT(count, lut):
    count_flt = count.flatten();
    output = np.zeros_like(count_flt, dtype=lut.dtype)
    for indx in range(count_flt.shape[0]):        
        output[indx] = lut[count_flt[indx]]
    output = output.reshape(count.shape)
    return output;

def scaleDS(ds, ao, sf, fv):
    ds_flt = ds.flatten();
    output = np.zeros_like(ds_flt, dtype=sf.dtype)
    output = ds_flt*sf+ao
    output[ds_flt==fv]=-999.0

    output = output.reshape(ds.shape)
    return output
        
def dumpData(filename, out_dir):
    jobid = os.path.splitext(os.path.basename(filename))[0]

    out_path = out_dir + os.sep + jobid
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    
    fid = h5py.File(filename, 'r')
    band_names=["IMG_TIR1", "IMG_TIR2", "IMG_MIR", "IMG_WV", "IMG_VIS", "IMG_SWIR"]
    cal_ds_list = ["IMG_TIR1_TEMP", "IMG_WV_TEMP", "IMG_TIR2_TEMP", "IMG_MIR_TEMP", "IMG_VIS_ALBEDO"]
    
    for bname in band_names:
        count_ds = fid[bname][:];
        print("writing " + bname)
        count_ds.tofile(out_path + os.sep + bname + ".bin")
        for dsname in cal_ds_list:
            if dsname.startswith(bname):
                lut = fid[dsname][:]
                cal_ds = applyLUT(count_ds, lut)   
#                plt.figure()
#                plt.imshow(cal_ds.squeeze())
                print("writing " + dsname)
                cal_ds.tofile(out_path + os.sep + dsname +".bin")
    geo_ds_list=["Latitude", "Longitude", "Latitude_WV", "Longitude_WV", "Latitude_VIS", "Longitude_VIS"]
    for dsname in geo_ds_list:
        ds = fid[dsname]
        fv = ds.attrs['_FillValue'][0]
        sf = ds.attrs['scale_factor'][0]
        ao = ds.attrs['add_offset'][0]
        scaled_ds = scaleDS(ds[:], ao, sf, fv)
        print("writing " + dsname)
        scaled_ds.tofile(out_path + os.sep + dsname +".bin")
        
    fid.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] +  "  <h5 file name> <out_dir>")
        sys.exit(-1)
        
    filename = sys.argv[1]
    out_dir = sys.argv[2]
#    filename = "/tmp/3DIMG_13FEB2020_0700_L1B_STD.h5"
#    out_dir = "/tmp/"
    dumpData(filename, out_dir)
    
    