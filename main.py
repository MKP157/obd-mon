import obd
import curses
import time
import os
import sys
import platform
from re import search

# Custom imports
from visuals import Colours

ENVIRONMENT = ""

TERM_WIDTH = int(os.get_terminal_size()[0])
TERM_HEIGHT = int(os.get_terminal_size()[1])
MARGIN_VERTICAL = 1
MARGIN_HORIZONTAL = 3
GAUGE_HEIGHT = 4

CODES = [obd.commands.SPEED,
         obd.commands.RPM,
         #obd.commands.FUEL_LEVEL,
         #obd.commands.RELATIVE_ACCEL_POS,
         #obd.commands.FUEL_RATE,
         obd.commands.ENGINE_LOAD,
         obd.commands.COOLANT_TEMP]

MAXES = [ 160,
          8000,
          #100,
          #100,
          #0,
          100,
          120 ]


def connect_odb_reader():
    print(Colours.fg.yellow, "\N{Warning Sign} Attempting to connect to a your car's OBD-II diagnostic port.\r")

    serial_options = obd.scan_serial()
    for option in serial_options:
        print(Colours.fg.yellow, f"\N{Warning Sign} Attempting to connect to a serial device {option}...\r")

        serial_connection = obd.OBD(option, fast=True)

        if serial_connection.is_connected():
            print(Colours.fg.lightgreen, "Connection to car over OBD-II successful!\nInitializing...\r")
            return serial_connection

        elif serial_connection.status() == obd.OBDStatus.ELM_CONNECTED:
            print(Colours.fg.lightred, "\N{Warning Sign} Only a connection with your ELM adapter could be made.\n"
                                       "Please plug your ELM adapter into your car's OBD-II port and try again.\r")
            exit(1)

        else:
            print(Colours.fg.lightred, "\N{Warning Sign} Connection unsuccessful. Trying next device...\r")
            continue

    print(Colours.reset, "\N{Warning Sign} No OBD-II serial connections could be established. Quitting...\r")
    exit(1)


def program(stdscr):
    if ENVIRONMENT == "simulator":
        os_type = platform.system()
        match os_type:
            case "Linux":
                connection = obd.OBD("/dev/pts/0", baudrate=115200, )
            case "Darwin":
                connection = obd.OBD("/dev/ttys001", baudrate=115200, )
            case _:
                print("windows not supported")
                exit(1)
    else:
        connection = connect_odb_reader()

    # Initialize curses #############
    stdscr.clear()
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)

    curses.start_color()

    #curses.use_default_colors()
    #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)

    #######################################################
    def draw_rectangle(y, x, w, h, char):
        stdscr.addstr(y, x, char * w)
        stdscr.addstr(y + h - 1, x, char * (w // len(char)))
        for i in range(y + 1, y + h - 1):
            stdscr.addstr(i, x, char)
            stdscr.addstr(i, x + w - 1, char)

    #######################################################
    def draw_gauge_notches(y, x, w, h, notches, placement):
        segment_width = w // notches
        segment = " " * segment_width

        # Put in middle:
        if placement:
            segment = segment[:(segment_width // 2)] + "|" + segment[(segment_width // 2) + 1:]
        # Put at end:
        else:
            segment = segment[:-1] + "|"

        lines = segment * notches

        for i in range(h):
            stdscr.addstr(y + i, x, lines)

    #######################################################
    def draw_gauge_complete(y, x, w, h):
        draw_rectangle(y, x, w, h, "#")
        draw_gauge_notches(y + 1, x + 1, w - 2, h - 2, 10, False)

    #######################################################
    # Main code

    gauges = [curses.newwin(GAUGE_HEIGHT,
                            (TERM_WIDTH // 2 - MARGIN_HORIZONTAL),
                            MARGIN_VERTICAL * pair[0] // 2 + GAUGE_HEIGHT * pair[0] // 2 + 1 if pair[0] % 2 == 0
                            else MARGIN_VERTICAL * (pair[0]-1) // 2 + GAUGE_HEIGHT * (pair[0]-1) // 2 + 1,
                            MARGIN_HORIZONTAL if pair[0] % 2 == 0
                            else TERM_WIDTH // 2 + MARGIN_HORIZONTAL // 2 )
              for pair in enumerate(CODES)]

    i = 0
    for gauge in gauges:
        gauge.border()
        gauge.addstr(0, 2, f" {CODES[i].name} ")
        i += 1
        gauge.redrawwin()
        gauge.overwrite(stdscr)
        gauge.clear()

        current_size = gauge.getmaxyx()
        gauge.resize(current_size[0]-2, current_size[1]-2)

        current_pos = gauge.getbegyx()
        gauge.mvwin(current_pos[0] + 1, current_pos[1] + 1)

    stdscr.refresh()

    while True:
        for code in enumerate(CODES):
            result = connection.query(code[1])

            gauges[code[0]].clear()
            gauges[code[0]].overwrite(stdscr)

            gauges[code[0]].addstr(0, 0, str(result.value))
            gauges[code[0]].attron(curses.color_pair(1))

            gauges[code[0]].hline(1, 0, "-", int((result.value.magnitude / MAXES[code[0]]) * (gauges[code[0]].getmaxyx()[1])))

            gauges[code[0]].attroff(curses.color_pair(1))
            gauges[code[0]].refresh()
            gauges[code[0]].overlay(stdscr)

        stdscr.refresh()
        time.sleep(0.05)


if __name__ == "__main__":
    print(sys.argv[1])
    if sys.argv[1].lower() in ["simulator", "sim", "emulator", "dev", "development"]:
        ENVIRONMENT = "simulator"

    else:
        ENVIRONMENT = "obd"

    # We use a wrapper to clean up the terminal on exit.
    curses.wrapper(program)
    print(Colours.reset)
