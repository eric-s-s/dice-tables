import Tkinter as tk
import dicestats as ds
import graphing_and_printing as gap
import random

class App:
    def __init__(self, master):
        info_frame = tk.Frame(master)
        info_frame.pack(side=tk.LEFT)
        
        frame = tk.Frame(master)
        frame.pack(side=tk.LEFT)
        
        add_frame = tk.Frame(master)
        add_frame.pack(side=tk.LEFT)
        
        remove_frame = tk.Frame(master)
        remove_frame.pack(side=tk.LEFT)
        
        stat_graph_frame = tk.Frame(master)
        stat_graph_frame.pack(side=tk.LEFT)
        
        all_info_frame = tk.Frame(master)
        all_info_frame.pack(side=tk.LEFT)
        
        self.table = ds.DiceTable()
        
        #infoframe
        self.button = tk.Button(
            info_frame, text='QUIT', fg='red', command=info_frame.quit)
        self.button.grid(sticky=tk.E)
        
        self.table_string = tk.StringVar()
        self.table_label = tk.Label(info_frame, textvariable=self.table_string)
        self.table_label.grid(row=1, sticky=tk.W)
        self.table_string.set(str(self.table))
        
        self.stats_string = tk.StringVar()
        self.stats_label = tk.Label(info_frame, textvariable=self.stats_string)
        self.stats_label.grid(row=1, column=1, sticky=tk.N)
        self.stats_string.set(self.stats_string_maker(self.table))
        
        #frame frame
        self.hi_there = tk.Button(frame, text='hello', command=self.say_hi)
        self.hi_there.pack(side=tk.BOTTOM)
        
        self.do_it = tk.Button(frame, text='do it', command = self.do_a_thing)
        self.do_it.pack(side=tk.LEFT)
    
        self.listbox = tk.Listbox(frame)
        self.listbox.pack(side=tk.LEFT)
        
        self.listbox.insert(tk.END, 'an entry')
        for item in ['one', '2', '3']:
            self.listbox.insert(tk.END, item)
        
        #stat_graph_frame
        self.graph_button = tk.Button(stat_graph_frame, text='graph',
                                      command=self.graphit)
        self.graph_button.pack(side=tk.TOP)
        
        #all_info_frame
        self.text_scrollbar = tk.Scrollbar(all_info_frame)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box = tk.Text(all_info_frame, width=20, 
                                yscrollcommand=self.text_scrollbar.set)
        self.text_box.pack()
        self.text_scrollbar.config(command=self.text_box.yview)

        
       
    def say_hi(self):
        print 'hi there'
    
    def graphit(self):
        gap.fancy_grapher(self.table, figure=2)    
    def do_a_thing(self):
        self.text_box.delete(1.0, tk.END)
        self.table.add_die(5, ds.Die(random.randint(1, 15)))
        self.table_string.set(str(self.table))
        self.stats_string.set(self.stats_string_maker(self.table))
        self.text_box.insert(tk.END, gap.print_table_string(self.table))
        gap.fancy_grapher_pct(self.table, legend=True, figure=1)
    def stats_string_maker(self, table):
        out = ('the range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
               % (table.values_min(), table.values_max(), table.mean(), 
               table.stddev()))
        return out
root = tk.Tk()
app = App(root)

root.mainloop()
root.destroy()