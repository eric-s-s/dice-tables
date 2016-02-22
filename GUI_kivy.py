from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
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
    pass
    def set_text(self, new_text, new_font_size):
        page_height = 600
        height_buffer = 120
        def splitter(text, line_limit):
            text = text.rstrip('\n')
            lines = text.split('\n')
            num_lines = len(lines)
            out = []
            if num_lines % line_limit == 0:
                pages = num_lines // line_limit
            else:
                pages = num_lines // line_limit + 1
            for count in range(0, (pages - 1)*line_limit, line_limit):
                page = '\n'.join(lines[count:count+line_limit])
                out.append(page)    
            last_page = lines[(pages - 1)*line_limit:]
            extra_lines = (line_limit - len(last_page)) * [' ']
            last_page = '\n'.join(last_page + extra_lines)  
            out.append(last_page)
            return out
        pages = splitter(new_text, page_height//new_font_size)
        container = self.ids['page_container']
        for child in container.children[:]:
            container.remove_widget(child)
        container.height = (page_height + height_buffer) * len(pages)
        for page in pages:
            container.add_widget(Label(text=page, font_size=new_font_size, valign='top', 
                                       size_hint_y=1./len(pages), text_size=(self.width, None)))
            
class WeightPopupContents(StackLayout):
    pass
    #def assign_cols(self, col):
    #    self.cols = col   
    def assign_sliders(self, die_size):
        #self.assign_cols(die_size//10 + 1)
        for roll in range(1, die_size + 1):
            slider = HorSlider(size_hint=(None,0.1), width=150)
            slider.write_holder(roll)
            slider.write_label('weight for ' + str(roll))
            self.add_widget(slider)
    def return_dictionary(self):
        out = {}
        for child in self.children[:]:
            if isinstance(child, HorSlider):
                roll = child.get_holder()
                out[roll] = int(child.get_value())
        return out.copy()
class HorSlider(BoxLayout):
    def __init__(self, **kwargs):
        super(HorSlider, self).__init__(**kwargs)
        self.holder=None
    def write_label(self, text):
        self.ids['hor_title'].text = text
    def write_holder(self, new_val):
        self.holder = new_val
    def get_holder(self):
        out = self.holder
        return out
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
        size = int(self.ids['blah'].value)
        cell_size = 150
        popup_width = cell_size*(size//10 + 1) 
        self.contents = WeightPopupContents()
        size_limit = 600
        pad_size = size_limit + 60
        if popup_width > size_limit:
            self.contents.size_hint = (None, None)
            new_width = cell_size * ((size+2)//10 +1)
            that_way = Label(text='[b]DRAG\n====>[/b]', size_hint=(None, None), 
                             size=(100, 50), font_size=20, markup=True) 
            self.contents.add_widget(that_way)
            self.contents.assign_sliders(size)
            def wrapper(instance):
                self.record_weight()
            self.second_button = Button(text='record\nweights', size_hint=(None, None), 
                                  size=(100, 50), on_press=wrapper) 
            self.contents.add_widget(self.second_button)
            self.contents.size = (new_width, size_limit)
            scroller = ScrollView(size_hint=(None, None), size=(size_limit, size_limit),
                                  scroll_timeout=70)
            scroller.add_widget(self.contents)
            self.weight_popup = Popup(title='weight', content=scroller, 
                                  size_hint=(None, None),size=(pad_size, pad_size))
        else:
            self.contents.assign_sliders(size)
            self.weight_popup = Popup(title='weight', content=self.contents, 
                                      size_hint=(None, None),
                                      size=(popup_width, size_limit))
        self.weight_popup.open()
        
#record_weight ok    
    def record_weight(self):
        self.weight_dictionary = self.contents.return_dictionary()
        self.use_weights = True
        print self.weight_dictionary
        if sum(self.weight_dictionary.values()) == 0:
            self.use_weights = False
        self.weight_popup.dismiss()

    def updater(self):
        self.ids['the_stat_box'].assign_limits()
        self.ids['all_rolls_label'].set_text(gap.print_table_string(self.table), 15)
        
        #self.ids['all_rolls_label'].text = gap.print_table_string(self.table)
class DiceTableApp(App):
    def build(self):
        return DicePlatform()
        
if __name__ == '__main__':
    DiceTableApp().run()