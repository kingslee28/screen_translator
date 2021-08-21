import logging
import pandas as pd
import pyautogui
import tkinter as tk

from utils import wrap_text


class ScreenTranslationService:

    def __init__(self, cfg, text_detector, translator, dictionary_path):
        logging.info('Initializing screen translation service...\n')
        self.text_detector = text_detector
        self.translator = translator
        self.dictionary_path = dictionary_path
        self.dictionary = None
        self.load_dictionary()

        self.display_popup_size = cfg['display_popup_size']
        self.text_width = cfg['text_width']
        self.translate_button = cfg['translate_button']
        self.translated_text_height = int(int(self.display_popup_size.split('x')[1]) / 2)
        self.output_filename = cfg['output_filename']
        self.topx, self.topy, self.botx, self.boty = 0, 0, 0, 0

        self.root = tk.Tk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry('%sx%s' % (self.screen_width, self.screen_height))
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0)

        self.display = None
        self.launch_display()
        self.mask = None
        self.canvas = None
        self.rect_id = None
        self.root.mainloop()

    def load_dictionary(self, *args):
        dictionary = pd.read_csv(self.dictionary_path).fillna('')
        self.dictionary = dict(dictionary.to_dict('split')['data'])

    def setup_canvas(self, *args):
        self.mask = tk.Tk()
        self.mask.geometry('%sx%s' % (self.screen_width, self.screen_height))
        self.mask.configure(background='grey')
        self.mask.overrideredirect(True)
        self.mask.attributes('-alpha', 0.5)

        self.canvas = tk.Canvas(
            self.mask, width=self.screen_width, height=self.screen_height, borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True)

        # Create selection rectangle (invisible since corner points are equal).
        self.rect_id = self.canvas.create_rectangle(
            self.topx, self.topy, self.botx, self.boty, dash=(5, 5), fill='', outline='black')

        self.canvas.bind('<Button-1>', self.get_mouse_position)
        self.canvas.bind('<B1-Motion>', self.update_rectangle)
        self.canvas.focus_set()
        self.canvas.bind(f'<B1-ButtonRelease>', self.remove_mask)

    def get_mouse_position(self, event):
        self.topx, self.topy = event.x, event.y

    def update_rectangle(self, event):
        self.botx, self.boty = event.x, event.y
        self.canvas.coords(self.rect_id, self.topx, self.topy, self.botx, self.boty)

    def remove_mask(self, event):
        self.mask.destroy()

    def launch_display(self):
        self.display = tk.Toplevel()
        self.display.geometry(self.display_popup_size)
        self.display.title(f'Press "Translate" or "{self.translate_button}" of your keyboard')
        self.display.protocol('WM_DELETE_WINDOW', self.root.destroy)
        self.display.bind(f'<{self.translate_button}>', self.screen_translate)
        tk.Button(self.display, text='Translate', command=self.screen_translate).place(x=10, y=10)
        tk.Button(self.display, text='Select Area', command=self.setup_canvas).place(x=100, y=10)
        tk.Button(self.display, text='Reload Dictionary', command=self.load_dictionary).place(x=210, y=10)
        tk.Label(self.display, text='Original Text').place(x=10, y=60)
        tk.Label(self.display, text='Translated Text').place(x=10, y=self.translated_text_height)

    def save_screenshot(self, *args):
        screenshot = pyautogui.screenshot(region=(self.topx, self.topy, self.botx-self.topx, self.boty-self.topy))
        screenshot.save(self.output_filename)

    def screen_translate(self, *args):
        self.save_screenshot()

        detection = self.text_detector.detect_text_from_image(self.output_filename).replace('\n', '')
        logging.info(detection)
        detection = wrap_text(detection, self.text_width, self.translator.source_word_split)
        detection_label = tk.Label(self.display, textvariable=tk.StringVar(name='detection'), justify='left')
        detection_label.place(x=10, y=100)
        detection_label.setvar('detection', detection)
        for i, (k, v) in enumerate(self.dictionary.items()):
            detection = detection.replace(k, f'<{i}>')

        translation = self.translator.translate_text(detection).replace('\n', '')
        for i, (k, v) in enumerate(self.dictionary.items()):
            translation = translation.replace(f'<{i}>', v)
        logging.info(f'--> {translation}\n')
        translation = wrap_text(translation, self.text_width, self.translator.target_word_split)
        translation_label = tk.Label(self.display, textvariable=tk.StringVar(name='translation'), justify='left')
        translation_label.place(x=10, y=self.translated_text_height + 40)
        translation_label.setvar('translation', translation)
