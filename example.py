# generate 3 Stochastic Kronecker Graphs with 1024 nodes using the 
# initiator matrix: 
# p_0 = [[0.9999,0.9999],[0.85,0.47]]

import skg_functions
import numpy as np
import matplotlib.pyplot as plt
import config

# change this to the directory containing SNAP executables 
snapdir = config.snapdir

# output directory for new SKG files
outdir = '.'

# SKG initiator matrix
p0 = [[0.9999,0.9999],[0.85,0.47]]

# number of Kronecker iterations
kIter = 10

# number of SKGs to generate
numSKG = 3

SKG_files = ['']*numSKG
for i in range(numSKG):
    oname = str(i)
    print(oname)
    SKG_files[i] = skg_functions.genSKG( outdir, snapdir, p_0 = p0, k = kIter, outname=oname, overwrite=True )
    
# calculate statistics for SKGs
[svSKG, hopSKG, inDegSKG, outDegSKG] = skg_functions.graphStats( SKG_files )
    
# calculate CDF of in-degree for all SKGs
cdfs = np.cumsum(inDegSKG,axis=1)
cdfNorm = cdfs / max(cdfs[0]) # normalize to 1
    
# plot the CDFs
fig, ax = plt.subplots()
ax.xaxis.set_ticks(np.arange(0, 1200, 200))
ax.set_title("CDF of In-Degree")
ax.set_xlabel("In-Degree")
ax.plot( np.transpose(cdfNorm) )
plt.show()
