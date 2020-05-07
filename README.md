## mcspy
**mcspy** is for working with data from the [Mars Climate Sounder](https://mars.nasa.gov/mro/mission/instruments/mcs/), an instrument aboard the NASA [Mars Reconnaisance Orbiter](https://mars.nasa.gov/mro/mission/overview/).

MCS data is publicly available on the [Planetary Data System (PDS) Atmospheres node](https://pds-atmospheres.nmsu.edu) in the form of thousands of separate text files. Each text file has several hundred retrieved profiles, typically from two orbits around Mars. All of the metadata is in the same files as the profile data, meaning that in order to find profiles at a specific location or time, it is necessary to read many text files. 

Working with the data in this form is inefficient, so mcspy makes it easy to download data from a range of dates, and then save the metadata and the profiles in binary numpy array files.

## Requirements
* numpy
* pandas
* requests (can substitute ftplib if necessary)



