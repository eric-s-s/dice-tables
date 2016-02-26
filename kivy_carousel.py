from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.clock import Clock

import dicestats as ds
import graphing_and_printing as gap
import random
import pylab 

#tools

#class SimpleSlider(Slider):
#    def __init__(self, **kwargs):
#        super(SimpleSlider, self).__init__(**kwargs)
#    def on_touch_move(self, touch):
#        if self.collide_point(*touch.pos):
#        # The touch has occurred inside the widgets area. Do stuff!
#            pass
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
class FlashButton(Button):
    def __init__(self, **kwargs):
        super(FlashButton, self).__init__(**kwargs)
        self.bind(on_press=self.long_press)
    def long_press(self, *args):
        self.color = [1,0,0,1]
        self.background_color = [0.2,0.2,1,1]
        Clock.schedule_once(self.callback, 0.5)
    def callback(self, dt):
        self.color=[1,1,1,1]
        self.background_color = [1,1,1,1]
class FlashLabel(Button):
    def __init__(self, do_flash=True, **kwargs):
        super(FlashLabel, self).__init__(**kwargs)
        self.background_normal=''
        self.do_flash = do_flash
    def add_text(self, text):
        self.text = text
        self.color=[1,1,1,1]
        self.background_color = [0,0,0,0]
        if self.do_flash:
            self.color = [1,0,0,1]
            self.background_color = [0.2,0.2,1,0.2]
            Clock.schedule_once(self.callback, 0.8)
    def callback(self, dt):
        self.color=[1,1,1,1]
        self.background_color = [0,0,0,0]

class PlusMinusButton(FlashButton):
    def __init__(self, number, **kwargs):
        super(PlusMinusButton, self).__init__(**kwargs)
        self.number = number
        self.text = '{:+}'.format(self.number)

class SizeButton(FlashButton):
    die_size = NumericProperty(1)
        
class PageBox(BoxLayout):
    def __init__(self, **kwargs):
        super(PageBox, self).__init__(**kwargs)
        self.pages = ['']
        self.current_page = 0
        self.font_size = 15
    def reset_sizes(self, f_size, ratios):
        self.ids['jump_to'].font_size= f_size
        self.ids['page_box_title'].size_hint_y = ratios[0]
        self.ids['buttons_container'].size_hint_y = ratios[1]
        self.ids['text_container'].size_hint_y = ratios[2]  
    def set_title(self, title):
        self.ids['page_box_title'].text = title
    def show_page(self, number):
        number = number % len(self.pages)
        self.current_page = number
        self.ids['text_container'].text = self.pages[number]
        self.ids['text_container'].font_size =  self.font_size
        self.ids['text_container'].text_size = self.ids['text_container'].size
        self.ids['jump_to'].text = str(number + 1)
    def set_text(self, new_text, new_font_size, fudge_factor):
        self.font_size = new_font_size
        page_height = self.height
        new_line_limit = int(fudge_factor * page_height/ float(new_font_size))
        def page_maker(text, line_limit):
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
            return out[:]
        self.pages = page_maker(new_text, new_line_limit)
        self.ids['page_total'].text = '/%s' % (len(self.pages))
        self.show_page(self.current_page)

class AddRmDice(BoxLayout):
    def __init__(self, parent_app, number, die, only_add=False, do_flash=True, **kwargs):
        super(AddRmDice, self).__init__(**kwargs)
        self._number = number
        self._die = die
        self.parent_app = parent_app
        self.only_add = only_add
        self.do_flash = do_flash
        self.small = 20
        self.medium = 100
        self.update()
    def assign_die(self, number, die):
        self._die = die
        self._number = number
        self.update()
    def addrm(self, btn):
        times = btn.number
        if times < 0:
            self.parent_app.remove(abs(times), self._die)
        else:
            self.parent_app.add(times, self._die)
    def update(self):
        self.clear_widgets()
        if self._die.get_size() < self.small:
            buttons = 3
        elif self.small <= self._die.get_size() < self.medium:
            buttons = 2
        else:
            buttons = 1
        sz_hnt_x = round(1./(2*buttons + 2), 2)
        if not self.only_add:
            for number in range(buttons - 1, -1, -1):
                btn = PlusMinusButton(-10**number, size_hint=(sz_hnt_x, 1))
                btn.bind(on_press=self.addrm)
                self.add_widget(btn)
        if self._number == 0:
            die_string = str(self._die)
        else:
            die_string = self._die.multiply_str(self._number)
        flash = FlashLabel(do_flash=self.do_flash)
        flash.size_hint=(sz_hnt_x*2, 1)
        self.add_widget(flash)
        flash.add_text(die_string)
        for number in range(buttons):
            btn = PlusMinusButton(10**number, size_hint=(sz_hnt_x, 1))
            btn.bind(on_press=self.addrm)
            self.add_widget(btn)

#big_boxes
class ChangeBox(GridLayout):
    def __init__(self, parent_app, **kwargs):
        super(ChangeBox, self).__init__(**kwargs)
        self.parent_app = parent_app
        self.cols = 1
        self.old_dice_list = []
    #def update(self):
    #    Clock.schedule_once(self.delay_update, 0.8)
    def update(self):
        dice_list = self.parent_app.request_info('dice_list')
        self.clear_widgets()
        new_height = 70
        if dice_list:
            new_height = min(self.height / len(dice_list), new_height) 
        for die, number in dice_list:
            if (die, number) in self.old_dice_list:
                changed = False
            else:
                changed = True
            self.add_rm = AddRmDice(self, number, die, do_flash=changed, size_hint=(1,None), height=new_height)
            self.add_widget(self.add_rm)
        self.old_dice_list = dice_list    
    def add(self, number, die, *args):
        Clock.schedule_once(lambda dt: self.delayed_add(number, die, *args), 0.5)
    def delayed_add(self, number, die, *args):
        self.parent_app.request_add(number, die)
    def remove(self, number, die, *args):
        Clock.schedule_once(lambda dt: self.delayed_remove(number, die, *args), 0.5)
    def delayed_remove(self, number, die, *args):
        self.parent_app.request_remove(number, die)    
    
class AddBox(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super(AddBox, self).__init__(**kwargs)
        self.parent_app = parent_app
        self.mod = 0
        self.dictionary = {}
        self.die_size = 6
        self.use_weights = False
        
        self.add_it = AddRmDice(self, 0, ds.Die(6), only_add=True, size_hint=(1, 1))
        self.pack()
    def pack(self):
        self.ids['add_it'].add_widget(self.add_it)
        for number in [2, 4, 6, 8, 10, 12, 20, 100]:
            btn = SizeButton(die_size=number)
            btn.bind(on_press=self.assign_size_btn)
            self.ids['presets'].add_widget(btn) 
    def assign_size_btn(self, btn):
        self.die_size = btn.die_size
        self.assign_die()
    
    def assign_mod(self):
        self.mod = int(self.ids['modifier'].value)
        self.assign_die()
    def assign_die(self):
        if self.use_weights:
            if self.mod == 0:
                die = ds.WeightedDie(self.dictionary)
            else:
                die = ds.ModWeightedDie(self.dictionary, self.mod)
        else:
            if self.mod == 0:
                die = ds.Die(self.die_size)
            else:
                die = ds.ModDie(self.die_size, self.mod)
        self.add_it.assign_die(0, die)
    def add(self, number, die, *args):
        Clock.schedule_once(lambda dt: self.delayed_add(number, die, *args), 0.5)
    def delayed_add(self, number, die, *args):
        self.parent_app.request_add(number, die)
    def remove(self, number, die, *args):
        Clock.schedule_once(lambda dt: self.delayed_remove(number, die, *args), 0.5)
    def delayed_remove(self, number, die, *args):
        self.parent_app.request_remove(number, die)        
    


class InfoBox(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super(InfoBox, self).__init__(**kwargs)
        self.parent_app = parent_app
    #def set_info_box(self):
        self.ids['weight_info'].reset_sizes(15, [0.1, 0.1, 0.8])
        self.ids['weight_info'].set_title('full weight info')
    def update(self):
        values_min, values_max = self.parent_app.request_info('range')
        mean, stddev = self.parent_app.request_info('mean_stddev')
        stat_text = ('the range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
               % (values_min, values_max, round(mean, 4), stddev))
        self.ids['stat_str'].text = stat_text
        
        self.ids['dice_table_str'].text = self.parent_app.request_info('table_str')
        self.ids['weight_info'].set_text(self.parent_app.request_info('weights_info'), 15, 0.65) 

class GraphBox(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super(GraphBox, self).__init__(**kwargs)
        self.parent_app = parent_app


class StatBox(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super(StatBox, self).__init__(**kwargs)
        self.parent_app = parent_app
        self.text_lines = 1
        #self.ids['stat_text'].font_size = (lambda:self.ids['stat_text'].height//15)()
        #self.ids['stat_text'].height = 1
        #self.bind(on_texture_size = self.font_sizer)
    def update(self):
        val_min, val_max = self.parent_app.request_info('range')
        self.ids['stop_slider'].min = val_min
        self.ids['start_slider'].min = val_min
        self.ids['stop_slider'].max = val_max
        self.ids['start_slider'].max = val_max        

    def assign_text_value(self, box='start'):
        val_min, val_max = self.parent_app.request_info('range')
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

    def show_stats(self):
        val_1 = int(self.ids['stop_slider'].value)
        val_2 = int(self.ids['start_slider'].value)

        stat_list = range(min(val_1, val_2), max(val_1, val_2) + 1)
        new_text = '\n' + self.parent_app.request_info('stats', stat_list).replace(' possible', '')
        text_lines = new_text.count('\n') + 1
        new_font_size = min(0.7 * self.ids['stat_text'].height//text_lines, 
                            int(0.08*self.ids['stat_text'].width))

        self.ids['stat_text'].font_size = min(new_font_size, 15)
        self.ids['stat_text'].text = new_text        
class AllRollsBox(PageBox):
    def __init__(self, parent_app, **kwargs):
        PageBox.__init__(self)
        self.parent_app = parent_app
        self.set_title('here are all the rolls and their frequency')
    def update(self):
        text = self.parent_app.request_info('all_rolls')
        self.set_text(text, 15, 0.65)
#class AllRollsBox(BoxLayout):
#    def __init__(self, parent_app, **kwargs):
#        super(AllRollsBox, self).__init__(**kwargs)
#        self.parent_app = parent_app
#        self.ids['all_rolls'].set_title('here are all the rolls\nand their frequency')
#
#    def update(self):
#        text = self.parent_app.request_info('all_rolls')
#        self.ids['all_rolls'].set_text(text, 15, 0.65)    

        
class DicePlatform(Carousel):
    def __init__(self, **kwargs):
        super(DicePlatform, self).__init__(**kwargs)
        self._table = ds.DiceTable()
        self.counter_temp_thing = 5
        self.use_weights = False
        self.weight_dictionary = {}

        self.bind_children()
        self.pack_children()
        self.direction='right'
        self.loop='true'
        self.scroll_timeout = 120

    
    def bind_children(self):
        self.stats = StatBox(self, size_hint=(1, 0.8))
        self.graphs = GraphBox(self, size_hint=(1, 0.2))
        
        self.changer = ChangeBox(self, size_hint=(0.5, 1))
        self.add_box = AddBox(self, size_hint=(0.5, 1))
        
        self.basic_info = InfoBox(self, size_hint=(0.5, 1))
        self.graph_stat = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        
        self.change_add = BoxLayout(orientation='horizontal')
        self.stat_basic = BoxLayout(orientation='horizontal')
        
        self.all_rolls = AllRollsBox(self)
               
        
        
    def pack_children(self):
        '''  change_box | add_box | basic_info | graphs |all_rolls
                                               | stats             '''
        self.graph_stat.add_widget(self.graphs)
        self.graph_stat.add_widget(self.stats)
        
        self.change_add.add_widget(self.changer)
        self.change_add.add_widget(self.add_box)
        
        self.stat_basic.add_widget(self.basic_info)
        self.stat_basic.add_widget(self.graph_stat)
        
        
        self.add_widget(self.change_add)
        self.add_widget(self.stat_basic)
        #self.add_widget(self.basic_info)
        #self.add_widget(self.graph_stat)
        self.add_widget(self.all_rolls)
        
    def updater(self):
        self.stats.update()
        self.all_rolls.update()
        self.changer.update()
        self.basic_info.update()
    def request_info(self, request, *args):
        if request == 'range':
            return self._table.values_range()
        if request == 'mean_stddev':
            return self._table.mean(), self._table.stddev()
        if request == 'table_str':
            return str(self._table)
        if request == 'weights_info':
            return self._table.weights_info()
        if request == 'dice_list':
            return self._table.get_list()
        if request == 'stats':
            return gap.stats(self._table, *args)
        if request == 'all_rolls':
            return gap.print_table_string(self._table)
    def request_graph(self, new=False):
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
        gap.fancy_grapher_pct(self._table, figure=fig_num, style=the_style, legend=True)
        pylab.pause(0.1)
        figure_obj.canvas.manager.window.activateWindow()
        figure_obj.canvas.manager.window.raise_()
    def request_clear_graph(self):
        figure_obj = pylab.figure(0)
        pylab.cla()
        pylab.pause(0.1)
        figure_obj.canvas.manager.window.activateWindow()
        figure_obj.canvas.manager.window.raise_()
    def request_add(self, number, die):
        self._table.add_die(number, die)
        self.updater()
    def request_remove(self, number, die):
        current = self._table.number_of_dice(die)
        if number > current:
            self._table.remove_die(current, die)
        else:
            self._table.remove_die(number, die)
        self.updater()

    def request_reset(self):
        self._table = ds.DiceTable()








class DiceCarouselApp(App):
    def build(self):
        bob = DicePlatform()
        #Window.bind(on_resize=bob.update_wrapper)
        return bob
        
if __name__ == '__main__':
    DiceCarouselApp().run()

