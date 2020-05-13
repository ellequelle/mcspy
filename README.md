# mcspy
`mcspy` is for working with data from the [Mars Climate Sounder](https://mars.nasa.gov/mro/mission/instruments/mcs/), an instrument aboard the NASA [Mars Reconnaisance Orbiter](https://mars.nasa.gov/mro/mission/overview/).

MCS data is publicly available on the [Planetary Data System (PDS) Atmospheres node](https://pds-atmospheres.nmsu.edu) in the form of thousands of separate text files. Each text file has several hundred retrieved profiles, typically from two orbits around Mars. All of the metadata is in the same files as the profile data, meaning that in order to find profiles at a specific location or time, it is necessary to read many text files. 

Working with the data as a collection of thousands of text files is inefficient, so I wrote `mcspy` to simplify the process of downloading data and converting it to a more useful form.

## Guide
`mcspy` recreates a modified DATA directory and its children from the volumes on the PDS. Each PDS volume is structured according to this diagram, taken from the file [AAREADME.TXT](https://atmos.nmsu.edu/PDS/data/MROM_2001/AAREADME.TXT) in volume [MROM_2001](https://atmos.nmsu.edu/PDS/data/MROM_2001/):
```
root
|- AAREADME.TXT          The file you are reading.
|
|- ERRATA.TXT            A listing of known errors/problems on
|                        this volume. (Not present if empty.)
|
|- VOLDESC.CAT           A description of the contents of this
|                        volume in a format readable by
|                        both humans and computers.
|
|- [CALIB]               A directory containing calibration
|                       information about this data set.
|
|- [CATALOG]             A directory containing descriptive
|     |                  information about this data set.
|     |
|    ...
|- [DOCUMENT]            A directory containing related documents.
|     |
|     |
|    ...
|- [INDEX]               A directory containing indices of data
|     |                  products in this data product set.
|     |
|     |- INDXINFO.TXT    A description of files in the INDEX
|     |                  directory.
|     |
|     |- INDEX.TAB       An index of data files on this volume.
|     |
|     |- INDEX.LBL       The detached PDS label for INDEX.TAB.
|     |
|     |- CUMINDEX.TAB    An index of all the data files on this
|     |                  archive volume set, including those on
|     |                  this volume.
|     |
|     |- CUMINDEX.LBL    The detached PDS label for CUMINDEX.TAB.
|
|- [DATA]                A directory containing the data files
|     |                  and PDS labels describing the contents
|     |                  of those files.
|     |
|     - [2006]           The year of this archive volume.
|         |
|         - [06]         The month of this archive volume.
|            |
|            - [DD]      A series of subdirectories organized by
|               |        day of month.
|               |
|               - YYYYMMDDHH_DDR.TAB
|               |        A four hour MCS RDR data product file.
|               |
|               - YYYYMMDDHH_DDR.LBL
|                        The corresponding detached label file.
|
|- [LABEL]               A directory containing the format
|                        structure files.
      |
      |- LABINFO.TXT     Description of files in the LABEL
      |                  directory.
      |
      |- MCS_DDR1.FMT     A format file describing the columns
      |                   in record 1 of MCS DDR data product tables.
      |
      |- MCS_DDR2.FMT     A format file describing the columns
                          in record 2 of MCS DDR data product tables. 
			
```

``mcspy.importer`` mirrors the `DATA` directory structure and downloads the requested data files, saving gzipped copies as `YYYYMMDDHH_DDR.TAB.gz`. Unlike the data volumes on the PDS server, the DDR data files are organized by date and not by data volume. In addition to the data files, ``mcspy`` requires the cumulative index file [CUMINDEX.TAB](https://atmos.nmsu.edu/PDS/data/MROM_2158/INDEX/CUMINDEX.TAB), which is downloaded once from the most recent available volume and saved as `CUMINDEX.TAB.gz`. This index file is loaded as a pandas DataFrame when the library is imported and it is used to look up file names and retrieval dates.





## Requirements
* numpy
* pandas
* requests (can substitute ftplib if necessary)



