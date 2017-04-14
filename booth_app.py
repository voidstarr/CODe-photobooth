
# -*- coding: utf8 -*-

import os
import sys
import time

import RPi.GPIO as GPIO
import picamera
import pygame

import backends
from libs.config import Config
from libs.gui import rounded_rect, Colors


class PhotoboothApp(object):
    config = Config()

    def __init__(self):
        self.runtime_id = 0
        self._canvas = None
        self._background = None
        self._photo_space = None
        self.target_dir = None
        self.font = None
        self._init_camera()
        self.photos = [] #TODO: remove this
        #self.printer = backends.acquire_backend("output", "line_printer", self.config)
        self._init_gpio()
        self._get_last_runtime_id()
        self.get_current_photo_directory()

        pygame.init()
        self.clock = pygame.time.Clock()
        self.limit_cpu_usage()
        display_mode = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN
        self._canvas = pygame.display.set_mode((0, 0), display_mode)
        self.screen_width = pygame.display.Info().current_w
        self.screen_height = pygame.display.Info().current_h
        self._background = self.fill_background()
        self._photo_space = self.fill_photo_space()
        self._running = True
        self.font = pygame.font.Font(self.config.get('font_filename'), self.config.getint('font_size'))
        pygame.mouse.set_visible(False)

    def _get_last_runtime_id(self):
        self.runtime_id = 0
        try:
            f = open(self.config.get("RUNTIME_ID_FILE"), "r")
            self.runtime_id = int(f.read())
            f.close()
        except (IOError, OSError, ValueError):
            pass

    def _acquire_new_runtime_id(self):
        self.runtime_id += 1
        f = open(self.config.get("RUNTIME_ID_FILE"), "w")
        f.write(str(self.runtime_id))
        f.close()

    def create_valid_photo_directory(self):
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)
            return True
        if os.path.isdir(self.target_dir):
            return not os.listdir(self.target_dir)
        return False

    def get_current_photo_directory(self):
        self.generate_runtime_dirname()
        while not self.create_valid_photo_directory():
            self._acquire_new_runtime_id()
            self.generate_runtime_dirname()

    def generate_runtime_dirname(self):
        base_dir = os.path.expanduser(self.config.get("TARGET_DIR"))
        runtime_dir = "photos-%04d" % self.runtime_id
        self.target_dir = os.path.join(base_dir, runtime_dir)

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.getint("SWITCH_PIN"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.config.getint("LED_PIN"), GPIO.OUT)
        self.enable_led(False)

    def _init_camera(self):
        self.camera = picamera.PiCamera()
        self.camera.annotate_text_size = 128
        self.camera.led = False
        self.camera.vflip = False
        self.camera.resolution = (self.config.getint("picture_width"), self.config.getint("picture_height"))

    def enable_led(self, mode):
        GPIO.output(self.config.getint("LED_PIN"), int(not mode))

    def wait_for_button(self):
        while True:
            button_pressed = GPIO.input(self.config.getint("SWITCH_PIN"))
            if button_pressed:
                return
            pygame.display.flip()
            time.sleep(0.1)
            self.parse_events()

    def fill_background(self):
        background = pygame.Surface((self.screen_width, self.screen_height))
        background_image = pygame.image.load(self.config.get("background_tile_image")).convert()
        for y in range(0, self.screen_height, background_image.get_height()):
            for x in range(0, self.screen_width, background_image.get_width()):
                background.blit(background_image, (x, y))
        return background

    def fill_photo_space(self):
        all_photos = pygame.Surface((self.screen_width, self.screen_height))

        #photo_filename = "images/sample-temp.png"
        #self.put_photo_on_surface(all_photos, photo_filename)

        all_photos.set_colorkey(Colors.BLACK)
        return all_photos

    def put_photo_on_surface(self, surface, filename):
        #gap_percentage = 5
        #width_gap = int(self.screen_width / 100 * gap_percentage)
        #height_gap = int(self.screen_height / 100 * gap_percentage)

        #frame_width = int((self.screen_width - 3* width_gap) / 2)
        #frame_height = int((self.screen_height - 3 * height_gap) / 2)

        #frame_x = width_gap if number % 2 != 0 else (2 * width_gap + frame_width)
        #frame_y = height_gap if number <= 2 else (2 * height_gap + frame_height)

        frame_x = 100
        frame_y = 100

        photo = self.load_and_scale_photo_for_display(filename, 100, 100)

        print("frame_x %d frame_y %d filename %s" % (frame_x, frame_y, filename))

        surface.blit(photo, (frame_x, frame_y))

    def display_disclaimer(self):
        self._photo_space = pygame.image.load("images/disclaimer.jpg")
        self.redraw_background()
    
    def load_and_scale_photo_for_display(self, photo_filename, x, y, scale=True):
        
        #frame_surface = pygame.Surface((photo_width, photo_height))
        #frame_surface.fill(Colors.WHITE)

        photo_surface = pygame.image.load(photo_filename)
        self.photos.append(photo_surface)
        #photo_width = frame_width - 2 * photo_width_gap
        #photo_height = frame_height - 2 * photo_height_gap
        
        if(scale):
            photo_width = int(((self.screen_width) - 2*x))
            photo_height = int(((self.screen_height) - 2*y))
            print("photo_width: %d photo_height: %d" % (photo_width, photo_height))
            return pygame.transform.scale(photo_surface, (photo_width, photo_height))
        else:
            return photo_surface
        #frame_surface.blit(scaled_surface, (photo_width, photo_height))


    def take_photo(self):
        time.sleep(1)
        self._photo_space = pygame.image.load("images/live_bg.jpg")
        self.redraw_background()
        pygame.display.flip()

        self.camera.start_preview()
        
        x = 40
        y = 0
        myWidth = self.screen_width - (2 * x)
        myHeight = self.screen_height - (2 * y)
        self.camera.preview.fullscreen = False
        self.camera.preview.window = (x, y, myWidth, myHeight)
        #self.camera.start_preview() #window = ((self.screen_width - myWidth)/2, (self.screen_height - myHeight)/2, myWidth, myHeight))
        #self.redraw_background(white_borders=True)
        print(self.camera.preview.window)

        for count in range(self.config.getint("countdown_seconds"), 0, -1):
            self.camera.annotate_text = str(count)
            time.sleep(1)
        self.camera.annotate_text = ""

        photo_filename = '%s/photobooth-temp.jpg' % (self.config.get("TEMP_DIR"))
        self.camera.capture(photo_filename)
        self.camera.stop_preview()
        self._photo_space = pygame.image.load("images/farewell.jpg")
        self.redraw_background()

        self.put_photo_on_surface(self._photo_space, photo_filename)

    def parse_events(self):
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                self._running = False
                self.cleanup()
                sys.exit(0)

    def limit_cpu_usage(self):
        self.clock.tick(self.config.getfloat("MAX_FPS"))

    def render_text(self, text, bg_color):
        overall_width = 0
        overall_height = 0
        text_lines = []
        for line in text.split('\n'):
            overall_width = max(overall_width, self.font.size(line)[0])
            overall_height += self.font.size(line)[1]
            text_lines.append(self.font.render(line, True, Colors.WHITE))

        top_and_bottom_margin_percentage = 10
        background_width = overall_width * (100 + top_and_bottom_margin_percentage) / 100
        background_height = overall_height * (100 + top_and_bottom_margin_percentage) / 100
        x = (self.screen_width - background_width) / 2
        y = 0 # (self.screen_height - background_height) / 6
        rounded_rect(self._canvas, (x, y, background_width, background_height), bg_color, radius=0.2)
        text_margin_percentage = top_and_bottom_margin_percentage / 2
        start_height = y + text_margin_percentage * overall_height / 100
        for i, line in enumerate(text_lines):
            label_x = (self.screen_width - line.get_width()) / 2
            label_y = start_height + i * line.get_height()
            self._canvas.blit(line, (label_x, label_y))

    def redraw_background(self, white_borders=False):
        self._canvas.blit(self._background, (0, 0))
        self._canvas.blit(self._photo_space, (0, 0))
        if white_borders:
            photo_height = self.config.getint("picture_height")
            rect_height = int((self.screen_height - photo_height) / 2)
            rect_size = (self.screen_width, rect_height)
            border_rect = pygame.Surface(rect_size)
            border_rect.fill(Colors.WHITE)
            self._canvas.blit(border_rect, (0, 0))
            self._canvas.blit(border_rect, (0, rect_height + photo_height))
        pygame.display.flip()

    def render_and_save_photo(self, photo_filename):
        dpi = self.config.getfloat("printer_dpi")
        width = dpi * self.config.getfloat("printer_width_inch")
        height = dpi * self.config.getfloat("printer_height_inch")
        print_surface = pygame.Surface((width, height))
        print_surface.fill(Colors.WHITE)
        #TODO: scale to instagram photo size & remove this for loop
        for number, photo in enumerate(self.photos):
            scaled_photo = pygame.transform.scale(photo, (int(width), int(height)))
            scaled_photo = pygame.transform.flip(scaled_photo, True, False)
            print_surface.blit(scaled_photo,(0,0))
        
        pygame.image.save(print_surface, photo_filename)

    def generate_photo_filename(self):
        picture = "%d.jpg" % time.time()
        filename = os.path.join(self.target_dir, picture)
        return os.path.normpath(filename)

    def stage_greeting(self):
        self.photos = []
        self.redraw_background()
        #TODO: disclaimer text
        #self.render_text(u"Welcome, blah blah blah", bg_color=Colors.ORANGE)
        pygame.display.flip()
        self.enable_led(True)
        self.display_disclaimer()
        self.wait_for_button()
        self.enable_led(False)

    def stage_farewell(self):
        time.sleep(2)
        self.render_text(u"Thanks! Sending to IG..", bg_color=Colors.RED)
        #self._photo_space = pygame.image.load("images/farewell.jpg")
        #self.redraw_background()

        pygame.display.flip()
        photo_filename = self.generate_photo_filename()
        self.render_and_save_photo(photo_filename)
        #self.printer.export(photo_filename)
        self.photos = []

        time.sleep(10)
        self._photo_space = self.fill_photo_space()

    def stage_photos(self):
        self.take_photo()
        self.redraw_background()

    def cleanup(self):
        GPIO.cleanup()
        pygame.quit()

    def launch_app(self):
        while self._running:
            self.stage_greeting()
            self.stage_photos()
            self.stage_farewell()
        self.cleanup()


if __name__ == "__main__":
    photo_app = PhotoboothApp()
    photo_app.launch_app()
