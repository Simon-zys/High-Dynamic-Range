import math
import numpy as np
from scipy.signal import convolve2d

def tonemapping(hdrpic, s, a=2.0 ):
    height, weight, channel = hdrpic.shape
    print(hdrpic.shape)
    N = height * weight
    delta = 0.00001
     
    L_w = 0.2125 * hdrpic[:,:,0] + 0.7154 * hdrpic[:,:,1] + 0.0721 * hdrpic[:,:,2] 
    L_w_mean = math.exp( sum(sum( np.log(delta + L_w) ))/N ) 
    
    key_scale = a / L_w_mean 
    
    L = key_scale * hdrpic 
    sL_w = key_scale * L_w 
    L_final = sL_w / (1 + sL_w) 

    ldrpic = np.zeros(hdrpic.shape)

    for i in range(3):
        ldrpic[:,:,i] = (((hdrpic[:,:,i] * ( 1/L_w ))) ** s ) * L_final
        
    return ldrpic

def tonemapping_local(hdrpic, sat, a=2.0 ):
    height, weight, channel = hdrpic.shape
#     print(hdrpic.shape)
    N = height * weight
    delta = 0.00001
      
    L_w = 0.2125 * hdrpic[:,:,0] + 0.7154 * hdrpic[:,:,1] + 0.0721 * hdrpic[:,:,2] 
    
    level, phi = 8, 8 
    
    v1 = np.zeros((L_w.shape[0], L_w.shape[1], level), dtype='float32')
    v = np.zeros((L_w.shape[0], L_w.shape[1], level), dtype='float32')
    v1_sm = np.zeros((L_w.shape[0], L_w.shape[1]), dtype='float32')
    
    for scale in range(level): 
        mask = matlab_style_gauss2D((43, 43), 0.5)
        v1[:,:,scale] = convolve2d(L_w, mask, 'same')
        mask = matlab_style_gauss2D((43, 43), 0.5)
        v2 = convolve2d(L_w, mask, 'same')
        if scale == 0:
            v[:,:,scale] = (v1[:,:,scale] - v2) /  v1[:,:,scale]
        else:
            v[:,:,scale] = (v1[:,:,scale] - v2) / (((2 ** phi * 0.36) / (scale)**2) + v1[:,:,scale])
    
    
    sm = np.zeros((L_w.shape[0], L_w.shape[1]))-1
    tmp = np.ones((L_w.shape[0], L_w.shape[1]))
    
    for scale in range(level):
        target = tmp * (abs(v[:,:,scale]) < 0.05)
        tmp = tmp - target
        sm[target==1] = scale

    sm[sm == -1] = 0
    
    for x in range(v1.shape[0]):
        for y in range(v1.shape[1]):
            v1_sm[x,y] = v1[x, y, int(sm[x,y])]

    L_w_mean = math.exp( sum(sum( np.log(delta + v1_sm) ))/N ) 
    key_scale = a / L_w_mean 
    L = key_scale * v1_sm 
    sL_w = key_scale * L_w 
    L_d = sL_w / (1 + L)  
    
    ldrpic = np.zeros(hdrpic.shape)

    for i in range(3):
        ldrpic[:,:,i] = (((hdrpic[:,:,i] * ( 1/L_w ))) ** sat ) * L_d
    
    ldrpic[ldrpic > 1] = 1
    
    return ldrpic

def matlab_style_gauss2D(shape=(3,3), sigma=0.5):
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h