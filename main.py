from scipy.misc import imread, imresize
import numpy as np
import cv2
from Robertson import *
from tonemapping import *
from PaulDebevec import *
import sys

path = 'HDR_data/test1/'

def readfromfile(path, filename, scale):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    exp_times = []
    images = []

    for l in lines:
        tmp = l.split()
        filename = path + tmp[0]#.split('.')[0] + '.png' #'.JPG'
        print(filename)
        i = imread(filename)
        if scale == 1:
            images.append(i)
        else:
            images.append(imresize(i, scale)) # imresize(i, 0.15)
        exp_times.append(1./float(tmp[1]))
        
    exp_times = np.array(exp_times, dtype='float32')
    return images, exp_times


if __name__ == '__main__':


	algo = 'Paul'
	imSet = 1
	tempScale = 1.0
	if len(sys.argv) > 1: 
		if sys.argv[1] == 'Robertson' :
			algo = 'Robertson'
		else :
			algo = 'Paul'
	if len(sys.argv) > 2: 
		if int(sys.argv[2]) <= 3 and  int(sys.argv[2]) > 0:
			imSet = int(sys.argv[2])
		else :
			imset = 1

	if len(sys.argv) > 3: 
		tempScale = float(sys.argv[3])

	#print(imSet)

	images, exp_times = readfromfile('test'+str(imSet)+'/', 'test'+str(imSet)+'/input.txt', tempScale)
	# images, exp_times = readfromfile('HDR_data/', 'HDR_data/input.txt', 0.15 )

	# Remove blue backgrounds
	# height, width, channel = images[0].shape
	# for c in range(len(images)):
	#     for i in range(height):
	#         for j in range(width):
	#             if np.all(images[c][i][j] == [0,  0,  255]):
	#                 images[c][i][j] = [0,  0,  0]
	#                 print('hi', end='\r')

	if algo == 'Robertson' :
		recovery = RobertsonHDR('pic/')
		recover_hdr = recovery.process(images, exp_times)
	else :
		recovery = PaulDebevecHDR()
		recover_hdr = recovery.AssembleHDR(images, exp_times)

	"""
	E = recover_hdr
	cv2.imwrite("Robertson_myhdr_mini.hdr", E[...,[2,1,0]]) 
	ldrDrago = tonemapping(E, 0.5, 1.0) 
	t = np.clip(ldrDrago*255, 0, 255).astype('uint8')
	cv2.imwrite("Robertson_mytonemap_mini.jpg", t[...,[2,1,0]] )

	print('finish recover mini HDR')

	images, exp_times = readfromfile('HDR_data/', 'HDR_data/input.txt', 1)

	height, width, channel = images[0].shape
	hdr = np.zeros([height, width, 3], dtype='float32')
	for c in range(3): 
	    for i in range(height):
	        for j in range(width):
	            u = 0.0
	            b = 0.0
	            for n in range(len(images)):
	                z = images[n][i,j,c]
	                t = exp_times[n]
	                u += recovery.w[z] * recovery.res_curve[c,z] * t
	                b += recovery.w[z] * t * t
	            hdr[i,j,c] = u/b
	    print('finish channel', c)
	"""
	if algo == "Robertson":
		s = "Robertson"
	else :
		s = "PaulDebevec"
		
	E = recover_hdr
	cv2.imwrite(s+"_myhdr_full.hdr", E[...,[2,1,0]]) 
	ldrDrago = tonemapping(E, 0.5, 1.0) 
	t = np.clip(ldrDrago*255, 0, 255).astype('uint8')
	cv2.imwrite(s+"_mytonemap_full.jpg", t[...,[2,1,0]] )
