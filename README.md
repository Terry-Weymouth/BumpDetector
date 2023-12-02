# BumpDetector
Code, collected data, and results related to a bicycle mounted road-roughness project.

Specifically, given a GPS trace (series of GPS readings for a moving vehicle):
* code to insert the trace data into a Postgres database
* code to match trace to streets in an Open Street View map (e.g. map matching)
* code to plot route from map-matched points
* code to plot data along route (in the case herein, accelerometer data)

A work in progress!

See related project on using a Raspberry PI to collect the data with sensors mounted on a bicycle,
reference in file RunningDetectorOnPi.txt