# ----------------------------------------------------------------------
# this code detects clusters based on particle size dp and location data 
# code output: clusterdistribution which is Ncx4 matrix 
# where number of rows Nc = number of clusters detected 
# and each row has format [# particles with cluster, x-centroid, y-centroid, z-centroid]
#
# If you use this tool, please reference the following publication:
# Bakshi, A., Altantzis, C., Bates, R.B., and Ghoniem, A. F.,
# "Multiphase-flow Statistics using 3D Detection and Tracking Algorithm (MS3DATA): 
# Methodology and application to large-scale fluidized beds.", 
# Chemical Engineering Journal 293 (2016): 355-364
# ------------------------------------------------------------------------

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np 
import time 

# enter variables
dp = 0.6    # distance between particle centroids for cluster detection. default = [particle diameter] 
particlelocation = np.loadtxt('currentparticlelocation.txt', usecols=range(3)) # particle locations = [x,y,z]

# calculations begin here 
start_time = time.time()
def func_updatelist(currentparticle,currentindex,neighbormatrix,currentlist,pendinglist):
    neighbormatrix[currentparticle,1] = currentindex
    currentlist = np.append(currentlist, currentparticle)
    pendinglist = np.setdiff1d(pendinglist,currentparticle)
    return currentlist, pendinglist, neighbormatrix   

numparticles = np.size(particlelocation,0)
neighbormatrix = np.zeros((numparticles,3), dtype=int)
neighbormatrix[:,0] = np.arange(numparticles)

currentlist = np.zeros((1,1))
np.delete(currentlist,0) 
pendinglist = np.arange(numparticles)
clusterindex = 0 

# first pass: link every particle with its neighbors in pendinglist using clusterindex  
while len(pendinglist)>0:
    iparticle = pendinglist[0]
    neighbormatrix[iparticle,2] = 1
    currentparticlelocation = particlelocation[iparticle,:]
    particlesincontact = np.sqrt(((currentparticlelocation - particlelocation)**2).sum(axis=1)) 
    particlesincontact = np.asarray(np.where(particlesincontact<dp))[0,:] 
    # particlesincontact = particles (absolute indices) in contact with iparticle, including iparticle itself 

    if len(particlesincontact) == 1: 
        pendinglist = np.setdiff1d(pendinglist,iparticle)
    else: 
        clusterindex += 1 
        currentlist, pendinglist, neighbormatrix = \
            func_updatelist(np.intersect1d(pendinglist,particlesincontact),clusterindex,neighbormatrix,currentlist,pendinglist) 
                  
# second pass: check clusterindices of neighbors of all particles skipped in first pass 
particleIDs = np.arange(numparticles)                    
for iparticle in particleIDs[neighbormatrix[:,2]==0]:
     currentparticlelocation = particlelocation[iparticle,:]
     particlesincontact = np.sqrt(((currentparticlelocation - particlelocation)**2).sum(axis=1)) 
     particlesincontact = np.asarray(np.where(particlesincontact<dp))[0,:]    
     
     equivalentclusters = np.unique(neighbormatrix[particlesincontact,1])
     if len(equivalentclusters)>1: 
         clusterindex = int(np.min(neighbormatrix[particlesincontact,1]))        
         neighbormatrix[np.isin(neighbormatrix[:,1],equivalentclusters),1] = clusterindex


# compute distribution of clusters in format: [num-particles, x, y, z]
clusterdistribution = np.zeros((len(np.unique(neighbormatrix[:,1])),4), dtype=float)
for cluster in range(len(np.unique(neighbormatrix[:,1]))):
    clusterdistribution[cluster,0] = sum(neighbormatrix[:,1]==np.unique(neighbormatrix[:,1])[cluster])
    clusterdistribution[cluster,1:] = np.mean(particlelocation[neighbormatrix[:,1]==np.unique(neighbormatrix[:,1])[cluster],:],axis=0)
clusterdistribution = clusterdistribution[1:,:]

print("--- %s seconds ---" % (time.time() - start_time))      
    

          
                                      


