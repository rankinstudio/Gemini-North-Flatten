# Gemini-North-Flatten

![](prev.JPG)

A small program to assemble raw Gemini North data into a single fits file for programs like astrometrica or tycho-tracker.

usage: fixgem.py 'dir' -prefix 'prefix'

This will assembling the data channels and flatten the image into a single data channel fits preserving the image gaps. They can then be solved in astrometrica. It does a few other tweaks to fix the time, sky location, and crops out empty data.

Requires astropy and numpy.
