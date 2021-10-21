from math import sqrt
import cv2
import numpy as np
from matplotlib import pyplot as plt
class ContorProduce:#imageは二つ画像(0,1)
    def __init__(self,image) -> None:
        self.image = np.array(image,dtype = np.uint8)
        self.image = np.flipud(self.image)
        self.image *= 255
        self.contours,self.hierarchy = cv2.findContours(self.image,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    def ContorNumber(self):
        return len(self.contours)
        
    def produce(self,index):#[[x,y] ...]
        self.rev = []
        for tmp in self.contours[index]:
            for x,y in tmp:
                self.rev.append((x,y))
        return np.array(self.rev)

    def viewCopntors(self,index):
 
        return
'''
image = np.load('./data/sliced.npy')
cp = ContorProduce(image)
cp.viewCopntors(0)
print(cp.produce(0))

'''


