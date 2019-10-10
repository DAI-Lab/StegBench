#!/usr/bin/python
#The program generate the lmdb dataset for the Caffe input
#Implement in python-2.7

import caffe
import lmdb
from scipy import ndimage
import os
import numpy as np
from caffe.proto import caffe_pb2

#prepare for the image dir and names
#the images should be decompressed to spatial format first
#
cover_path="./spatial_representations/cover/"
stego_path="./spatial_representations/stego_juniward_40/"

#image name    
image_names_string=os.popen("ls "+cover_path).read()
image_names=image_names_string.split('\n')[0:-1]

#basic setting
lmdb_file = 'target_lmdbfile'
batch_size = 50000

# create the lmdb file
lmdb_env = lmdb.open(lmdb_file, map_size=int(1e13))
lmdb_txn = lmdb_env.begin(write=True)
datum = caffe_pb2.Datum()

item_id = -1
image_id= 0
for x in range(500000):
    item_id += 1
    
    #prepare the data and label
    #read in cover-stego pair
    if(item_id % 2) == 0:
        image_path=os.path.join(cover_path,image_names[image_id])
        images=np.zeros([256,256])
        image_file=open(image_path,'r')
        for i in range(256):
            images[i]=image_file.readline().split()
        data_temp=images
        data=data_temp[np.newaxis,:,:]
        label=1
    else :
        image_path=os.path.join(stego_path,image_names[image_id])
        images=np.zeros([256,256])
        image_file=open(image_path,'r')
        for i in range(256):
            images[i]=image_file.readline().split()
        data_temp=images
        data=data_temp[np.newaxis,:,:]
        label=0
        image_id+=1

    # save in datum
    datum = caffe.io.array_to_datum(data, label)
    keystr = '{:0>8d}'.format(item_id)
    lmdb_txn.put( keystr, datum.SerializeToString() )

    # write batch
    if(item_id + 1) % batch_size == 0:
        lmdb_txn.commit()
        lmdb_txn = lmdb_env.begin(write=True)
        print (item_id + 1)

# write last batch
if (item_id+1) % batch_size != 0:
    lmdb_txn.commit()
    print 'last batch'
    print (item_id + 1)
