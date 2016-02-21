from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty

import dicestats as ds
import graphing_and_printing as gap
import random
import pylab 
class StatBox(BoxLayout):
    def __init__(self, **kwargs):
        super(StatBox, self).__init__(**kwargs)
        self.table=ds.DiceTable()
    def assign_text_value(self, box='start'):
        val_min, val_max = self.table.values_range()
        change_str = self.ids[box + '_slider_text'].text
        if change_str != '':
            if int(change_str) < val_min:
                val_new = val_min
            elif int(change_str) > val_max:
                val_new = val_max
            else:
                val_new = int(change_str)
            self.ids[box+'_slider'].value = val_new 
            self.ids[box + '_slider_text'].text = str(val_new)       
        self.show_stats()
    def assign_table(self, table):
        self.table = table
    def assign_limits(self):
        val_min, val_max = self.table.values_range()
        self.ids['stop_slider'].min = val_min
        self.ids['start_slider'].min = val_min
        self.ids['stop_slider'].max = val_max
        self.ids['start_slider'].max = val_max
    def show_stats(self):
        val_1 = int(self.ids['stop_slider'].value)
        val_2 = int(self.ids['start_slider'].value)
        if val_1 > val_2:
            stat_list = range(val_2, val_1 + 1)
        else:
            stat_list = range(val_1, val_2 + 1)
        new_text = gap.stats(self.table, stat_list).replace(' possible', '')
        self.ids['stat_text'].text = new_text
class ScrollLabel(ScrollView):
    text = StringProperty('')
class WeightPopup(Popup):
    pass
        
class HorSlider(BoxLayout):
    pass
    def write_label(self, text):
        self.ids['hor_title'].text = text
    def get_value(self):
        return int(self.ids['hor_slider'].value)

class DicePlatform(BoxLayout):
    def __init__(self, **kwargs):
        super(DicePlatform, self).__init__(**kwargs)
        self.table = ds.DiceTable()
        self.counter = 5
        self.use_weights = False
        self.weight_dictionary = {}
        self.ids['the_stat_box'].assign_table(self.table)

    def make_shit(self):
        use_frame = self.ids['add_new']
        for count in range(self.counter):
            use_frame.add_widget(Button(text=str(count)))
    def use_shit(self):
        use_frame = self.ids['add_new']
        for child in use_frame.children[:]:
            if isinstance(child, Button) and child.text != 'pop':
                use_frame.remove_widget(child)
    def do_it(self):
        self.table.add_die(random.randint(1, 5), ds.Die(6))
        self.updater()
    def graph_it(self, new=False):
        points = ('o', '<', '>', 'v', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd')
        colors = ('b', 'g', 'y', 'r', 'c', 'm', 'y', 'k')
        the_style = random.choice(points) + '-' + random.choice(colors)
        if new:
            figure_obj = pylab.figure(1)
            fig_num = 1
            pylab.clf()
        else:
            figure_obj = pylab.figure(0)
            fig_num = 0 
        gap.fancy_grapher_pct(self.table, figure=fig_num, style=the_style, legend=True)
        pylab.pause(0.1)
        figure_obj.canvas.manager.window.activateWindow()
        figure_obj.canvas.manager.window.raise_()
    def clear_graph(self):
        figure_obj = pylab.figure(0)
        pylab.cla()
        pylab.pause(0.1)
        figure_obj.canvas.manager.window.activateWindow()
        figure_obj.canvas.manager.window.raise_()        
#generally ok.  layout sux        
    def weight_it(self):
        self.weight_popup = WeightPopup()
        self.weight_popup.open()
        box = self.weight_popup.ids['pop_up_frame']
        for count in range(5):
            temp = HorSlider()
            temp.write_label('hah' + str(count))
            box.add_widget(temp)
#record_weight ok    
    def record_weight(self):
        count = 1
        self.use_weights = True
        for widget in self.weight_popup.ids['pop_up_frame'].children[:]:
            if isinstance(widget, HorSlider):
                self.weight_dictionary[count] = widget.get_value()
            count += 1
        if sum(self.weight_dictionary.values()) == 0:
            self.use_weights = False
        self.weight_popup.dismiss()
        #print self.weight_dictionary
    def updater(self):
        self.ids['the_stat_box'].assign_limits()
        self.ids['all_rolls_label'].text = gap.print_table_string(self.table)
class DiceTableApp(App):
    def build(self):
        return DicePlatform()
        
if __name__ == '__main__':
    DiceTableApp().run()