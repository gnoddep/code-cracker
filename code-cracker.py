import signal
import threading
import time
import random

import RPi.GPIO as GPIO

from Nerdman.LedButton import LedButton
from Nerdman.Button import Button

class CodeCracker:
    RED = 0
    GREEN = 1
    ORANGE = 2
    BLUE = 3

    RED_led = 23
    RED_button = 24
    GREEN_led = 21
    GREEN_button = 22
    ORANGE_led = 19
    ORANGE_button = 18
    BLUE_led = 15
    BLUE_button = 16

    def __init__(self):
        self.wait_mutex = threading.Event()
        signal.signal(signal.SIGINT, self.signal_handler)

        GPIO.setmode(GPIO.BOARD)

        self.led_buttons = [
            LedButton(self.RED_button, self.RED_led),
            LedButton(self.GREEN_button, self.GREEN_led),
            LedButton(self.ORANGE_button, self.ORANGE_led),
            LedButton(self.BLUE_button, self.BLUE_led),
        ]

        for button in self.led_buttons:
            button.set_callback(Button.PRESSED, self.handle_press_button_action)
            button.set_callback(Button.RELEASED, self.handle_release_button_action)

        self.code = []
        self.code_input = []

    def run(self):
        try:
            print("Press CTRL+C to exit")
            while not self.wait_mutex.wait():
                pass
            return
        except KeyboardInterrupt:
            pass
        finally:
            self.all_leds_off()

            GPIO.cleanup()

        sys.exit(0)

    def all_leds_off(self):
        for b in self.led_buttons:
            b.off()

    def all_leds_on(self):
        for b in self.led_buttons:
            b.on()

    def blink(self, times = 1):
        for _ in range(times):
            self.all_leds_off()
            time.sleep(0.3)
            self.all_leds_on()
            time.sleep(0.3)

        for b in self.led_buttons:
            b.off()

    def print_code(self, code):
        names = []
        for b in code:
            if b == self.led_buttons[self.RED]:
                names.append('RED')
            elif b == self.led_buttons[self.GREEN]:
                names.append('GREEN')
            elif b == self.led_buttons[self.ORANGE]:
                names.append('ORANGE')
            elif b == self.led_buttons[self.BLUE]:
                names.append('BLUE')
        print(names)

    def reset_code(self, blink = 2):
        self.code = []
        self.code_input = []
        self.blink(blink)

    def handle_reset_release_button_action(self, button):
        button.set_callback(Button.RELEASED, self.handle_release_button_action)

    def handle_press_button_action(self, button):
        button.on()

        if (self.led_buttons[self.RED].button_state() == Button.PRESSED
            and self.led_buttons[self.BLUE].button_state() == Button.PRESSED):
            print('RESET')
            self.led_buttons[self.RED].set_callback(Button.RELEASED, self.handle_reset_release_button_action)
            self.led_buttons[self.BLUE].set_callback(Button.RELEASED, self.handle_reset_release_button_action)
            self.reset_code()

    def handle_release_button_action(self, button):
        button.off()

        if len(self.code) == 0:
            for b in self.led_buttons:
                self.code.append(b)

            random.shuffle(self.code)
            self.print_code(self.code)

        if len(self.code_input) < len(self.code):
            self.code_input.append(button)
            self.print_code(self.code_input)

        if len(self.code_input) == len(self.code):
            if self.code_input == self.code:
                print('CORRECT!')
                self.reset_code(4)
            else:
                print('WRONG!')
                for i, b in enumerate(self.code_input):
                    if b == self.code[i]:
                        b.on()
                    else:
                        b.off()
                self.code_input = []
                time.sleep(1)
                self.all_leds_off()
                    

    def signal_handler(self, signal, frame):
        self.wait_mutex.set()

if __name__ == '__main__':
    main = CodeCracker()
    main.run()
