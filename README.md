# VFX-HW1-HDR
### Soure Code

  ./main.py: the main function to read all .ldr files and run HDR recovery, then finally tonemapping to .ldr
  
  ./PaulDebevec.py: The Paul's Debevec HDR recovery algorithm
  
  ./Robertson.py: The Robertson HDR recovery algorithm
  
  ./tonemapping.py: The Photographic tone mapping of global operator and local operator(Dodging and burning)

### How to run
* ```python main.py [method] [imageSet] [scale]```
* method : "Paul" for PaulDebevec algorithm  , "Robertson" for Robertson algorithm
* imageSet: can be 1 , 2 or 3
* scale: scale the image to run faster
