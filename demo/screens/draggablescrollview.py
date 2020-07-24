from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import OneLineListItem

Builder.load_string(
    """
<Item@OneLineListItem>:
    canvas.before:
        Color:
            rgba: app.theme_cls.bg_normal
        Rectangle:
            pos: self.pos 
            size: self.size 

<DraggableScrollView>:
    name: 'DraggableScrollView'
    BoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: root.name
            left_action_items:[['arrow-left' , lambda x:app.show_screen('Home','back') ]]

        AKDraggableScrollView:
            id: draggable
            on_select: print('selected')
            on_collision: print('collide')
            on_complete: print('complete')
    """
)

class Item(OneLineListItem):
    pass 

class DraggableScrollView(Screen):

    def on_enter(self):
        for x in range(20):
            self.ids.draggable.add_widget(Item(
                text= 'item %d'%x
            ))

    def on_leave(self, *args):
        self.ids.draggable.clear_widgets()
