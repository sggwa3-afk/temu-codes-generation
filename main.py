import random
import string
import os
import json

from kivy.app import App
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from kivy.graphics import Color, RoundedRectangle, Ellipse


Window.clearcolor = (0.035, 0.045, 0.08, 1)


RED = (0.95, 0.08, 0.18, 1)
DARK = (0.08, 0.10, 0.16, 1)
WHITE = (1, 1, 1, 1)
GREEN = (0.20, 0.95, 0.70, 1)
GRAY = (0.60, 0.64, 0.73, 1)


class Card(BoxLayout):
    def __init__(self, color=DARK, radius=18, **kwargs):
        super().__init__(**kwargs)

        self.bg_color = color
        self.radius = dp(radius)

        with self.canvas.before:
            self.bg_instruction = Color(*self.bg_color)
            self.bg_shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg_shape.pos = self.pos
        self.bg_shape.size = self.size


class CircleButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            self.circle_color = Color(*RED)
            self.circle = Ellipse(
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size


class TemuCodesApp(App):

    def build(self):
        self.title = "TEMU CODES GENERATION"
        self.current_code = ""

        self.history_file = os.path.join(
            self.user_data_dir,
            "saved_codes.json"
        )

        self.codes = self.load_codes()

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(18), dp(20), dp(12)],
            spacing=dp(12)
        )

        # Header
        title = Label(
            text="[b][color=ff2945]TEMU[/color] CODES[/b]",
            markup=True,
            font_size=dp(27),
            size_hint_y=None,
            height=dp(48)
        )

        subtitle = Label(
            text="C O D E   G E N E R A T O R",
            color=GRAY,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(24)
        )

        root.add_widget(title)
        root.add_widget(subtitle)

        # Code length
        length_label = Label(
            text="CODE LENGTH",
            color=GRAY,
            halign="left",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(25)
        )
        length_label.bind(size=self.set_text_size)
        root.add_widget(length_label)

        self.length_input = TextInput(
            text="12",
            hint_text="Enter length",
            input_filter="int",
            multiline=False,
            halign="center",
            font_size=dp(18),
            foreground_color=WHITE,
            cursor_color=RED,
            background_normal="",
            background_active="",
            background_color=DARK,
            padding=[dp(12), dp(14)],
            size_hint_y=None,
            height=dp(50)
        )

        root.add_widget(self.length_input)

        # Generated code card
        code_card = Card(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(105)
        )

        code_card.add_widget(Label(
            text="YOUR GENERATED CODE",
            color=GRAY,
            font_size=dp(11),
            size_hint_y=0.4
        ))

        self.result = Label(
            text="••••••••••••",
            color=GREEN,
            font_size=dp(21),
            bold=True,
            size_hint_y=0.6
        )

        code_card.add_widget(self.result)
        root.add_widget(code_card)

        # Circular generate button
        button_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            spacing=dp(2)
        )

        self.generate_button = CircleButton(
            text="GENERATE",
            color=WHITE,
            font_size=dp(13),
            bold=True,
            size_hint=(None, None),
            size=(dp(112), dp(112)),
            pos_hint={"center_x": 0.5}
        )

        self.generate_button.bind(
            on_press=self.generate_code
        )

        button_box.add_widget(self.generate_button)
        root.add_widget(button_box)

        # Copy button
        copy_button = Button(
            text="COPY CODE",
            color=WHITE,
            bold=True,
            font_size=dp(14),
            background_normal="",
            background_color=RED,
            size_hint_y=None,
            height=dp(46)
        )

        copy_button.bind(on_press=self.copy_code)
        root.add_widget(copy_button)

        # Status
        self.status = Label(
            text="Ready to generate",
            color=GRAY,
            font_size=dp(12),
            size_hint_y=None,
            height=dp(25)
        )

        root.add_widget(self.status)

        # History header
        history_header = BoxLayout(
            size_hint_y=None,
            height=dp(35)
        )

        history_header.add_widget(Label(
            text="[b]SAVED CODES[/b]",
            markup=True,
            color=WHITE,
            font_size=dp(14),
            halign="left"
        ))

        clear_button = Button(
            text="CLEAR",
            color=RED,
            font_size=dp(11),
            size_hint_x=None,
            width=dp(75),
            background_normal="",
            background_color=DARK
        )

        clear_button.bind(on_press=self.clear_codes)
        history_header.add_widget(clear_button)

        root.add_widget(history_header)

        # Scrollable history
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3)
        )

        self.history_box = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            padding=[0, dp(3), 0, dp(8)]
        )

        self.history_box.bind(
            minimum_height=self.history_box.setter("height")
        )

        scroll.add_widget(self.history_box)
        root.add_widget(scroll)

        self.refresh_history()

        return root

    def set_text_size(self, widget, size):
        widget.text_size = size

    def load_codes(self):
        try:
            with open(self.history_file, "r") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def save_codes(self):
        os.makedirs(self.user_data_dir, exist_ok=True)

        with open(self.history_file, "w") as file:
            json.dump(self.codes, file)

    def generate_code(self, instance):
        try:
            length = int(self.length_input.text)

            if not 1 <= length <= 128:
                self.status.text = "Choose a length from 1 to 128"
                self.status.color = RED
                return

            characters = string.ascii_uppercase + string.digits

            self.current_code = "".join(
                random.choices(characters, k=length)
            )

            self.result.text = self.current_code
            self.result.color = GREEN

            self.codes.insert(0, self.current_code)
            self.codes = self.codes[:100]

            self.save_codes()
            self.refresh_history()

            self.status.text = "New code generated!"
            self.status.color = GREEN

        except ValueError:
            self.status.text = "Enter a valid code length"
            self.status.color = RED

    def copy_code(self, instance):
        if not self.current_code:
            self.status.text = "Generate a code first!"
            self.status.color = RED
            return

        Clipboard.copy(self.current_code)

        self.status.text = "Code copied to clipboard!"
        self.status.color = GREEN

    def refresh_history(self):
        self.history_box.clear_widgets()

        if not self.codes:
            self.history_box.add_widget(Label(
                text="No saved codes yet",
                color=GRAY,
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for code in self.codes:
            row = Card(
                orientation="horizontal",
                padding=[dp(10), dp(5)],
                spacing=dp(5),
                size_hint_y=None,
                height=dp(43)
            )

            code_label = Label(
                text=code,
                color=GREEN,
                font_size=dp(13),
                halign="left"
            )

            copy_button = Button(
                text="COPY",
                color=WHITE,
                font_size=dp(10),
                size_hint_x=None,
                width=dp(65),
                background_normal="",
                background_color=RED
            )

            copy_button.bind(
                on_press=lambda btn, c=code: self.copy_saved(c)
            )

            row.add_widget(code_label)
            row.add_widget(copy_button)

            self.history_box.add_widget(row)

    def copy_saved(self, code):
        Clipboard.copy(code)
        self.status.text = "Saved code copied!"
        self.status.color = GREEN

    def clear_codes(self, instance):
        self.codes = []
        self.save_codes()
        self.refresh_history()

        self.status.text = "Saved history cleared"
        self.status.color = GRAY


if __name__ == "__main__":
    TemuCodesApp().run()
