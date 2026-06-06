"""
start_two_robots.py
-------------------
Launches two nn_client agents with different starting positions and roles.

Agent 1 = ATTACKER by default (walks toward the ball).
Agent 2 = SUPPORTER by default (takes a position 6m behind the ball).

Once both robots can see each other, the Voronoi logic in nn_client.py
takes over: whichever robot is closer to the ball becomes the attacker
automatically, and the other moves to the support position.

Usage:
    python start_two_robots.py                        # players 1 & 2, team=Test
    python start_two_robots.py --p1 3 --p2 7
    python start_two_robots.py --team RedTeam
    python start_two_robots.py --host 192.168.1.10

Press Ctrl+C to stop both agents.

Starting positions (from BEAM_POSES in nn_client.py):
    Player 1 -> (27.5,  0.0)   Player 2 -> (22.0, 12.0)
    Player 3 -> (22.0,  4.0)   Player 7 -> ( 4.0, 16.0)
"""

import argparse
import os
import signal
import subprocess
import sys
import time

BEAM_POSES = {
    1:  (27.5,  0.0), 2:  (22.0, 12.0), 3:  (22.0,  4.0),
    4:  (22.0, -4.0), 5:  (22.0,-12.0), 6:  (15.0,  0.0),
    7:  ( 4.0, 16.0), 8:  (11.0,  6.0), 9:  (11.0, -6.0),
    10: ( 4.0,-16.0), 11: ( 7.0,  0.0),
}


def main():
    parser = argparse.ArgumentParser(
        description='Launch two nn_client agents (attacker + supporter).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-s', '--host',  type=str, default='127.0.0.1',
                        help='Server IP address (default: 127.0.0.1)')
    parser.add_argument('-p', '--port',  type=int, default=60000,
                        help='Server port (default: 60000)')
    parser.add_argument('-t', '--team',  type=str, default='Test',
                        help='Team name (default: Test)')
    parser.add_argument('-r', '--robot', type=str, default='T1',
                        choices=['ant', 'T1'],
                        help='Robot model (default: T1)')
    parser.add_argument('--p1', type=int, default=1, metavar='PLAYER_NO',
                        help='Player number for agent 1 / attacker (default: 1)')
    parser.add_argument('--p2', type=int, default=2, metavar='PLAYER_NO',
                        help='Player number for agent 2 / supporter (default: 2)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Seconds between spawning the two agents (default: 0.5)')
    args = parser.parse_args()

    if args.p1 == args.p2:
        print('[ERROR] --p1 and --p2 must be different player numbers.')
        sys.exit(1)

    python = sys.executable
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nn_client.py')

    base_cmd = [
        python, script,
        '--host',  args.host,
        '--port',  str(args.port),
        '--team',  args.team,
        '--robot', args.robot,
    ]

    def pos_str(n):
        pos = BEAM_POSES.get(n, ('?', '?'))
        return f'x={pos[0]}, y={pos[1]}'

    print('=' * 60)
    print('  RCSSServerMJ — Two-Robot Test')
    print('=' * 60)
    print(f'  Server : {args.host}:{args.port}')
    print(f'  Team   : {args.team}   Robot: {args.robot}')
    print(f'  Agent 1: player_no={args.p1}  role=ATTACKER   start @ ({pos_str(args.p1)})')
    print(f'  Agent 2: player_no={args.p2}  role=SUPPORTER  start @ ({pos_str(args.p2)})')
    print(f'  CSV    : CSV/robot_log_{args.team}_p<N>_<timestamp>.csv')
    print('  Roles swap automatically once robots see each other (Voronoi).')
    print('=' * 60)
    print()

    # Agent 1 = ATTACKER  -> walks toward ball
    # Agent 2 = SUPPORTER -> moves to position 6m behind ball (toward own goal)
    # Voronoi logic in nn_client.py overrides roles dynamically once they
    # can see each other: closer robot = attacker, farther = supporter.
    p1 = subprocess.Popen(base_cmd + ['--player_no', str(args.p1),
                                       '--default-role', 'attacker'])
    print(f'[INFO] Agent 1 started  (PID {p1.pid}, player_no={args.p1}, role=attacker)')

    time.sleep(args.delay)

    p2 = subprocess.Popen(base_cmd + ['--player_no', str(args.p2),
                                       '--default-role', 'supporter'])
    print(f'[INFO] Agent 2 started  (PID {p2.pid}, player_no={args.p2}, role=supporter)')
    print('[INFO] Press Ctrl+C to stop both agents.\n')

    processes = [p1, p2]

    def shutdown(sig=None, frame=None):
        print('\n[INFO] Shutting down both agents...')
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1.0)
            rc1 = p1.poll()
            rc2 = p2.poll()
            if rc1 is not None:
                status = 'cleanly (rc=0)' if rc1 == 0 else f'with error (rc={rc1})'
                print(f'[INFO] Agent 1 (player_no={args.p1}) exited {status}')
            if rc2 is not None:
                status = 'cleanly (rc=0)' if rc2 == 0 else f'with error (rc={rc2})'
                print(f'[INFO] Agent 2 (player_no={args.p2}) exited {status}')
            if rc1 is not None and rc2 is not None:
                break
    except KeyboardInterrupt:
        shutdown()

    for p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()

    print('[INFO] Both agents stopped.')
    print('[INFO] CSV files saved in: CSV/')


if __name__ == '__main__':
    main()
