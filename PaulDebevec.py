import numpy as np
import math


class PaulDebevecHDR():
	
	def __init__ (self):
		#self.weight = [  abs(x-127.5)/127.5  for x in range(256)]
		self.smoothLambda = 3.0
		



	def AssembleHDR(self ,images , exp_time ):

		if images is None or exp_time is None :
			return None

		if len(images) != len(exp_time):
			return None

		# Initialization

		print("init")
		

		self.images = images
		self.exp_time = exp_time
		self.ldrCount = len(images)
		# self.weight = [  abs(float(x)-(127.5))/(127.5)  for x in range( 256)]
		self.weight = np.zeros((256,1))
		for z in range(128):
			self.weight[z] = float(z + 1) / 128.
		for z in range(128, 256):
			self.weight[z] = float(255 - z + 1) / 128.
		# print(self.weight)

		self.sampleNum = int( float(255) / float(self.ldrCount-1) ) * 2 if  int( float(255) / float(self.ldrCount-1) ) * 2 >= 50 else 50 # according to formula
		self.imageCount = len(images)

		print(self.sampleNum)

		self.valueRange = 255
		self.channel = np.shape(images[0])[2]


		self.g = np.zeros((256, self.channel ) , dtype='float32' )
		self.le = np.zeros((self.sampleNum, self.channel ) , dtype='float32' )
		self.hdr = np.zeros( np.shape(self.images[0]) , dtype='float32')

		totalPixel = np.shape(images[0])[0] * np.shape(images[0])[1]
		Z = np.zeros( (self.sampleNum , self.imageCount ,self.channel) , dtype = 'int32')

		#print("aaa")

	
		for i in range(self.sampleNum):
		
			n = np.random.randint(0, totalPixel)
			for j in range(self.imageCount):
				for c in range(self.channel):
					
					Z[i,j,c] = (  self.images[j][ int(n/np.shape(images[j])[1]) , int(n%np.shape(images[j])[1]) , c] )
		# print(Z)
					#print("i "+str(i)+" j " +str(j)+"  "+str(Z[j,i]))


		#ImageAlignment()  ... not implement yet

		# Solve least square
		N = 256

		for c in range(self.channel):

			print("c "+str(c))

			A = np.zeros( ( self.sampleNum*self.ldrCount + N + 1 , self.sampleNum+(256)) , dtype='float32')
			print(A.shape)
			b = np.zeros( ( self.sampleNum*self.ldrCount + N+1  , 1) , dtype='float32')
			x = np.zeros ( ( self.sampleNum+N+1,1) , dtype = 'float32')

			k = 0

			for i in range(self.sampleNum) :
				for j in range(self.imageCount):

					wij = self.weight[Z[i,j,c]]
					A[k, Z[i,j,c]] = wij
					A[k, 256 + i]  = -wij
					b[k , 0] = wij * math.log(self.exp_time[j])
					k = k+1


			A[k,128] = 1.0
			k = k+1

			#print("ddd")

			for j in range(254):
				A[k,j] = self.smoothLambda * self.weight[j+1]
				A[k,j+1] = -2.0 * self.smoothLambda*self.weight[j+1]
				A[k,j+2] = self.smoothLambda * self.weight[j+1]
				k = k +1

			sol = np.linalg.lstsq(A,b)[0] # solve least square

			print(np.shape(sol))
			self.g[:,c] = np.squeeze(sol[:256]) #np.reshape(  sol[:256] , (256,) )
			self.le[:,c] = np.squeeze(sol[256:]) #np.reshape( sol[256:] , (len(sol)-256 , ) )

			# Reconstuct Radiance Map

			#print("eee")

			for i in range(np.shape(self.hdr)[0]):

				for j in range(np.shape(self.hdr)[1]):
					upper = 0.0
					bottom = 0.0
					for index in range(len(self.images)):
						value = self.images[index][i,j,c]
						t = self.exp_time[index]
						upper += self.weight[value] * ( self.g[value,c] - math.log(t) )
						bottom += self.weight[value] 

					self.hdr[i,j,c] = math.exp(upper/bottom)

		with open('CRF_deb.dat', 'wb') as f:
			self.g.dump(f)
			
		return self.hdr


	def ImageAlignment():
		pass










		





	def ImageAlignment(self):
		pass
