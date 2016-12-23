#!/usr/bin/python

# genExchangeSKG.py
# generate a kidney exchange graph using the 2x2 Stochastic Kronecker Grpah 
# Model, trained on real-world kidney exchange data.

import skg_functions

# parameters for SKG models
SKG_params = dict()
SKG_params[('64','k')]  = 6
SKG_params[('64','p0')]  = [[0.826,0.902],[0.865,0.327]]
SKG_params[('128','k')]  = 7
SKG_params[('128','p0')] = [[0.910,0.917],[0.868,0.331]]
SKG_params[('256','k')]  = 8
SKG_params[('256','p0')] = [[0.990,0.920],[0.841,0.367]]
SKG_params[('512','k')]  = 9
SKG_params[('512','p0')] = [[0.999,0.936],[0.857,0.408]]

import sys, getopt

def main(argv):
   snapdir = ''
   outdir = ''
   num=0
   try:
      opts, args = getopt.getopt(argv,"hs:o:n:",["sdir=","odir=","num="])
   except getopt.GetoptError:
      print 'genExchangeSKG.py -s <snapdir> -o <outdir> -n <size=(64|128|256|512)>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'genExchangeSKG.py -s <snapdir> -o <outdir> -n <size=(64|128|256|512)>'
         sys.exit()
      elif opt in ("-s", "--snapdir"):
         snapdir = arg
      elif opt in ("-o", "--outdir"):
         outdir = arg
      elif opt in ("-n", "--num"):
         num = arg
         if num not in [64,128,256,512]:
             print 'genExchangeSKG.py -s <snapdir> -o <outdir> -n <size=(64|128|256|512)>'
             print 'num must be either 64, 128, 256, or 512'             
             sys.exit(2)
   print 'SNAP dir is: "', snapdir
   print 'Ourput dir is: "', outdir
   print 'SKG size is: "', num
   k = SKG_params[(num,'k')]
   p0 = SKG_params[(num,'p0')]
   skg_file = skg_functions.genSKG(outdir, snapdir, p_0=p0, k=k,overwrite=False)
   print 'Generated SKG file: "', skg_file

if __name__ == "__main__":
   main(sys.argv[1:])