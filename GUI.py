import Tkinter as tk
import dicestats as ds
import graphing_and_printing as gap
import random

class App:
    def __init__(self, master):
        self.info_frame = tk.Frame(master)
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.info_frame.config(borderwidth=5, relief=tk.GROOVE)

        self.change_frame = tk.Frame(master)
        self.change_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.change_frame.config(borderwidth=5, relief=tk.GROOVE)

        self.add_frame = tk.Frame(master)
        self.add_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.add_frame.config(borderwidth=5, relief=tk.GROOVE)

        self.stat_graph_frame = tk.Frame(master)
        self.stat_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.stat_graph_frame.config(borderwidth=5, relief=tk.GROOVE)

        self.all_info_frame = tk.Frame(master)
        self.all_info_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.all_info_frame.config(borderwidth=5, relief=tk.GROOVE)

        self.table = ds.DiceTable()
        self.use_weights = False
        self.weight_dictionary = {1:0}
        self.weight_widgets = []
        self.change_widgets = []
        #infoframe
        self.quit_button = tk.Button(self.info_frame, text='QUIT', fg='red',
                                     command=self.info_frame.quit, bg='light yellow')
        self.quit_button.grid(row=1, sticky=tk.W)

        self.new_button = tk.Button(self.info_frame, text='NEW TABLE', bg='light yellow',
                                    command=self.restart_table)
        self.new_button.grid(row=0)

        self.table_string = tk.StringVar()
        self.table_label = tk.Label(self.info_frame, textvariable=self.table_string)
        self.table_label.grid(row=2, column=1, sticky=tk.W)
        self.table_string.set(str(self.table))

        self.stats_string = tk.StringVar()
        self.stats_label = tk.Label(self.info_frame, textvariable=self.stats_string)
        self.stats_label.grid(row=1, column=1, sticky=tk.N)
        self.stats_string.set(self.stats_string_maker(self.table))

        self.weight_text_scrollbar = tk.Scrollbar(self.info_frame)
        self.weight_text_scrollbar.grid(row=3, column=2, ipady=50)
        self.weight_text_box = tk.Text(self.info_frame, width=35, height=10,
                                       yscrollcommand=self.weight_text_scrollbar.set)
        self.weight_text_box.grid(row=3, column=0, columnspan=2)
        self.weight_text_scrollbar.config(command=self.weight_text_box.yview)
        self.weight_text_box.insert(tk.END, 'here is full weight info\n')
        #change_frame

        self.update_change_frame()
        self.add_rm_button = tk.Button(self.change_frame, text='add/remove',
                                       bg='pale turquoise', command=self.add_rm)
        self.add_rm_button.pack()


        #add_frame
        self.num_dice_scale = tk.Scale(self.add_frame, from_=0, to=50, orient=tk.VERTICAL,
                                       label='how many dice', troughcolor='light yellow')
        self.num_dice_scale.grid(column=0, row=0, sticky=tk.W)

        self.die_size_scale = tk.Scale(self.add_frame, from_=1, to=100, length=200,
                                       label='size of dice', troughcolor='light yellow')
        self.die_size_scale.grid(column=0, row=1, sticky=tk.W, rowspan=2)

        self.die_modifier_scale = tk.Scale(self.add_frame, from_=-5, to=5,
                                           orient=tk.HORIZONTAL, label='die modifier',
                                           troughcolor='light yellow')
        self.die_modifier_scale.grid(column=1, row=0, sticky=tk.N+tk.W)

        self.add_weights_button = tk.Button(self.add_frame, text='weight the die',
                                            command=self.add_weights, bg='light yellow')
        self.add_weights_button.grid(column=1, row=1, sticky=tk.N+tk.W)

        self.add_new_button = tk.Button(self.add_frame, text='YES!\nADD IT!',
                                        fg='red', width=10, height=5,
                                        bg='pale turquoise', command=self.add_new)
        self.add_new_button.grid(column=1, row=2)

        self.d2 = tk.Button(self.add_frame, text='D2', command=lambda: self.set_size(2))
        self.d4 = tk.Button(self.add_frame, text='D4', command=lambda: self.set_size(4))
        self.d6 = tk.Button(self.add_frame, text='D6', command=lambda: self.set_size(6))
        self.d8 = tk.Button(self.add_frame, text='D8', command=lambda: self.set_size(8))
        self.d10 = tk.Button(self.add_frame, text='D10', command=lambda: self.set_size(10))
        self.d12 = tk.Button(self.add_frame, text='D12', command=lambda: self.set_size(12))
        self.d20 = tk.Button(self.add_frame, text='D20', command=lambda: self.set_size(20))
        self.d100 = tk.Button(self.add_frame, text='D100', command=lambda: self.set_size(100))

        self.d2.grid(row=3, column=0)
        self.d4.grid(row=4, column=0)
        self.d6.grid(row=5, column=0)
        self.d8.grid(row=6, column=0)
        self.d10.grid(row=3, column=1)
        self.d12.grid(row=4, column=1)
        self.d20.grid(row=5, column=1)
        self.d100.grid(row=6, column=1)

        #stat_graph_frame
        self.graph_button = tk.Button(self.stat_graph_frame, text='graph',
                                      command=self.graph_it, bg='light yellow')
        self.graph_button.grid(row=2, column=1, pady=30)
        self.stats_button = tk.Button(self.stat_graph_frame, text='stats',
                                      command=self.stats_it, bg='light yellow')
        self.stats_button.grid(row=2, column=0, pady=30)
        self.stats_label1 = tk.Label(self.stat_graph_frame,
                                     text='assign star/stop\nand click button for stats')
        self.stats_label1.grid(row=0, column=0, pady=30)
        self.stats_label2 = tk.Label(self.stat_graph_frame,
                                     text='click graph button\nfor graph')
        self.stats_label2.grid(row=0, column=1, pady=30)
        self.stats_start = tk.Scale(self.stat_graph_frame, label='stats start value')
        self.stats_stop = tk.Scale(self.stat_graph_frame, label='stats stop value')
        self.stats_start.grid(row=1, column=0)
        self.stats_stop.grid(row=1, column=1)
        self.stats_text_box = tk.Text(self.stat_graph_frame, width=60, height=20)
        self.stats_text_box.grid(row=3, column=0, columnspan=2)
        #all_info_frame
        self.all_info_label = tk.Label(self.all_info_frame, fg='white', bg='blue',
                                       text=('here are all the rolls\n'+
                                             'and their frequency'))
        self.all_info_label.pack()
        self.text_scrollbar = tk.Scrollbar(self.all_info_frame)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box = tk.Text(self.all_info_frame, width=20, height=30,
                                yscrollcommand=self.text_scrollbar.set)
        self.text_box.pack()
        self.text_scrollbar.config(command=self.text_box.yview)



    def graph_it(self):
        points = ('o', '<', '>', 'v', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd')
        colors = ('b', 'g', 'y', 'r', 'c', 'm', 'y', 'k')
        the_style = random.choice(points) + '-' + random.choice(colors)
        gap.fancy_grapher_pct(self.table, figure=2, style=the_style, legend=True)
    def stats_it(self):
        start = self.stats_start.get()
        stop = self.stats_stop.get()
        if start < stop:
            input_lst = range(start, stop + 1)
        else:
            input_lst = range(stop, start + 1)
        self.stats_text_box.delete(1.0, tk.END)
        self.stats_text_box.insert(tk.END, gap.stats(self.table, input_lst))

    def restart_table(self):
        self.table = ds.DiceTable()
        self.mutate_labels()
        self.update_change_frame()
    def stats_string_maker(self, table):
        out = ('the range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
               % (table.values_min(), table.values_max(), table.mean(),
                  table.stddev()))
        return out
    def set_size(self, number):
        self.die_size_scale.set(number)
    def add_weights(self):
        self.weight_dictionary = {0:1}
        self.weight_widgets = []
        self.weight_window = tk.Toplevel()
        self.weight_frame = tk.Frame(self.weight_window)
        self.weight_frame.pack()
        #self.weight_window.maxsize(height=100, width=1000)
        self.weight_window.title('makin weights')
        use_row = 0
        use_column = 0
        for roll in range(1, self.die_size_scale.get() + 1):
            if roll%12 == 1 and roll != 1:
                use_column += 1
                use_row = 0
            scale = tk.Scale(self.weight_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                             label='weight for' + str(roll))
            scale.set(1)
            scale.grid(column=use_column, row=use_row)
            self.weight_widgets.append(scale)
            use_row += 1
        enter_weights = tk.Button(self.weight_frame, command=self.record_weights,
                                  text='RECORD\nWEIGHTS', height=5, width=10,
                                  bg='pale turquoise', fg='red')
        enter_weights.grid()
    def record_weights(self):
        count = 1
        self.use_weights = True
        for widget in self.weight_widgets:
            self.weight_dictionary[count] = widget.get()
            count += 1
        #dic_disp = tk.Label(self.add_frame, text=str(self.weight_dictionary))
        #dic_disp.grid()
        self.weight_window.destroy()
    def add_new(self):
        #num_dice_scale+die_size_scale+die_modifier_scale
        mod = self.die_modifier_scale.get()
        if self.use_weights:
            if mod == 0:
                the_die = ds.WeightedDie(self.weight_dictionary)
            else:
                the_die = ds.ModWeightedDie(self.weight_dictionary, mod)
        else:
            size = self.die_size_scale.get()
            if mod == 0:
                the_die = ds.Die(size)
            else:
                the_die = ds.ModDie(size, mod)
        num_dice = self.num_dice_scale.get()
        self.table.add_die(num_dice, the_die)
        self.mutate_labels()
        self.update_change_frame()
        self.use_weights = False

    def add_rm(self):
        for scale, die in self.change_widgets:
            if scale.get() < 0:
                self.table.remove_die(abs(scale.get()), die)
            if scale.get() > 0:
                self.table.add_die(scale.get(), die)
        self.mutate_labels()
        self.update_change_frame()

    def mutate_labels(self):

        self.table_string.set(str(self.table))
        self.stats_string.set(self.stats_string_maker(self.table))
        self.weight_text_box.delete(1.0, tk.END)
        self.weight_text_box.insert(tk.END, ('here is full weight info\n\n' +
                                             self.table.weights_info()))

        val_min, val_max = self.table.values_range()
        self.stats_start.config(from_=val_min, to=val_max)
        self.stats_stop.config(from_=val_min, to=val_max)

        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, gap.print_table_string(self.table))



    def update_change_frame(self):
        for scale, die in self.change_widgets:
            scale.destroy()
        self.change_widgets = []
        for die, number in self.table.get_list():
            scale_label = die.multiply_str(number)
            max_remove = 20
            max_add = 20
            if number < max_remove:
                max_remove = number
            scale = tk.Scale(self.change_frame, from_=-1 * max_remove, to=max_add,
                             orient=tk.HORIZONTAL, label=scale_label)
            scale.pack()
            self.change_widgets.append((scale, die))





root = tk.Tk()
app = App(root)

root.mainloop()
root.destroy()
