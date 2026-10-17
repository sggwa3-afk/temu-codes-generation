from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
import random
import string

Window.clearcolor = (0.07, 0.07, 0.09, 1)


class TemuCodesApp(App):

    def build(self):
        self.title = "TEMU CODES GENERATION"

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        title = Label(
            text="TEMU CODES GENERATION",
            font_size="24sp",
            bold=True
        )

        self.code_label = Label(
            text="اضغط لتوليد كود",
            font_size="22sp"
        )

        generate_button = Button(
            text="GENERATE CODE",
            size_hint=(1, 0.2),
            background_color=(1, 0.15, 0.15, 1)
        )

        generate_button.bind(
            on_press=self.generate_code
        )

        layout.add_widget(title)
        layout.add_widget(self.code_label)
        layout.add_widget(generate_button)

        return layout

    def generate_code(self, instance):
        characters = string.ascii_uppercase + string.digits

        code = "".join(
            random.choices(characters, k=12)
        )

        self.code_label.text = code


if __name__ == "__main__":
    TemuCodesApp().run()
