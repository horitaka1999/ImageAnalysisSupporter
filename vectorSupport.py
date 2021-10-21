from sklearn.decomposition import PCA
from itertools import combinations
import numpy as np 
class pcaVector:
    def __init__(self,contorData,parameter = 3):
        self.revVector = []
        self.contorData = contorData
        for i in range(len(contorData)):
            data = []
            for k in range(i-parameter,i+parameter):
                if self.check(k):
                        data.append(contorData[k])
            pca = PCA(n_components = 1)
            pca.fit(data)
            self.revVector.append(pca.components_[0])
        self.revVector = np.array(self.revVector)  

    def check(self,index):
        if 0 <= index < len(self.contorData):
            return True
        
    def saveData(self):
       np.save('./data/pcaVector',self.revVector) 
       
    def calcMaxArg(self,index,kparameter):
        tmp = [i for i in range(max(index-kparameter,0),min(index+kparameter,len(self.contorData)))]
        store = []
        for u,v in combinations(tmp,2):
            vec1 = self.revVector[u]
            vec2 = self.revVector[v]
            arg = np.inner(vec1,vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            store.append(1-abs(arg))
        return max(store)
            
            
            
        