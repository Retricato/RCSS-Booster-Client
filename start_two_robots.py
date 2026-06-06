"""
start_two_robots.py
-------------------
Launches two nn_client agents with different starting positions.

Usage:
    python start_two_robots.py                          # defaults: T1, team=Test, players 1 & 2
    python start_two_robots.py --team RedTeam
    python start_two_robots.py --p1 3 --p2 7           # custom player numbers
    python start_two_robots.py --host 192.168.1.10      # remote server

Each agent runs in its own process and writes to its own CSV file in CSV/.
Press Ctrl+C to stop both agents.

Starting positions (from BEAM_POSES in nn_client.py):
    Player 1 → (27.5,  0.0) — right wing, centre line
    Player 2 → (22.0, 12.0) — right wing, 12 m to the left
    Player 3 → (22.0,  4.0) — right wing,  4 m to the left
    (change --p1 / --p2 to pick different spots)
"""

import argparse
import os
import signal
import subprocess
import sys
import time


# Map player number → starting beam position (for the status printout only).
# These must match BEAM_POSES in nn_client.py.
BEAM_POSES = {
    1:  (27.5,  0.0),
    2:  (22.0, 12.0),
    3:  (22.0,  4.0),
    4:  (22.0, -4.0),
    5:  (22.0,-12.0),
    6:  (15.0,  0.0),
    7:  ( 4.0, 16.0),
    8:  (11.0,  6.0),
    9:  (11.0, -6.0),
    10: ( 4.0,-16.0),
    11: ( 7.0,  0.0),
}


def main():
    parser = argparse.ArgumentParser(
        description='Launch two nn_client agents for RCSSServerMJ.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-s', '--host',  type=str, default='127.0.0.1',
                        help='Server IP address (default: 127.0.0.1)')
    parser.add_argument('-p', '--port',  type=int, default=60000,
                        help='Server port (default: 60000)')
    parser.add_argument('-t', '--team',  type=str, defa