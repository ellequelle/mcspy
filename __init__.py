from indexing import *



# load index, only keep records that overlap with time that has published MDGMs
dfindex = reload_index().query(qmarci_mdgm)
