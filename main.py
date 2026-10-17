# Ahmed's art shop — Touch Drawing Studio
# Built with Python + Kivy. Designed for Android and desktop.
from kivy.config import Config
Config.set("graphics", "minimum_width", "360")
Config.set("graphics", "minimum_height", "640")

import os
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage

APP_BG = "#11131A"
PANEL_BG = "#1C202B"
ACCENT = "#8B5CF6"
TEXT = "#F4F5FA"
MUTED = "#AAB0C0"

PALETTE = [
    ("#FFFFFF", "White"), ("#111111", "Black"), ("#F43F5E", "Red"),
    ("#F97316", "Orange"), ("#FACC15", "Yellow"), ("#22C55E", "Green"),
    ("#06B6D4", "Cyan"), ("#3B82F6", "Blue"), ("#8B5CF6", "Purple"),
    ("#EC4899", "Pink"), ("#A16207", "Brown"), ("#9CA3AF", "Gray"),
]

def rgba(hex_color):
    return get_color_from_hex(hex_color)

class DrawingCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brush_color = "#111111"
        self.brush_size = dp(5)
        self.eraser = False
        self._active_line = None
        self._undo_stack = []
        self._redo_stack = []
        self._background = "#FFFFFF"
        with self.canvas.before:
            self._bg_color = Color(*rgba(self._background))
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _sync_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._redo_stack.clear()
        self._undo_stack.append(self.export_png_bytes())
        if len(self._undo_stack) > 30:
            self._undo_stack.pop(0)
        color = self._background if self.eraser else self.brush_color
        with self.canvas:
            Color(*rgba(color))
            self._active_line = Line(points=[touch.x, touch.y], width=self.brush_size, cap="round", joint="round")
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._active_line:
            self._active_line.points += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._active_line = None
            return True
        return super().on_touch_up(touch)

    def export_png_bytes(self):
        # Undo snapshots are kept as canvas instructions instead of screenshots.
        # This method is intentionally a no-op placeholder for compatibility.
        return None

    def undo(self):
        # Kivy canvas instructions are not individually reversible without a
        # retained instruction list, so we use the stored stroke records below.
        if not self.strokes:
            return
        self.redo_strokes.append(self.strokes.pop())
        self._redraw()

    def redo(self):
        if not self.redo_strokes:
            return
        self.strokes.append(self.redo_strokes.pop())
        self._redraw()

    def initialize_history(self):
        self.strokes = []
        self.redo_strokes = []
        self._current_record = None

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self.redo_strokes.clear()
        color = self._background if self.eraser else self.brush_color
        self._current_record = {"points": [touch.x, touch.y], "color": color, "width": self.brush_size}
        self.strokes.append(self._current_record)
        with self.canvas:
            Color(*rgba(color))
            self._active_line = Line(points=[touch.x, touch.y], width=self.brush_size, cap="round", joint="round")
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._active_line:
            self._active_line.points += [touch.x, touch.y]
            self._current_record["points"] += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._active_line = None
            self._current_record = None
            return True
        return super().on_touch_up(touch)

    def _redraw(self):
        self.canvas.clear()
        with self.canvas.before:
            pass
        with self.canvas:
            for stroke in self.strokes:
                Color(*rgba(stroke["color"]))
                Line(points=stroke["points"], width=stroke["width"], cap="round", joint="round")
        self._sync_bg()

    def clear(self):
        self.strokes.clear()
        self.redo_strokes.clear()
        self.canvas.clear()
        self._sync_bg()

    def set_background(self, hex_color):
        self._background = hex_color
        self._bg_color.rgba = rgba(hex_color)
        self._redraw()

    def save(self, filepath):
        self.export_to_png(filepath)

class ArtShopApp(App):
    title = "Ahmed's art shop"

    def build(self):
        Window.clearcolor = rgba(APP_BG)
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.root_box.add_widget(self._header())
        self.canvas_area = DrawingCanvas()
        self.canvas_area.initialize_history()
        self.canvas_area.size_hint_y = 1
        self.canvas_area.background_color = "#FFFFFF"

        # White paper with subtle frame.
        paper_wrap = BoxLayout(padding=dp(2))
        with paper_wrap.canvas.before:
            Color(*rgba("#343949"))
            self.paper_border = Rectangle(pos=paper_wrap.pos, size=paper_wrap.size)
        def sync_paper(*_):
            self.paper_border.pos = paper_wrap.pos
            self.paper_border.size = paper_wrap.size
        paper_wrap.bind(pos=sync_paper, size=sync_paper)
        paper_wrap.add_widget(self.canvas_area)
        self.root_box.add_widget(paper_wrap)

        self.root_box.add_widget(self._palette())
        self.root_box.add_widget(self._brush_controls())
        self.root_box.add_widget(self._actions())
        self.status = Label(text="Ready to create ✦", size_hint_y=None, height=dp(24),
                            color=rgba(MUTED), font_size="12sp")
        self.root_box.add_widget(self.status)
        return self.root_box

    def _header(self):
        bar = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        title_box = BoxLayout(orientation="vertical", spacing=0)
        title_box.add_widget(Label(text="[b]Ahmed's art shop[/b]", markup=True, color=rgba(TEXT),
                                   font_size="20sp", halign="left", valign="middle"))
        title_box.add_widget(Label(text="YOUR POCKET ART STUDIO", color=rgba(MUTED),
                                   font_size="9sp", halign="left", valign="middle"))
        bar.add_widget(title_box)
        clear = self._button("New canvas", ACCENT, width=dp(100))
        clear.bind(on_release=lambda *_: self.confirm_clear())
        bar.add_widget(clear)
        return bar

    def _palette(self):
        outer = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(76), spacing=dp(4))
        outer.add_widget(Label(text="COLORS", color=rgba(MUTED), font_size="10sp",
                               size_hint_y=None, height=dp(16), halign="left"))
        row = BoxLayout(spacing=dp(5))
        for color, name in PALETTE:
            btn = Button(text="", background_normal="", background_down="", background_color=rgba(color))
            btn.bind(on_release=lambda _btn, c=color, n=name: self.choose_color(c, n))
            row.add_widget(btn)
        outer.add_widget(row)
        return outer

    def _brush_controls(self):
        panel = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(68), padding=[dp(10), dp(5)],
                          spacing=dp(2))
        with panel.canvas.before:
            Color(*rgba(PANEL_BG))
            panel_bg = Rectangle(pos=panel.pos, size=panel.size)
        panel.bind(pos=lambda w, *_: setattr(panel_bg, "pos", w.pos),
                   size=lambda w, *_: setattr(panel_bg, "size", w.size))
        top = BoxLayout(size_hint_y=None, height=dp(24))
        top.add_widget(Label(text="BRUSH SIZE", color=rgba(MUTED), font_size="10sp", halign="left"))
        self.size_value = Label(text="5 px", color=rgba(TEXT), font_size="12sp", size_hint_x=None, width=dp(48))
        top.add_widget(self.size_value)
        panel.add_widget(top)
        self.size_slider = Slider(min=1, max=35, value=5, cursor_size=(dp(18), dp(18)))
        self.size_slider.bind(value=self.change_size)
        panel.add_widget(self.size_slider)
        return panel

    def _actions(self):
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        actions = [
            ("Undo", "#343949", self.do_undo),
            ("Redo", "#343949", self.do_redo),
            ("Eraser", "#343949", self.toggle_eraser),
            ("Paper", "#343949", self.change_paper),
            ("Save PNG", ACCENT, self.save_art),
        ]
        for label, color, callback in actions:
            b = self._button(label, color)
            b.bind(on_release=lambda _b, cb=callback: cb())
            row.add_widget(b)
        return row

    def _button(self, text, color, width=None):
        b = Button(text=text, size_hint_x=None if width else 1, width=width,
                   background_normal="", background_down="", background_color=rgba(color),
                   color=rgba(TEXT), font_size="12sp")
        return b

    def choose_color(self, color, name):
        self.canvas_area.brush_color = color
        self.canvas_area.eraser = False
        self.status.text = f"{name} selected"
        self.status.color = rgba(MUTED)

    def change_size(self, _, value):
        self.canvas_area.brush_size = dp(value)
        self.size_value.text = f"{int(value)} px"

    def toggle_eraser(self):
        self.canvas_area.eraser = not self.canvas_area.eraser
        self.status.text = "Eraser on" if self.canvas_area.eraser else "Brush on"
        self.status.color = rgba("#FACC15" if self.canvas_area.eraser else MUTED)

    def do_undo(self):
        self.canvas_area.undo()
        self.status.text = "Undo"

    def do_redo(self):
        self.canvas_area.redo()
        self.status.text = "Redo"

    def change_paper(self):
        options = [("#FFFFFF", "White"), ("#FFF7ED", "Warm"), ("#E0F2FE", "Sky"), ("#F3E8FF", "Lilac"), ("#111827", "Dark")]
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        pop = Popup(title="Choose paper", content=box, size_hint=(.85, .55))
        for color, label in options:
            b = self._button(label, color)
            b.color = rgba("#111111" if color != "#111827" else "#FFFFFF")
            b.size_hint_y = None
            b.height = dp(42)
            b.bind(on_release=lambda _b, c=color, p=pop: (self.canvas_area.set_background(c), setattr(self.canvas_area, "eraser", False), p.dismiss()))
            box.add_widget(b)
        pop.open()

    def confirm_clear(self):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        box.add_widget(Label(text="Start a new blank canvas? This clears your current drawing.", color=rgba(TEXT)))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        pop = Popup(title="New canvas", content=box, size_hint=(.85, .35))
        no = self._button("Cancel", "#343949")
        yes = self._button("Clear canvas", "#E11D48")
        no.bind(on_release=pop.dismiss)
        yes.bind(on_release=lambda *_: (self.canvas_area.clear(), pop.dismiss(), setattr(self.status, "text", "New canvas ready")))
        row.add_widget(no); row.add_widget(yes); box.add_widget(row)
        pop.open()

    def save_art(self):
        try:
            folder = os.path.join(self.user_data_dir, "artworks")
            os.makedirs(folder, exist_ok=True)
            filename = "ahmed_art_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
            path = os.path.join(folder, filename)
            self.canvas_area.save(path)
            self.status.text = "Saved: " + filename
            self.status.color = rgba("#22C55E")
            self.show_saved(path)
        except Exception as exc:
            self.status.text = "Save failed: " + str(exc)
            self.status.color = rgba("#F43F5E")

    def show_saved(self, path):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        box.add_widget(Label(text="Your artwork was saved as a PNG inside the app's private storage.", color=rgba(TEXT)))
        box.add_widget(Label(text=os.path.basename(path), color=rgba(MUTED), font_size="12sp"))
        done = self._button("Great", ACCENT)
        done.size_hint_y = None
        done.height = dp(44)
        box.add_widget(done)
        pop = Popup(title="Artwork saved", content=box, size_hint=(.85, .3))
        done.bind(on_release=pop.dismiss)
        pop.open()

if __name__ == "__main__":
    ArtShopApp().run()
