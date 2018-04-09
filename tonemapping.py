import math
import numpy as np
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
        ldrpic[:,:,i] = (((hdrpic[:,:,i] *( 1/L_w ))) ** s ) * L_final
        
    return ldrpic