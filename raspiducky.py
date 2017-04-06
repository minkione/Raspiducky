#!/usr/bin/python

import argparse
import subprocess
from time import sleep

import keyboard_layouts.current as kb


class Raspiducky:
    def_delay = 0
    hid_dev = "/dev/hidg0"
    hid_bin = "./hid-gadget-test"
    last_cmd = ""
    last_string = ""
    run_cmd = True

    def getKBCode(self, char):
        try:
            return kb.KEYBOARD_LAYOUT[char]
        except KeyError:
            return char.lower()

    def exec_code(self, code, code_type="keyboard"):
        p1 = subprocess.Popen(["echo", code], stdout=subprocess.PIPE)
        p2 = subprocess.Popen([self.hid_bin, self.hid_dev, code_type], stdin=p1.stdout, stdout=subprocess.PIPE)
        p2.communicate()

    def parse_cmd(self, cmd):
        if (cmd[0] == "ENTER"):
            return "enter"
        elif cmd[0] in ["WINDOWS", "GUI"]:
            return "left-meta " + cmd[1].lower()
        elif cmd[0] in ["MENU", "APP"]:
            return "left-shift f10"
        elif cmd[0] in ["DOWNARROW", "DOWN"]:
            return "down"
        elif cmd[0] in ["LEFTARROW", "LEFT"]:
            return "left"
        elif cmd[0] in ["RIGHTARROW", "RIGHT"]:
            return "right"
        elif cmd[0] in ["UPARROW", "UP"]:
            return "up"
        elif cmd[0] in ["BREAK", "PAUSE"]:
            return "pause"
        elif cmd[0] in ["ESC", "ESCAPE"]:
            return "escape"
        elif (cmd[0] == "PRINTSCREEN"):
            return "print"
        elif cmd[0] in ["CAPSLOCK", "DELETE", "END", "HOME", "INSERT", "NUMLOCK", "PAGEUP", "PAGEDOWN",
                        "SCROLLLOCK", "SPACE", "TAB", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
                        "F10", "F11", "F12"]:
            return cmd[0].lower()

    def run(self, payload):
        with open(payload) as f:
            for line in f:
                cmd = line.replace('\n', '').replace('\r', '').split(' ', 1)
                # KEYBOARD
                if (cmd[0] == ""):
                    continue  # Discard empty lines
                elif (cmd[0] == "STRING"):
                    self.run_cmd = False
                    self.last_cmd = "STRING"
                    self.last_string = cmd[1]
                    for c in cmd[1]:
                        self.exec_code(self.getKBCode(c))
                elif (cmd[0] == "DELAY"):
                    self.run_cmd = False
                    self.last_cmd = "UNS"
                    sleep(float(cmd[1]) / 1000000.0)
                elif cmd[0] in ["DEFAULTDELAY", "DEFAULT_DELAY"]:
                    self.run_cmd = False
                    self.last_cmd = "UNS"
                    self.def_delay = float(cmd[1]) / 1000000.0
                elif (cmd[0] == "REM"):
                    print(cmd[1])
                elif (cmd[0] == "SHIFT"):
                    self.last_cmd = "left-shift " + self.parse_cmd(cmd[1].split(' ', 1))
                elif cmd[0] in ["CONTROL", "CTRL"]:
                    self.last_cmd = "left-ctrl " + self.parse_cmd(cmd[1].split(' ', 1))
                elif (cmd[0] == "CTRL-SHIFT"):
                    self.last_cmd = "left-ctrl left-shift " + self.parse_cmd(cmd[1].split(' ', 1))
                elif (cmd[0] == "ALT"):
                    self.last_cmd = "left-alt " + self.parse_cmd(cmd[1].split(' ', 1))
                elif (cmd[0] == "ALT-SHIFT"):
                    self.last_cmd = "left-shift left-alt"
                elif (cmd[0] == "REPEAT"):
                    self.run_cmd = False
                    if self.last_cmd not in ["UNS", "REM", ""]:
                        for time in xrange(int(cmd[1])):
                            if (self.last_cmd == "STRING"):
                                for c in self.last_string:
                                    self.exec_code(self.getKBCode(c))
                            else:
                                self.exec_code(self.last_cmd)
                else:
                    self.last_cmd = self.parse_cmd(cmd)

                # Run a new command
                if (self.run_cmd):
                    self.exec_code(self.last_cmd)

                self.run_cmd = True  # reset the value

                sleep(self.def_delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', '-p', required=True, help='Path to payload file')
    args = parser.parse_args()

    ducky = Raspiducky()
    ducky.run(args.payload)
