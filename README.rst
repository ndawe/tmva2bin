
Convert TMVA BDT XML files into small binary or text files.

Dependencies
------------

This package depends on:

* rootpy https://github.com/rootpy/rootpy

To download and install ootpy::

   git clone git://github.com/rootpy/rootpy.git
   python rootpy/setup.py install --user


Install
-------

To install tmva2bin::

   git clone git://github.com/ndawe/tmva2bin.git
   python setup.py install --user


Usage
-----

See the help::

   tmva2bin -h
   usage: tmva2bin [-h] [-f {txt,bin,root}] [-m {BDT,CUTS,TRANS}] [-c CATEGORIES]
                   [-o OUTPUT] [-b]
                   files [files ...]

   positional arguments:
     files

   optional arguments:
     -h, --help            show this help message and exit
     -f {txt,bin,root}, --format {txt,bin,root}
                           Output format
     -m {BDT,CUTS,TRANS}, --method {BDT,CUTS,TRANS}
                           Type of tree: BDT, CUTS, or TRANS
     -c CATEGORIES, --categories CATEGORIES
                           Category string e.g. {ET:F|60000}x{numTrack:I|1}
     -o OUTPUT, --output OUTPUT
                           name of output file
     -b, --batch           convert multiple files separately (do not combine them
                           into one binned file)

For example::

   tmva2bin -f bin TMVAClassification_BDT.weights.xml
   INFO:tmva2bin] reading input ...
   INFO:tmva2bin] writing output ...
   INFO:tmva2bin] done
