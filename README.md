Tested on python3.4.
====================

Requirements for running the script

1) Python
2) Cerealizer

Installing Cerealizer:
  pip install cerealizer
  pip install matplotlib

Loading the shares:
  python load.py shares_file_location
  Now the variable "allshares" contains:
  - index 0 shares for the first person
  - index 1 shares for the second person
  - and so on


One can modify load.py script to play around with the shares

Usage
==========

    Fetches all files from test_data and applied sharing scheme w.r.t to get_shares.py
    (currently 4 2)

    $ python get_shares.py test_data/ correct_shamir | aloneh

    After fetching the serialized files can be found in new_version/ folder


Statistics
===========
    Plots graphs from the hex files with the shares computed at the previous steps.

    $ python diff.py new_version/CV_BG.hex new_version/CV_DK.hex new_version/DM_RO.hex 4000




