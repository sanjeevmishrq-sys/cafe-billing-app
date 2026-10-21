from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
import datetime

Window.clearcolor = (0.05, 0.1, 0.25, 1)

MENU = {
    "Beverages": {
        "Cappuccino": 150,
        "Cafe Latte": 160,
        "Cold Coffee": 140,
        "Hot Chocolate": 180,
        "Masala Chai": 60
    },
    "Snacks & Fast Food": {
        "Veg Cheese Burger": 120,
        "French Fries": 100,
        "Cheese Garlic Bread": 130
    },
    "Main Course & Italian": {
        "White Sauce Pasta": 220,
        "Veg Pizza (Regular)": 250
    },
    "Desserts": {
        "Chocolate Brownie": 110,
        "Red Velvet Pastry": 130
    }
}

GLOBAL_ORDERS = []

class CustomerMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # सुरक्षित तरीके سے बैकग्राउंड इमेज सेटअप
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source='cafe_bg.jpg', size=Window.size, pos=(0, 0))
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        self.cart = {}
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        title_label = Label(
            text="CAFE & PIZZA - DELIVERY", 
            font_size=18, 
            bold=True,
            color=(1, 0.85, 0.3, 1)
        )
        owner_nav_btn = Button(
            text="Owner Panel", 
            size_hint_x=None, 
            width=110,
            background_color=(0.9, 0.5, 0.1, 1),
            font_size=13
        )
        owner_nav_btn.bind(on_press=self.goto_owner_panel)
        
        top_bar.add_widget(title_label)
        top_bar.add_widget(owner_nav_btn)
        main_layout.add_widget(top_bar)
        
        scroll = ScrollView(size_hint=(1, 0.55))
        self.grid_menu = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid_menu.bind(minimum_height=self.grid_menu.setter('height'))
        
        for category, items in MENU.items():
            cat_label = Label(
                text=f"--- {category} ---", 
                font_size=16, 
                bold=True,
                size_hint_y=None, 
                height=35,
                color=(0.4, 0.9, 1, 1)
            )
            self.grid_menu.add_widget(cat_label)
            
            for item_name, price in items.items():
                btn_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=8)
                
                lbl = Label(text=f"  {item_name} (₹{price})", font_size=15, halign='left', valign='middle', color=(1, 1, 1, 1))
                lbl.bind(size=lbl.setter('text_size'))
                
                minus_btn = Button(text="-", background_color=(0.8, 0.3, 0.3, 1), size_hint_x=None, width=45)
                minus_btn.bind(on_press=lambda x, name=item_name: self.remove_from_cart(name))
                
                add_btn = Button(text="+", background_color=(0.15, 0.65, 0.35, 1), size_hint_x=None, width=45)
                add_btn.bind(on_press=lambda x, name=item_name: self.add_to_cart(name))
                
                btn_box.add_widget(lbl)
                btn_box.add_widget(minus_btn)
                btn_box.add_widget(add_btn)
                self.grid_menu.add_widget(btn_box)
                
        scroll.add_widget(self.grid_menu)
        main_layout.add_widget(scroll)
        
        self.address_input = TextInput(
            hint_text='Enter delivery address & phone...', 
            size_hint_y=None, 
            height=45,
            multiline=False,
            font_size=14
        )
        main_layout.add_widget(self.address_input)
        
        self.total_label = Label(
            text="Items: 0 | Total: ₹0", 
            font_size=16, 
            bold=True, 
            size_hint_y=None, 
            height=35,
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(self.total_label)
        
        order_btn = Button(
            text="Place Online Order", 
            font_size=17, 
            background_color=(0.2, 0.5, 0.9, 1),
            size_hint_y=None, 
            height=50
        )
        order_btn.bind(on_press=self.place_order)
        main_layout.add_widget(order_btn)
        
        self.add_widget(main_layout)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def get_item_price(self, item_name):
        for cat, items in MENU.items():
            if item_name in items:
                return items[item_name]
        return 0

    def add_to_cart(self, item_name):
        self.cart[item_name] = self.cart.get(item_name, 0) + 1
        self.update_total_display()

    def remove_from_cart(self, item_name):
        if item_name in self.cart and self.cart[item_name] > 0:
            self.cart[item_name] -= 1
            if self.cart[item_name] == 0:
                del self.cart[item_name]
        self.update_total_display()

    def update_total_display(self):
        total_price = sum(self.get_item_price(item) * qty for item, qty in self.cart.items())
        total_items = sum(self.cart.values())
        self.total_label.text = f"Items: {total_items} | Total: ₹{total_price}"

    def place_order(self, instance):
        if not self.cart:
            self.total_label.text = "Cart is Empty!"
            return
        
        address = self.address_input.text.strip()
        if not address:
            self.total_label.text = "Enter address!"
            return
        
        grand_total = sum(self.get_item_price(item) * qty for item, qty in self.cart.items())
        time_str = datetime.datetime.now().strftime('%H:%M:%S')
        
        new_order = {
            "time": time_str,
            "address": address,
            "items": dict(self.cart),
            "total": grand_total,
            "status": "Order Accepted 🟢"
        }
        GLOBAL_ORDERS.insert(0, new_order)
        
        app = App.get_running_app()
        app.status_screen.update_order_details(new_order)
        app.screen_manager.current = 'status'

    def goto_owner_panel(self, instance):
        app = App.get_running_app()
        app.owner_screen.refresh_orders()
        app.screen_manager.current = 'owner'


class OrderStatusScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source='cafe_bg.jpg', size=Window.size, pos=(0, 0))
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        self.add_widget(self.layout)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def update_order_details(self, order):
        self.layout.clear_widgets()
        
        title = Label(
            text="ORDER CONFIRMED!", 
            font_size=22, 
            bold=True,
            size_hint_y=None, 
            height=45,
            color=(0.2, 1, 0.4, 1)
        )
        self.layout.add_widget(title)
        
        info_lbl = Label(
            text=f"Time: {order['time']}\nAddress: {order['address']}", 
            font_size=14, 
            size_hint_y=None, 
            height=50,
            halign='center',
            color=(0.8, 1, 1, 1)
        )
        info_lbl.bind(size=info_lbl.setter('text_size'))
        self.layout.add_widget(info_lbl)
        
        scroll = ScrollView(size_hint=(1, 0.45))
        grid = GridLayout(cols=1, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for item, qty in order['items'].items():
            price = self.get_price(item)
            total = price * qty
            lbl = Label(
                text=f"  {item} x {qty} = ₹{total}", 
                font_size=15, 
                size_hint_y=None, 
                height=35,
                halign='left',
                valign='middle',
                color=(1, 1, 1, 1)
            )
            lbl.bind(size=lbl.setter('text_size'))
            grid.add_widget(lbl)
            
        scroll.add_widget(grid)
        self.layout.add_widget(scroll)
        
        total_lbl = Label(
            text=f"GRAND TOTAL: ₹{order['total']}", 
            font_size=18, 
            bold=True,
            size_hint_y=None, 
            height=40,
            color=(1, 0.75, 0.2, 1)
        )
        self.layout.add_widget(total_lbl)
        
        status_box = Label(
            text=f"Status: {order['status']}", 
            font_size=14, 
            size_hint_y=None, 
            height=45,
            halign='center',
            color=(0.4, 0.85, 1, 1)
        )
        status_box.bind(size=status_box.setter('text_size'))
        self.layout.add_widget(status_box)
        
        back_btn = Button(
            text="Back to Menu", 
            font_size=16, 
            background_color=(0.8, 0.25, 0.2, 1),
            size_hint_y=None, 
            height=50
        )
        back_btn.bind(on_press=self.back_to_menu)
        self.layout.add_widget(back_btn)

    def get_price(self, item):
        for cat, items in MENU.items():
            if item in items:
                return items[item]
        return 0

    def back_to_menu(self, instance):
        app = App.get_running_app()
        app.menu_screen.cart = {}
        app.menu_screen.address_input.text = ""
        app.menu_screen.total_label.text = "Items: 0 | Total: ₹0"
        app.screen_manager.current = 'menu'


class CafeOwnerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source='cafe_bg.jpg', size=Window.size, pos=(0, 0))
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=45)
        title = Label(
            text="CAFE OWNER - LIVE ORDERS", 
            font_size=18, 
            bold=True,
            color=(1, 0.6, 0.2, 1)
        )
        back_btn = Button(
            text="Back to Menu", 
            size_hint_x=None, 
            width=120,
            background_color=(0.2, 0.5, 0.9, 1),
            font_size=13
        )
        back_btn.bind(on_press=self.goto_menu)
        
        top_bar.add_widget(title)
        top_bar.add_widget(back_btn)
        layout.add_widget(top_bar)
        
        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.orders_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.orders_grid.bind(minimum_height=self.orders_grid.setter('height'))
        
        self.scroll.add_widget(self.orders_grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def refresh_orders(self):
        self.orders_grid.clear_widgets()
        
        if not GLOBAL_ORDERS:
            no_order_lbl = Label(
                text="No active orders yet!", 
                font_size=16, 
                size_hint_y=None, 
                height=50,
                color=(1, 1, 1, 1)
            )
            self.orders_grid.add_widget(no_order_lbl)
            return
            
        for order in GLOBAL_ORDERS:
            items_str = ", ".join([f"{k} x{v}" for k, v in order['items'].items()])
            order_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=10, spacing=5)
            
            lbl_info = Label(
                text=f"Time: {order['time']} | Total: ₹{order['total']}\nAddr: {order['address']}",
                font_size=13,
                size_hint_y=None,
                height=35,
                color=(0.9, 1, 1, 1)
            )
            lbl_info.bind(size=lbl_info.setter('text_size'))
            
            lbl_items = Label(
                text=f"Items: {items_str}",
                font_size=13,
                size_hint_y=None,
                height=30,
                color=(1, 0.85, 0.3, 1)
            )
            lbl_items.bind(size=lbl_items.setter('text_size'))
            
            status_btn = Button(
                text=f"Status: {order['status']} (Click to toggle)",
                size_hint_y=None,
                height=35,
                background_color=(0.2, 0.6, 0.3, 1),
                font_size=13
            )
            status_btn.bind(on_press=lambda x, o=order: self.toggle_status(o))
            
            order_box.add_widget(lbl_info)
            order_box.add_widget(lbl_items)
            order_box.add_widget(status_btn)
            
            self.orders_grid.add_widget(order_box)

    def toggle_status(self, order):
        if "Accepted" in order['status']:
            order['status'] = "Out for Delivery 🛵"
        elif "Delivery" in order['status']:
            order['status'] = "Delivered ✅"
        else:
            order['status'] = "Order Accepted 🟢"
        self.refresh_orders()

    def goto_menu(self, instance):
        App.get_running_app().screen_manager.current = 'menu'


class CafeDeliveryApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        
        self.menu_screen = CustomerMenuScreen(name='menu')
        self.status_screen = OrderStatusScreen(name='status')
        self.owner_screen = CafeOwnerScreen(name='owner')
        
        self.screen_manager.add_widget(self.menu_screen)
        self.screen_manager.add_widget(self.status_screen)
        self.screen_manager.add_widget(self.owner_screen)
        
        return self.screen_manager

if __name__ == '__main__':
    CafeDeliveryApp().run()
    
