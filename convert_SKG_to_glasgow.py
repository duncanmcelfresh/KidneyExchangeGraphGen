"""convert_SKG_to_glasgow.py: converts an SKG file into Glasgow format for use 
with the kidney_solver package. Altruists are detected automatically (any 
vertex with no incoming edges is considered an altruist).

This borrows from the script convert_CMU_input_to_Glasgow.py in the 
kidney_solver/utils repo."""

import argparse
import logging
import os
import csv
import sys

logging.basicConfig()
_log = logging.getLogger('convert')
_log.setLevel(logging.DEBUG)

#    Glasgow format:
#    *.ginput:
#        <#pairs>	<#edges>
#    <from>	<to>	<weight>
#    0	6	1.0
#    -1	-1	-1
#    *.gndds is identical, indexed from zero
#    
#    SKG format: 
#    #comments  
#    <from> <to>


def readEdgeList( filename , comment='#'):
    with open(filename,'r') as f:
        lines = f.readlines()
    edges = [ l for l in lines if not l.startswith(comment) ]
    out_id = []
    in_id = []
    for i,e in enumerate(edges):
        outStr, inStr = e.split()[:2]
        out_id.append(int(outStr))
        in_id.append(int(inStr))
    return out_id,in_id

def convert_and_write( out_ids, in_ids, output_base ):
    """Take a complete edge list and return two edge lists, one for altruists 
    and one for patient/donor pairs"""

    ndd_id_map = {}
    pair_id_map = {}
    real_edge_list = []
    seen_ids = set()
    weight = 1.0 # set all weighs to 1
    ndd_outgoing_edge_ct = 0
    pairs_outgoing_edge_ct = 0
    
    for out_id,in_id in zip(out_ids,in_ids):
        # if id has not been seen, check if altruist
        if out_id not in seen_ids: 
            if out_id not in in_ids:
                new_ndd_id = len(ndd_id_map)
                ndd_id_map[out_id] = new_ndd_id
            else:
                new_pair_id = len(pair_id_map)
                pair_id_map[out_id] = new_pair_id
        seen_ids.add(out_id)
     
        if in_id not in seen_ids:
            if in_id not in in_ids:
                new_ndd_id = len(ndd_id_map)
                ndd_id_map[in_id] = new_ndd_id
            else:
                new_pair_id = len(pair_id_map)
                pair_id_map[in_id] = new_pair_id
            seen_ids.add(in_id)
        
        real_edge_list.append([out_id, in_id, weight])
        if out_id in ndd_id_map.keys():
            ndd_outgoing_edge_ct += 1
        else:
            pairs_outgoing_edge_ct += 1
        
    # Write all edges to either the .gndd or the .ginput output file
    pair_outfile = "{0}.ginput".format(output_base)
    ndds_outfile = "{0}.gndds".format(output_base)
    with open(pair_outfile, 'w') as pf, open(ndds_outfile, 'w') as nf:
        pwriter = csv.writer(pf, delimiter='\t')  # writer for pairs file
        nwriter = csv.writer(nf, delimiter='\t')  # writer for ndds file
        
        # Headers for either file are <num-verts-of-that-type> <num-edges>
        pwriter.writerow([len(pair_id_map), pairs_outgoing_edge_ct])
        nwriter.writerow([len(ndd_id_map), ndd_outgoing_edge_ct])

        # Now write the edges, with translated vertex IDs, to the files
        for src, tgt, weight in real_edge_list:
            if src in ndd_id_map.keys():
                assert tgt not in ndd_id_map.keys()  # can't have NDD->NDD
                nwriter.writerow([ndd_id_map[src], pair_id_map[tgt], weight])
            else:
                assert tgt not in ndd_id_map.keys()  # can't have pair->NDD
                pwriter.writerow([pair_id_map[src], pair_id_map[tgt], weight])
                
        # Each of the Glasgow files ends with -1 -1 -1
        EOF_arr = [-1, -1, -1]
        pwriter.writerow(EOF_arr)
        nwriter.writerow(EOF_arr)

    _log.info("Done writing to two files!")
          

def main():
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert SKG edge list to Glasgow input.')
    parser.add_argument('--input-file', dest='input_file', required=True, 
                        help='full path to SKG edge list file')
    parser.add_argument('--output-base', dest='output_base', required=True,
                        help='base path for Glasgow output files')
    args = parser.parse_args()

    input_file = args.input_file
    output_base = args.output_base
    
    # Sanity check arguments
    if not os.path.isfile(input_file):
        _log.error("Could not find input file {0}; quitting.".format(input_file))
        sys.exit(-1)    
    
    _log.info("Taking input from {0} and outputting to {1}.(ginput,gndds)".format(input_file, output_base))
    
    _log.info("Reading SKG edge list from {0}".format(input_file))
    out_ids, in_ids = readEdgeList( input_file )
    
    convert_and_write( out_ids, in_ids , output_base )

    # Perform the conversion and output to files
    _log.info("Done!")


if __name__ == '__main__':
    main()