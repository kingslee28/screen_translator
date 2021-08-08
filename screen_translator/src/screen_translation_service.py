import logging
import tkinter as tk
import pyautogui

from utils import wrap_text


class ScreenTranslationService:

    def __init__(self, cfg, text_detector, translator):
        self.text_detector = text_detector
        self.translator = translator

        self.display_popup_size = cfg['display_popup_size']
        self.message_box_width = cfg['message_box_width']
        self.text_width = cfg['text_width']
        self.translate_button = cfg['translate_button']
        self.output_filename = cfg['output_filename']
        self.topx, self.topy, self.botx, self.boty = 0, 0, 0, 0

        self.root = tk.Tk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry('%sx%s' % (self.screen_width, self.screen_height))
        self.root.configure(background='grey')
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.5)

        self.canvas = None
        self.rect_id = None
        self.setup_canvas()

        self.display = None
        self.root.mainloop()

    def setup_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=self.screen_width, height=self.screen_height, borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True)

        # Create selection rectangle (invisible since corner points are equal).
        self.rect_id = self.canvas.create_rectangle(
            self.topx, self.topy, self.botx, self.boty, dash=(5, 5), fill='', outline='black')

        self.canvas.bind('<Button-1>', self.get_mouse_position)
        self.canvas.bind('<B1-Motion>', self.update_rectangle)
        self.canvas.focus_set()
        self.canvas.bind(f'<{self.translate_button}>', self.launch_display)

    def get_mouse_position(self, event):
        self.topx, self.topy = event.x, event.y

    def update_rectangle(self, event):
        self.botx, self.boty = event.x, event.y
        self.canvas.coords(self.rect_id, self.topx, self.topy, self.botx, self.boty)

    def launch_display(self, event):
        self.display = tk.Toplevel()
        self.display.geometry(self.display_popup_size)
        self.display.title(f'Press "Translate" or "{self.translate_button}" of your keyboard')
        self.display.protocol('WM_DELETE_WINDOW', self.root.destroy)
        self.display.bind(f'<{self.translate_button}>', self.screen_translate)
        tk.Button(self.display, text='Translate', command=self.screen_translate).place(x=10, y=10)
        tk.Label(self.display, text='Original Text').place(x=10, y=60)
        tk.Label(self.display, text='Translated Text').place(x=10, y=210)
        self.root.withdraw()

    def save_screenshot(self, *args):
        screenshot = pyautogui.screenshot(region=(self.topx, self.topy, self.botx-self.topx, self.boty-self.topy))
        screenshot.save(self.output_filename)

    def screen_translate(self, *args):
        self.save_screenshot()
        detection = self.text_detector.detect_text_from_image(self.output_filename)
        translation = self.translator.translate_text(detection)
        logging.info(detection)
        logging.info(f'--> {translation}')
        detection = wrap_text(detection, self.text_width, self.translator.source_word_split)
        translation = wrap_text(translation, self.text_width, self.translator.target_word_split)
        tk.Message(self.display, text=detection, width=self.message_box_width).place(x=10, y=100)
        tk.Message(self.display, text=translation, width=self.message_box_width).place(x=10, y=250)
