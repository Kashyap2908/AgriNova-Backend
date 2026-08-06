import numpy as np
import pickle

class IndexFlatIP:
    def __init__(self, d):
        self.d = d
        self.xb = np.empty((0, d), dtype='float32')
        
    def add(self, x):
        self.xb = np.vstack((self.xb, x))
        
    def search(self, x, k):
        # Inner product
        sims = np.dot(x, self.xb.T)
        I = np.argsort(sims, axis=1)[:, ::-1][:, :k]
        D = np.take_along_axis(sims, I, axis=1)
        return D, I

def write_index(index, filename):
    with open(filename, 'wb') as f:
        pickle.dump(index, f)

def read_index(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
