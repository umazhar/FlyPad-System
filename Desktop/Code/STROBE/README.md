# Sip TRiggered Optogenetic Behavior Enclosure (STROBE) Software and Source
This repository contains the UI source and executable, and Python post-processing scripts for the STROBE device.

The STROBE UI was built in Visual Studios 2012 in C++ on Windows 10. It will require installation of Qt 5.11 in order to compile. Included in the source are all 3rd party modules ([FTD2XX](http://www.ftdichip.com), [qtcustomplot](https://www.qcustomplot.com/), etc) needed to compile the executable. Packet decoding snippet in C++ UI modified from [Bonsai.Neuro/FlyPad](https://github.com/rcwchan/STROBE_software/blob/master/STROBE_UI_source/QtGuiApplication4/main.cpp).
