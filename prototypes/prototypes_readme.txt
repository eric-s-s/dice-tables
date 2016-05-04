some prototypes to play around with dice
these are assuming you've done
>>> pip install dicetables

prototype_tkinter.py:
   required modules: tkinter, matplotlib
   try
   >>> pip install matplotlib
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