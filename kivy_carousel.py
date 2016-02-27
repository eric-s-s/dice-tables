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
FLASH_DELAY = 0.5
# kv file line 4
class HorSlider(BoxLayout):
    '''a slider of set size that displays it's number and stores a holder for
    future reference (used here to get roll numbers on die weights)'''
    def __init__(self, **kwargs):
        super(HorSlider, self).__init__(**kwargs)
        self.holder=None
    def write_label(self, text):
        '''text= str'''
        self.ids['hor_title'].text = text
    def write_holder(self, new_val):
        '''holder = int'''
        self.holder = new_val
    def get_holder(self):
        '''returns int'''
        out = self.holder
        return out
    def get_value(self):
        '''returns value of slider'''
        return int(self.ids['hor_slider'].value)        
# kv file line NONE
class FlashButton(Button):
    '''a button that flashes for FLASH_DELAY time after pressed, so you know you
    done taht press real clear-like'''
    def __init__(self, **kwargs):
        super(FlashButton, self).__init__(**kwargs)
        self.bind(on_press=self.long_press)
    def long_press(self, *args):
        '''sets background to flash on press'''
        self.color = [1,0,0,1]
        self.background_color = [0.2,0.2,1,1]
        Clock.schedule_once(self.callback, FLASH_DELAY)
    def callback(self, dt):
        '''sets background to normal'''
        self.color=[1,1,1,1]
        self.background_color = [1,1,1,1]
# kv file line NONE
class FlashLabel(Button):
    '''a label that flashes for FLASH_DELAY when text is added by add_text.
    can be turned off with boolean do_flash'''
    def __init__(self, **kwargs):
        super(FlashLabel, self).__init__(**kwargs)
        self.background_normal=''
    def add_text(self, text, do_flash=True):
        '''flahes (or not) when text is changed'''
        self.text = text
        self.color=[1,1,1,1]
        self.background_color = [0,0,0,0]
        if do_flash:
            self.color = [1,0,0,1]
            self.background_color = [0.2,0.2,1,0.2]
            Clock.schedule_once(self.callback, FLASH_DELAY)
    def callback(self, dt):
        '''reset background and color after delay'''
        self.color=[1,1,1,1]
        self.background_color = [0,0,0,0]
# kv file line NONE
class PlusMinusButton(FlashButton):
    '''init - numer=int.  self.number is stored and text is +/- the number'''
    def __init__(self, number, **kwargs):
        super(PlusMinusButton, self).__init__(**kwargs)
        self.number = number
        self.text = '{:+}'.format(self.number)
# kv file line 25
class SizeButton(FlashButton):
    '''a button for sizing a die.  label is "D(diesize)" defaults to 1'''
    die_size = NumericProperty(1)
# kv file line 28        
class PageBox(BoxLayout):
    '''a box that splits a long text into pages. displays labels of requested page.
    default size ratio is TITLE = 0.15, buttons = 0.05, text=0.8.'''
    def __init__(self, **kwargs):
        super(PageBox, self).__init__(**kwargs)
        self.pages = ['']
        self.current_page = 0
        self.font_size = 15
    def reset_sizes(self, f_size, ratios):
        '''reset font_size = f_size, 
        [title ratio, button ratio, text ratio] = ratios'''
        self.ids['jump_to'].font_size= f_size
        self.ids['page_box_title'].size_hint_y = ratios[0]
        self.ids['buttons_container'].size_hint_y = ratios[1]
        self.ids['text_container'].size_hint_y = ratios[2]  
    def set_title(self, title):
        '''title is a string'''
        self.ids['page_box_title'].text = title
    def show_page(self, number):
        '''display page number (number % total pages)'''
        number = number % len(self.pages)
        self.current_page = number
        self.ids['text_container'].text = self.pages[number]
        self.ids['text_container'].font_size =  self.font_size
        self.ids['text_container'].text_size = self.ids['text_container'].size
        self.ids['jump_to'].text = str(number + 1)
    def set_text(self, new_text, new_font_size, fudge_factor=0.65):
        '''this sets the page box with a new text which it splits into pages
        according to lines_per_page = fudge_factor * box_height/font_size.
        fudge_factor=0.65 work here, but it's set-able just in case.''' 
        self.font_size = new_font_size
        page_height = self.height
        lines_per_page = int(fudge_factor * page_height/ float(new_font_size))
        def page_maker(text, line_limit):
            '''helper function.  splits a str into lst of strings according to
            line_limit.  adds enout \n to final string so all strings have same
            # of lines.'''
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
        self.pages = page_maker(new_text, lines_per_page)
        self.ids['page_total'].text = '/%s' % (len(self.pages))
        self.show_page(self.current_page)
# kv file line 101
class AddRmDice(BoxLayout):
    '''a box taht can call parent_widget's add(num, die) and remove(num, die) funtion
    when pressed.  
    number=int - how many dice on the label. 0 means just str(die) displayed.
    die=child of dicestats.ProtoDie - the die on the label and what will be called.
    only_add=boolean - false let's you + or - the current die.
    do_flash=boolean - flash the label upon creation.'''
    def __init__(self, parent_widget, number, die, only_add=False, do_flash=True, **kwargs):
        super(AddRmDice, self).__init__(**kwargs)
        self._number = number
        self._die = die
        self.parent_widget = parent_widget
        self.only_add = only_add
        self.do_flash = do_flash
        self.small = 20
        self.medium = 100
        self.update()
    def assign_die(self, number, die):
        '''can re-assign number and die after creation.'''
        self._die = die
        self._number = number
        self.update()
    def addrm(self, btn):
        '''what is called by the on_press method for packed buttons'''
        times = btn.number
        if times < 0:
            self.parent_widget.remove(abs(times), self._die)
        else:
            self.parent_widget.add(times, self._die)
    def update(self):
        '''called at creation and assign_die. packs the box appropriately'''
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
        flash = FlashLabel()
        flash.size_hint=(sz_hnt_x*2, 1)
        self.add_widget(flash)
        flash.add_text(die_string, do_flash=self.do_flash)
        for number in range(buttons):
            btn = PlusMinusButton(10**number, size_hint=(sz_hnt_x, 1))
            btn.bind(on_press=self.addrm)
            self.add_widget(btn)

#big_boxes
# kv file line 107
class ChangeBox(GridLayout):
    '''displays current dice and allows to change. parent app is what's called 
    for dice actions and info updates. all calls are 
    self.parent_app.request_something(*args).'''
    def __init__(self, parent_app, **kwargs):
        super(ChangeBox, self).__init__(**kwargs)
        self.parent_app = parent_app
        self.cols = 1
        self.old_dice_list = []
    def update(self):
        '''updates the current dice after add, rm or clear'''
        dice_list = self.parent_app.request_info('dice_list')
        self.clear_widgets()
        self.add_widget(Button(on_press=self.parent_app.request_reset, text='reset table',
                               font_size=20, size_hint=(1, None), height=60))
        new_height = 70
        if dice_list:
            new_height = min((self.height - 60) / len(dice_list), new_height) 
        for die, number in dice_list:
            if (die, number) in self.old_dice_list:
                changed = False
            else:
                changed = True
            add_rm = AddRmDice(self, number, die, do_flash=changed, size_hint=(0.8,None), height=new_height)
            self.add_widget(add_rm)
        self.old_dice_list = dice_list    
    def add(self, number, die, *args):
        '''delay after call because otherwise button press won't be shown before
        button gets erased and rewritten'''
        Clock.schedule_once(lambda dt: self.delayed_add(number, die, *args), FLASH_DELAY)
    def delayed_add(self, number, die, *args):
        '''see add'''
        self.parent_app.request_add(number, die)
    def remove(self, number, die, *args):
        '''delay. same as add'''
        Clock.schedule_once(lambda dt: self.delayed_remove(number, die, *args), FLASH_DELAY)
    def delayed_remove(self, number, die, *args):
        '''see remove'''
        self.parent_app.request_remove(number, die)    
# kv file line 110    
class AddBox(BoxLayout):
    #TODO - put weights and i believe i'll find what i need in branch gui_kivy
    '''box for adding new dice.  parent app is what's called for dice actions and
    info updates. all calls are self.parent_app.request_something(*args).'''
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
        '''how the box is packed'''
        self.ids['add_it'].add_widget(self.add_it)
        for number in [2, 4, 6, 8, 10, 12, 20, 100]:
            btn = SizeButton(die_size=number)
            btn.bind(on_press=self.assign_size_btn)
            self.ids['presets'].add_widget(btn) 
    def assign_size_btn(self, btn):
        '''assigns the die size and die when a preset btn is pushed'''
        self.die_size = btn.die_size
        self.assign_die()
    
    def assign_mod(self):
        '''assigns a die modifier and new die when slider is moved'''
        self.mod = int(self.ids['modifier'].value)
        self.assign_die()
    def assign_die(self):
        '''all changes to size, mod and weight call this function'''
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
        '''delay after call because otherwise button press won't be shown before
        button gets erased and rewritten'''
        Clock.schedule_once(lambda dt: self.delayed_add(number, die, *args), FLASH_DELAY)
    def delayed_add(self, number, die, *args):
        '''see add'''
        self.parent_app.request_add(number, die)
    def remove(self, number, die, *args):
        '''delay. same as add'''
        Clock.schedule_once(lambda dt: self.delayed_remove(number, die, *args), FLASH_DELAY)
    def delayed_remove(self, number, die, *args):
        '''see remove'''
        self.parent_app.request_remove(number, die)        
# kv file line 164
class InfoBox(BoxLayout):
    '''displays basic info about the die. parent app is what's called for dice 
    actions and info updates. all calls are 
    self.parent_app.request_something(*args).'''
    def __init__(self, parent_app, **kwargs):
        super(InfoBox, self).__init__(**kwargs)
        self.parent_app = parent_app
        self.ids['weight_info'].reset_sizes(15, [0.1, 0.1, 0.8])
        self.ids['weight_info'].set_title('full weight info')
    def update(self):
        '''updates all the info in box.'''
        values_min, values_max = self.parent_app.request_info('range')
        mean = self.parent_app.request_info('mean')
        stddev = self.parent_app.request_info('stddev')        
        stat_text = ('the range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
               % (values_min, values_max, round(mean, 4), stddev))
        self.ids['stat_str'].text = stat_text
        
        self.ids['dice_table_str'].text = '\n' + self.parent_app.request_info('table_str')
        self.ids['weight_info'].set_text(self.parent_app.request_info('weights_info'), 15) 
# kv file line 186
class GraphBox(BoxLayout):
#TODO: complete rewrite using kivy garden graph
    '''buttons for making graphs.  parent app is what's called for dice actions
    and info updates. all calls are self.parent_app.request_something(*args).'''
    def __init__(self, parent_app, **kwargs):
        super(GraphBox, self).__init__(**kwargs)
        self.parent_app = parent_app

# kv file line 209
class StatBox(BoxLayout):
    '''box for getting and displaying stats about rolls. parent app is what's
    called for dice actions and info updates. all calls are 
    self.parent_app.request_something(*args).'''
    def __init__(self, parent_app, **kwargs):
        super(StatBox, self).__init__(**kwargs)
        self.parent_app = parent_app
        self.text_lines = 1
        #self.ids['stat_text'].font_size = (lambda:self.ids['stat_text'].height//15)()
        #self.ids['stat_text'].height = 1
        #self.bind(on_texture_size = self.font_sizer)
    def update(self):
        '''called when dice list changes.'''
        val_min, val_max = self.parent_app.request_info('range')
        self.ids['stop_slider'].min = val_min
        self.ids['start_slider'].min = val_min
        self.ids['stop_slider'].max = val_max
        self.ids['start_slider'].max = val_max        

    def assign_text_value(self, box='start'):
        '''called by text_input to assign that value to sliders and show stats'''
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
        '''the main function. displays stats of current slider values.'''
        val_1 = int(self.ids['stop_slider'].value)
        val_2 = int(self.ids['start_slider'].value)

        stat_list = range(min(val_1, val_2), max(val_1, val_2) + 1)
        new_text = '\n' + self.parent_app.request_stats(stat_list).replace(' possible', '')
        text_lines = new_text.count('\n') + 1
        new_font_size = min(0.7 * self.ids['stat_text'].height//text_lines, 
                            int(0.08*self.ids['stat_text'].width))

        self.ids['stat_text'].font_size = min(new_font_size, 15)
        self.ids['stat_text'].text = new_text        
# kv file line 304
class AllRollsBox(PageBox):
    '''a pagebox that display the frequency for each roll in the table. parent 
    app is what's called for dice actions and info updates. all calls are 
    self.parent_app.request_something(*args).'''
    def __init__(self, parent_app, **kwargs):
        PageBox.__init__(self)
        self.parent_app = parent_app
        self.set_title('here are all the rolls and their frequency')
    def update(self):
        '''rewrites after dice change'''
        text = self.parent_app.request_info('all_rolls')
        self.set_text(text, 15)   

        
class DicePlatform(Carousel):
    '''the main box.  the parent_app.'''
    def __init__(self, **kwargs):
        super(DicePlatform, self).__init__(**kwargs)
        self._table = ds.DiceTable()
        
        self.bind_children()
        self.pack_children()
        
        self.direction='right'
        self.loop='true'
        self.scroll_timeout = 120

    
    def bind_children(self):
        '''creates all children'''
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
        '''  change_box add_box | basic_info graphs |all_rolls
                                             stats             '''
        self.graph_stat.add_widget(self.graphs)
        self.graph_stat.add_widget(self.stats)
        
        self.change_add.add_widget(self.changer)
        self.change_add.add_widget(self.add_box)
        
        self.stat_basic.add_widget(self.basic_info)
        self.stat_basic.add_widget(self.graph_stat)
        
        
        self.add_widget(self.change_add)
        self.add_widget(self.stat_basic)
        self.add_widget(self.all_rolls)
        
    def updater(self):
        '''updates appropriate things for any die add or remove'''
        self.stats.update()
        self.all_rolls.update()
        self.changer.update()
        self.basic_info.update()
    def request_info(self, request):
        '''returns requested info to child widget'''
        requests = {'range': [self._table.values_range, ()],
                    'mean': [self._table.mean, ()],
                    'stddev': [self._table.stddev, ()],
                    'table_str': [str, (self._table,)],
                    'weights_info': [self._table.weights_info, ()],
                    'dice_list': [self._table.get_list, ()],
                    'all_rolls': [gap.print_table_string, (self._table,)]}
        command, args = requests[request]
        return command(*args)
    def request_stats(self, stat_list):
        return gap.stats(self._table, stat_list)
    def request_graph(self, new=False):
        '''creates a pylab graph'''
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
        '''clears the pylab overlay graph'''
        figure_obj = pylab.figure(0)
        pylab.cla()
        pylab.pause(0.1)
        figure_obj.canvas.manager.window.activateWindow()
        figure_obj.canvas.manager.window.raise_()
    def request_add(self, number, die):
        '''adds dice to table'''
        self._table.add_die(number, die)
        self.updater()
    def request_remove(self, number, die):
        '''safely removes dice from table. if too many removed, removes all of 
        that kind of dice'''
        current = self._table.number_of_dice(die)
        if number > current:
            self._table.remove_die(current, die)
        else:
            self._table.remove_die(number, die)
        self.updater()

    def request_reset(self, *args):
        '''reset dice table'''
        self._table = ds.DiceTable()
        self.updater()







class DiceCarouselApp(App):
    '''the app.  it's the dice platform'''
    def build(self):
        bob = DicePlatform()
        #Window.bind(on_resize=bob.update_wrapper)
        return bob
        
if __name__ == '__main__':
    DiceCarouselApp().run()

