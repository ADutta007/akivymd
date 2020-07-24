from kivy.lang.builder import Builder 
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.event import EventDispatcher
from kivy.animation import Animation

Builder.load_string(
    """
<AKDraggableScrollView>:

    MyFloatLayout:    
        id: _float 
        size_hint: None, None 
        width: root.width
        height: 0

    """
)

class MyFloatLayout(FloatLayout):

    _time_passed= 0    
    _item_found= None
    _first_item_found_move= True
    _animation_started= False
    _timer_event= None 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        self.touch_down_pos= touch.pos
        self._timer_event= Clock.schedule_interval(lambda x:self._timer(1/60, touch.pos), 1/60)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self._reset_timer()
        self.do_scroll= True 
        # Animation
        if self._item_found:
            anim= Animation(pos= [self.parent.x, self._item_y_1], duration= self.parent.aimation_duration, t= self.parent.transition )
            anim.start(self._item_found)

        self._item_found= None 
        self.parent.dispatch('on_complete')
        return super().on_touch_up(touch)

    def on_touch_move(self, touch):
        if self._item_found:
            self._move_widget(touch.pos)
        else:
            distance_passed= Vector(self.touch_down_pos).distance(touch.pos)
            if distance_passed>self.parent.scroll_distance:
                self._reset_timer()
        return super().on_touch_move(touch)

    def _timer(self,time, point):
        self._time_passed+= time 
        if self._time_passed> self.parent.select_duration:
            self._drag_trigger(point)
            self.do_scroll= False 
            self._reset_timer()
        
    def _reset_timer(self):
        if not self._timer_event:
            return 
        self._timer_event.cancel()
        self._time_passed=0
        self._first_item_found_move= True 

    def _drag_trigger(self, point):
        point= self.to_widget( point[0], point[1])
        for item in self.children:
            if item.collide_point(point[0], point[1]):
                self.remove_widget(item)
                self.add_widget(item)
                self._item_found= item
                self._item_y_1= item.pos[1]
                self.parent.dispatch('on_select', item)

    def _move_widget(self, pos):
        #========== Runs once
        if self._first_item_found_move:
            self._item_y_1= self._item_found.y
            self.y_diff= pos[1]- self._item_found.y
            self._first_item_found_move= False
        #========== Updates selected widget's position
        self._item_found.pos=[
            self.parent.x, pos[1]-self.y_diff
        ]
        #==========
        for item in self.children:
            if item.collide_point( pos[0], pos[1] ) and item!=self._item_found and not self._animation_started:
                y= item.pos[1]
                self.parent.dispatch('on_collision')
                # Animation
                anim= Animation(
                    pos=[self.parent.x , 
                    self._item_y_1] , 
                    duration= self.parent.aimation_duration, 
                    t= self.parent.transition
                    )
                anim.bind(on_complete=self._enable_move)
                anim.bind(on_start= self._disable_move)
                anim.start(item)
                self._item_y_1= y
                break

    def _enable_move(self, *args):
        self._animation_started= False 

    def _disable_move(self, *args):
        self._animation_started= True 

class AKDraggableScrollView(ScrollView, EventDispatcher):
    spacing= NumericProperty(0)
    select_duration= NumericProperty(0.5)
    aimation_duration= NumericProperty(0.1)
    transition= StringProperty('out_quad')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_select')
        self.register_event_type('on_collision')
        self.register_event_type('on_complete')

    def add_widget(self, widget, index=0):
        if issubclass(widget.__class__, MyFloatLayout):
            return super().add_widget(widget, index=index)
        else:
            return Clock.schedule_once(lambda x: self._add_in_order(widget)) 

    def _add_in_order(self, widget):
        widget.pos= [self.x, self.ids._float.height+ self.spacing]
        self._update_box_size(widget)
        self.ids._float.add_widget(widget)

    def _update_box_size(self, widget):
        box_height= 0
        for item in self.ids._float.children:
            box_height+= item.height+ self.spacing
        self.ids._float.height= box_height+ widget.height+ self.spacing

    def on_select(self, *args):
        pass 

    def on_collision(self, *args):
        pass 

    def on_complete(self, *args):
        pass 

