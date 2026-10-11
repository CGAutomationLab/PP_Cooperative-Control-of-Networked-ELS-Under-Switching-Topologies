#!/usr/bin/env python3
"""One-shot controller state recovery for six Gazebo manipulators.

Starts after the normal spawners. Detects controllers left inactive by the
startup race and activates them; fails loudly if an arm cannot be recovered.
It never deactivates an already active controller.
"""
import re
import subprocess
import sys
import time

ARMS = range(1, 7)
MAX_SECONDS = 120.0


def run(*argv, timeout=12):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return type('Result', (), {'returncode': 1, 'stdout': '', 'stderr': str(exc)})()


def controller_state(arm, controller):
    result = run('ros2', 'control', 'list_controllers',
                 '-c', f'/arm{arm}/controller_manager', timeout=8)
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == controller:
            return parts[-1].lower()
    return 'missing'


def fix(arm):
    manager = f'/arm{arm}/controller_manager'
    for controller in ('joint_state_broadcaster', 'effort_controller'):
        state = controller_state(arm, controller)
        if state == 'active':
            continue
        if state == 'inactive':
            result = run('ros2', 'control', 'set_controller_state',
                         controller, 'active', '-c', manager, timeout=15)
            if result.returncode == 0:
                print(f'[controller guard] arm{arm} {controller}: activation requested', flush=True)
            else:
                print(f'[controller guard] arm{arm} {controller}: activation failed: '
                      f'{result.stdout.strip()} {result.stderr.strip()}', flush=True)
        elif state == 'unconfigured':
            run('ros2', 'control', 'set_controller_state',
                controller, 'inactive', '-c', manager, timeout=15)
        # If still missing, leave loading to the ROS 2 spawner; recheck later.
    return all(controller_state(arm, c) == 'active'
               for c in ('joint_state_broadcaster', 'effort_controller'))


def main():
    deadline = time.monotonic() + MAX_SECONDS
    pending = set(ARMS)
    while pending and time.monotonic() < deadline:
        for arm in sorted(tuple(pending)):
            if fix(arm):
                print(f'[controller guard] arm{arm}: joint_state_broadcaster and '
                      'effort_controller ACTIVE', flush=True)
                pending.remove(arm)
        if pending:
            time.sleep(2.0)
    if pending:
        print(f'[controller guard] FAILED to activate controllers on: {sorted(pending)}',
              file=sys.stderr, flush=True)
        return 1
    print('[controller guard] ALL SIX ARMS READY.', flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
