prototypes work for 
python 2.7

they MIGHT work for python 3.?
i know prototype_tkinter.py does mostly work on python 3.4 (there's a small
error with bringing pyplot windows to the front), but i haven't tested 
anything with kivy in python 3.

some prototypes to play around with dice
these are assuming you've done
>>> pip install dicetables

prototype_tkinter.py:
   required modules: tkinter, matplotlib
   matplotlib is handy, but can be a pain to install. here's the link
   	http://matplotlib.org/users/installing.html
   
   tkinter should be a standard library. if you are using a mac, go to this website
        https://www.python.org/download/mac/tcltk/

   to run 
   >>> python prototype_tkinter.py



prototype_kivy_wide.py
prototype_kivy_tabbed.py
    required modules: kivy, kivy garden.graph
       https://kivy.org/docs/installation/installation.html
    for garden:
    >>> pip install kivy-garden
    >>> garden install graph
    >>> garden install --upgrade graph

    to run
    >>> python prototype_kivy_wide.py  

ui_text_only.py
CURRENTLY BUGGY. WHEN IT IS FIXED THIS WILL BE REMOVED.
(haven't fixed it bcuz the others are better)

    required modules: matplotlib
    runs in a python interpreter or command line
    
    to run
    >>> python ui_text_only.py 