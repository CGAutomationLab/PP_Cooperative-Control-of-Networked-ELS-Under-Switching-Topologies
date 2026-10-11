#!/usr/bin/env python3
"""Public-path compatibility publisher for unchanged proprietary PPV18 binaries.

This is infrastructure only, not the observer or controller algorithm.
It accepts the binaries' private raw Path topics and republishes the complete
6001-sample records to the ORIGINAL public topics at 1 Hz after completion.
"""
import functools
import os
import time
from pathlib import Path as FilePath

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from nav_msgs.msg import Path


class FinalPathRelay(Node):
    def __init__(self):
        super().__init__('pp_final_path_relay')
        self.declare_parameter('mode', 'observer')
        self.declare_parameter('period_sec', 1.0)
        self.mode = self.get_parameter('mode').value
        assert self.mode in ('observer', 'tracking')
        self.topic_prefix = 'pp_observer' if self.mode == 'observer' else 'pp_tracking'
        self.raw_prefix = 'pp_observer_raw' if self.mode == 'observer' else 'pp_tracking_raw'
        period = max(0.2, float(self.get_parameter('period_sec').value))
        latched = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=1,
                             reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.full = {}
        self.publisher = {}
        self.finished_arms = set()
        self.summarized_arms = set()
        self.session_start_wall = time.time()
        self.subscribers = []
        for arm in range(1, 7):
            for joint in (1, 2):
                ident = (arm, joint)
                raw_topic = f'/{self.raw_prefix}{arm}/joint{joint}_path'
                pub_topic = f'/{self.topic_prefix}{arm}/joint{joint}_path'
                self.publisher[ident] = self.create_publisher(Path, pub_topic, latched)
                self.subscribers.append(self.create_subscription(
                    Path, raw_topic, functools.partial(self._on_path, arm=arm, joint=joint),
                    latched))
        self.timer = self.create_timer(period, self._republish)

    def _on_path(self, msg, arm, joint):
        ident = (arm, joint)
        if ident in self.full:
            return
        # Require a completed, 30s record; do not expose intermediate
        # growing tracking Paths on the stable paper evaluation interface.
        if (len(msg.poses) < 6001 or
                msg.poses[-1].pose.position.x < 29.999):
            return
        self.full[ident] = msg
        if ((arm, 1) in self.full and (arm, 2) in self.full and
                arm not in self.finished_arms):
            self.finished_arms.add(arm)
            self.get_logger().info(
                f'{self.mode.upper()} arm{arm} FINISHED: '
                'updates=6000/6000; duration=30.000 s; '
                f'samples joint1={len(self.full[(arm, 1)].poses)} '
                f'joint2={len(self.full[(arm, 2)].poses)}; '
                'complete Path topics repeat at 1 Hz')
            for j in (1, 2):
                self.publisher[(arm, j)].publish(self.full[(arm, j)])
            if len(self.finished_arms) == 6:
                self.get_logger().info(
                    f'ALL SIX {self.mode.upper()} PATH SETS READY; '
                    'publishers remain active until shutdown.')

    def _summary_file(self, arm):
        return FilePath(os.path.expanduser(
            f'~/pp_data/PPV18/{self.mode}/{self.mode}{arm}_diagnostic_summary.txt'))

    def _report_diagnostic_summary(self, arm):
        if arm in self.summarized_arms:
            return
        summary_path = self._summary_file(arm)
        try:
            if summary_path.stat().st_mtime < self.session_start_wall:
                return  # Ignore any summary from a previous test session.
            pairs = {}
            for line in summary_path.read_text().splitlines():
                if '=' in line:
                    k, v = line.split('=', 1)
                    pairs[k.strip()] = v.strip()
            metrics = (('main_updates_completed', 'max_abs_qhat',
                        'max_consensus_norm', 'numerical_fault')
                       if self.mode == 'observer' else
                       ('control_updates', 'trigger_count',
                        'max_abs_tracking_error', 'timing_valid',
                        'constraint_violation_steps'))
            visible = [f'{k}={pairs[k]}' for k in metrics if k in pairs]
            if visible:
                self.get_logger().info(
                    f'{self.mode.upper()} arm{arm} RESULT: ' + '; '.join(visible))
                self.summarized_arms.add(arm)
        except (OSError, UnicodeError, ValueError):
            pass  # A new file may still be under construction by the C++ node.

    def _republish(self):
        for arm in sorted(self.finished_arms):
            for joint in (1, 2):
                self.publisher[(arm, joint)].publish(self.full[(arm, joint)])
            self._report_diagnostic_summary(arm)


def main():
    rclpy.init()
    node = FinalPathRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
