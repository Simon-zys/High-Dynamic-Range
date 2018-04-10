import numpy as np
import math
class RobertsonHDR():
    def __init__(self):
        self.MAXITER = 10
        self.THRESHOLD = 0.0001
        self.res_curve = np.zeros([3, 256], dtype='float32')
        
        # init for weight function
        self.w = [math.exp(-4 * (y - 127.5)**2 / (127.5)**2) for y in range(256)]
         
    def process(self, images, exp_time):
        self.images = images
        self.exp_time = exp_time
        
        self.res_curve[0,:] = self.find_res_curve(0)
        self.res_curve[1,:] = self.find_res_curve(1)
        self.res_curve[2,:] = self.find_res_curve(2)
        
#         self.normalizeCurve()
        
        # recover HDR
        print('Start to recovery HDR')
        height, width, channel = self.images[0].shape
        self.hdr = np.zeros([height, width, 3], dtype='float32')
        for c in range(3): 
            for i in range(height):
                for j in range(width):
                    u = 0.0
                    b = 0.0
                    for n in range(len(images)):
                        z = self.images[n][i,j,c]
                        t = self.exp_time[n]
                        u += self.w[z] * self.res_curve[c,z] * t
                        b += self.w[z] * t * t
                    self.hdr[i,j,c] = u/b
        
        return self.hdr
    
    def find_res_curve(self, c):
        
        height, width, channel = self.images[0].shape
        # init Em
        Em = {}
        for j in range(256):
            Em[j] = []
         
        for n in range(len(self.images)):
            for i in range(height):
                for j in range(width): 
                    m = self.images[n][i,j,c] 
                    Em[m].append(tuple((tuple((i,j)),n)))

        
        # init CRF: g
        crf_c = np.zeros([256], dtype='float32')
        for i in range(256):
            crf_c[i] = ((float)(i) / 128.)
        print('make sure g(128) = 1, res_curve(128):', crf_c[128])
        
        # init rad map: E
        rad_map_c = np.zeros([height, width], dtype='float32')
        for i in range(height):
            for j in range(width):
                u, b = 0.0, 0.0 
                for n in range(len(self.images)):
                    z = self.images[n][i,j,c]
                    t = self.exp_time[n]
                    u += self.w[z] * crf_c[z] * t
                    b += self.w[z] * t * t
                rad_map_c[i,j] = u/b
        
        num = 0          
        old_value = 1000000.0
        while num < self.MAXITER:
            
            # assume E is known, optimize g
            crf_c = np.zeros([256], dtype='float32') 
            for i in range(256): 
                for n in range(0,len(Em[i])):
                    point, idx = Em[i][n]
                    crf_c[i] += rad_map_c[point[0],point[1]] * self.exp_time[idx]
                if len(Em[i]) > 0:
                    crf_c[i] /= len(Em[i])
                    
            crf_c /= crf_c[128]
            # assume g is known, optimize E 
            for i in range(height):
                for j in range(width):
                    u, b = 0.0, 0.0
                    for n in range(len(self.images)):
                        z = self.images[n][i,j,c]
                        t = self.exp_time[n]
                        u += self.w[z] * crf_c[z] * t
                        b += self.w[z] * t * t
                    rad_map_c[i,j] = u/b

            # check if converge
            current_value = 0.0
            for n in range(len(self.images)): 
                t = self.exp_time[n]
                for i in range(height):
                    for j in range(width):
                        z = self.images[n][i,j,c] 
                        d = crf_c[z] - rad_map_c[i,j] * t;
                        current_value += self.w[z] * d * d;
            
        
            diff = abs(old_value - current_value)
            if num>0 and diff < self.THRESHOLD:
                #print()
                print('converge, round = %d/%d, diff=%f' % (num+1, self.MAXITER, diff))
                break
            else:
                old_value = current_value
#             print(current_value)
                
            print('channel %d, Robertson round = %d/%d, diff = %f   ' %(c, num+1, self.MAXITER, diff), end='\r')
            num += 1
        print()
        print('Finish find response curve for channel', c)
        
        
        return np.expand_dims(crf_c, 0)
        
    
    def normalizeCurve(self):
        for c in range(3):
            t = self.res_curve[c,crf_c]
            self.res_curve[c] /= t