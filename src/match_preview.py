#!/usr/bin/env python

import os, argparse, glob
import cv2
import numpy as np
import pandas as pd

# parse arguments in a beautiful way
# includes automatic help generation
def getArgs():

   # setup parser
   parser = argparse.ArgumentParser(
    description = '''Inner crop algorithm. Removes outer border from.''',
    epilog = '''post bug reports to the github repository''')

   parser.add_argument('-f',
                       '--file',
                       help = 'location of the cnn labels',
                       default = '../data-raw/cnn-labels/format_1_6127_162_cnn_labels.csv')

   parser.add_argument('-g',
                       '--guides',
                       help = 'guides',
                       default = '../data/templates/guides.txt')

   parser.add_argument('-i',
                       '--image',
                       help = 'location of a matched image',
                       default = 'format_1_6127_162_preview.jpg')
                       
   parser.add_argument('--output_dir',
                       help = 'name of output dir',
                       default = '../data/output/')

   # put arguments in dictionary with
   # keys being the argument names given above
   return parser.parse_args()

def load_guides(filename, mask_name):
   # check if the guides file can be read
   # if not return error
   try:
    guides = []
    file = open(u''+filename,'r')
    lines = file.readlines()
    for line in lines:
     if line.find("Guide:" + mask_name) > -1:
       data = line.split('|')
       data[0] = data[0].split(":")
       data[1] = data[1].split(",")
       data[2] = data[2].split(",")
       data[3] = data[3].split(",")
       guides.append(data)
    file.close()
    return guides
   except:
    print("No subset location file found!")
    print("looking for: " + mask_name + ".csv")
    exit()

def print_labels(im, locations, df):
  
  # retain empty values only
  #df = df.loc[df.cnn_label == "empty",:]
  
  # split out the locations
  # convert to integer
  x = np.asarray(locations[0][3], dtype=float)
  x = x.astype(int)
  x = np.sort(x)
  y = np.asarray(locations[0][2], dtype=float)
  y = y.astype(int)
  y = np.sort(y)
  
  # loop over all rows
  for i, row in df.iterrows():
   y_value = int(row['row'])
   x_value = int(row['col'])
   label = row['cnn_label']
   
   center_x = int(round((x[x_value-1] + x[x_value])/2))
   center_y = int(round((y[y_value-1] + y[y_value])/2))
   
   if label == 'empty':
    try:
     cv2.putText(im, "X" ,(center_x,center_y),
      cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),10,cv2.LINE_AA)
    except:
     continue
   else:
    try:
     cv2.putText(im, "." ,(center_x,center_y),
      cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),10,cv2.LINE_AA)
    except:
     continue
  return im

if __name__ == '__main__':
  
  # parse arguments
  args = getArgs()

  # get mask name
  mask_name, file_extension = os.path.splitext(args.image)
  mask_name = os.path.basename(mask_name)
  mask_name = "format_" + mask_name.split("_")[1]
  
  # load cnn results
  df = pd.read_csv(args.file)

  # read in aligned image
  im = cv2.imread(args.image)
  
  # load guides
  guides = load_guides(args.guides, mask_name)
  
  # print labels on original image
  im  = print_labels(im, guides, df)
  
  # print stuff to file
  filename = os.path.join(args.output_dir, os.path.basename(args.image))
  cv2.imwrite(filename, im)
  

