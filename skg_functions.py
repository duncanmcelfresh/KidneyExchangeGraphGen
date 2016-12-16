# Functions for generating SKGs using SNAP library
#
# 
#
# -----------------------------------------------------------------------------
 #run_command: run a command using subprocess and save output
#
# required arguments:
# - command : UNIX shell command
#
# optional arguments
# - logfile : file path for shell output
#
def run_command(command, logfile=''):
    import subprocess
    import shlex
    doLog = False
    if logfile != '':
        outf = open(logfile, 'w')
        doLog = True
        
    #print "Running Command: " + command
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            outs = output.strip()
            print outs
            if doLog: outf.write(outs + '\n')
    rc = process.poll()
    if doLog: outf.close()
    return rc
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# genSKG: generate an SKG using SNAP
#
# required arguments:
# - outdir  : output directory for generated SKG files
# - snapdir : directory containing SNAP executables
#
# optional arguments:
# - p_0 : nxn SKG initiator matrix
# - k   : number of Kronecker iterations. The number of nodes in the resulting 
#         SKG will be n^k
# - outname : output file name for the SKG
# - overwrite : if True, overwrite existing files if 
#
def genSKG(outdir, snapdir, p_0 = [[0.9,0.5],[0.5,0.1]], k = 5, outname='',overwrite=False):
    import os
    import time
    
    if outname == '' : outname = time.strftime("%d%b%Y_%H%M%S")
    
    krongen = snapdir + r'/examples/krongen/krongen'
    
    # convert p_0 to matlab-formatted string
    p_0_str = '"' + '; '.join( [' '.join(j)
        for j in [ [ str(i) for i in p] for p in p_0 ] ] ) + '"' 
    fname = outdir + os.sep + 'SKG_' + outname + '.txt'
    
    ## only if graph isn't generated
    if not os.path.isfile(fname) or overwrite:
        curdir = os.getcwd()    
        os.chdir(outdir)
        ## set up command
        cmd = ' '.join([krongen, '-o:'+fname, '-m:'+p_0_str, '-i:'+str(k)])
                
        rc = run_command(cmd)
        return fname
        os.chdir(curdir)
    else: 
        print "WARNING: Graph already exists with the following name: "+fname
        print "no SKG was generated."
        return fname
  
    if os.path.isfile(fname): 
        return fname
    else:
        print "SKG generation failed"
        return False

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# graphStats : calculate network singular values, hop plot, in degree, and out 
#              degree for a set of graphs. SNAP functions are used to calculate
#              each of these parameters.
#
# dependencies:
# - snap (SNAP python interface)
# - numpy
#
# required arguments:
# - graph_file_list : list containing graph files in edge list format
#
# optional arguments:
# - savefile : if this argument is used, a dict containing lists of these graph
#              parameters will be pickled with this filename
# 
def graphStats( graph_file_list, savefile='' ):
    import snap
    import numpy as np
    n_sv = 4
    n_hop = 20
    n_deg = 2000
    svArr = np.zeros( [ len(graph_file_list),n_sv ] )
    hopCntArr = np.zeros( [ len(graph_file_list), n_hop ] )
    inDegCntArr = np.zeros( [ len(graph_file_list), n_deg  ] )
    outDegCntArr = np.zeros( [ len(graph_file_list), n_deg  ] )

    i = 0
    for graph in graph_file_list:
        g = snap.LoadEdgeList(snap.PNGraph, graph, 0, 1) # outedge - 0th col, inedge - 1st col
        # ev = evalsSNAP( g, n_eig = n_ev) # undirected grpah only...
        sv = svalsSNAP( g, n_sv = n_sv)
        [hop, hcnt] = hopSNAP( g, maxnum = n_hop, qual = 1024)
        [indeg, dcnt] = indegSNAP( g )
        [outdeg, odcnt] = outdegSNAP( g )
        svArr[i] = sv
        hopCntArr[i][ hop ] = hcnt
        inDegCntArr[i][ indeg ] = dcnt
        outDegCntArr[i][ outdeg ] = odcnt
        i+=1

    maxhop = np.max(np.nonzero(np.sum(hopCntArr,axis=0)))
    maxindeg = np.max(np.nonzero(np.sum(inDegCntArr,axis=0)))
    maxoutdeg = np.max(np.nonzero(np.sum(outDegCntArr,axis=0)))
    
    hopCntArr = hopCntArr[:,:maxhop+1]   
    inDegCntArr = inDegCntArr[:,:maxindeg+1]
    outDegCntArr = outDegCntArr[:,:maxoutdeg+1]
    
    skgStats = { 'sv':svArr, 
                   'hop':hopCntArr,
                   'indeg':inDegCntArr,
                   'outdeg':outDegCntArr}
    
    ## save the graph metrics
    if savefile != '':
        import pickle
        with open(savefile,'w') as f:
            pickle.dump(skgStats, f)    
        
    return [ svArr, hopCntArr, inDegCntArr, outDegCntArr ]
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# use SNAP to calculate graph metrics. For each function, the parameter "grpah"
# is a SNAP graph object. Each function returns python lists
import snap

# Singular Values
def svalsSNAP( graph, n_sv = 20):
    SngValV = snap.TFltV()
    snap.GetSngVals(graph, n_sv, SngValV)
    svArr = [ sv for sv in SngValV ]
    return svArr

# Hop Plot
def hopSNAP( graph, maxnum = 10, qual = 1024):
    DistNbrsV = snap.TIntFltKdV()
    snap.GetAnf(graph, DistNbrsV, maxnum, False, qual) # adjust the approximation quality if too slow
    cnt = [ dn.Dat() for dn in DistNbrsV ]
    hop = [ dn.Key() for dn in DistNbrsV ]
    return [ hop, cnt ]
    
# in-degree distribution
def indegSNAP( graph ):
    DegToCntV = snap.TIntPrV()
    snap.GetDegCnt(graph, DegToCntV)
    deg = [ dg.GetVal1() for dg in DegToCntV ]
    cnt = [ dg.GetVal2() for dg in DegToCntV ]
    return [deg, cnt]

# out-degree distribution
def outdegSNAP( graph ):
    DegToCntV = snap.TIntPrV()
    snap.GetOutDegCnt(graph, DegToCntV)
    deg = [ dg.GetVal1() for dg in DegToCntV ]
    cnt = [ dg.GetVal2() for dg in DegToCntV ]
    return [deg, cnt]
# -----------------------------------------------------------------------------
