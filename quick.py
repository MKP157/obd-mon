import obd
import curses
import time
import os

# Custom Python files
import visuals

WIDTH = int(os.get_terminal_size()[0])
HEIGHT = int(os.get_terminal_size()[1])

def main(stdscr):
    # Initialize curses #############
    stdscr.clear()
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)

    conn = obd.OBD(obd.scan_serial()[1])
    while not conn:
        print("No serial detected, retrying...")
        conn = obd.OBD(obd.scan_serial()[1])

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "        Speed: " + str(conn.query(obd.commands.SPEED)))
        stdscr.addstr(1, 0, "          RPM: " + str(conn.query(obd.commands.RPM)))
        stdscr.addstr(2, 0, "  Engine load: " + str(conn.query(obd.commands.ENGINE_LOAD)))
        stdscr.addstr(3, 0, " Throttle pos: " + str(conn.query(obd.commands.THROTTLE_POS)))
        stdscr.addstr(4, 0, "  Intake temp: " + str(conn.query(obd.commands.INTAKE_TEMP)))
        stdscr.addstr(5, 0, "   Fuel level: " + str(conn.query(obd.commands.FUEL_LEVEL)))
        stdscr.addstr(6, 0, " Coolant temp: " + str(conn.query(obd.commands.COOLANT_TEMP)))
        stdscr.addstr(7, 0, "Engine Uptime: " + str(conn.query(obd.commands.RUN_TIME)))

        stdscr.refresh()
        #time.sleep(0.5)

# We use a wrapper to clean up the terminal on exit.
curses.wrapper(main)



connection = obd.OBD(obd.scan_serial()[1])

