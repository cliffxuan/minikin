# -*- coding: utf-8 -*-
"""
load test using locustio in distributed mode
"""
import argparse
import os
import subprocess

PWD = os.path.abspath(os.path.dirname(__file__))


def argument_parser():
    default_locustfile = os.path.join(PWD, 'locustfile.py')
    parser = argparse.ArgumentParser(description='run locust load test')
    parser.add_argument(
        '--file', '-f',
        dest='locustfile',
        help=f'locust file default to {default_locustfile}',
        default=default_locustfile
    )
    parser.add_argument(
        '--host', '-t', help='host of server under test',
        default='http://localhost:8080')
    parser.add_argument(
        '--web', action='store_true',
        help='run with web UI')
    parser.add_argument(
        '--num', '-n', type=int,
        help='number of slaves', default=2)
    parser.add_argument(
        '--concurrency', '-c', help='number of concurrent users',
        default=1000)
    parser.add_argument(
        '--hatch-rate', '-r', help='hatch rate',
        default=1000)
    return parser


def run(locustfile, host, num, web, concurrency, hatch_rate):
    if web:
        master = subprocess.Popen([
            'locust', '-f', locustfile, f'--host={host}', '--master'])

        slaves = [
            subprocess.Popen([
                'locust', '-f', locustfile,
                f'--host={host}', '--slave',
                '--master-host=localhost'
            ])
            for i in range(num)
        ]
    else:
        master = subprocess.Popen([
            'locust', '-f', locustfile, '--no-web',
            '-c', f'{concurrency}', '-r', f'{hatch_rate}',
            f'--host={host}', '--master',
            f'--expect-slaves={num}'
        ])

        slaves = [
            subprocess.Popen([
                'locust', '-f', locustfile,
                f'--host={host}', '--slave',
                '--master-host=localhost'
            ])
            for i in range(num)
        ]
    try:
        while True:
            master.poll()
            for slave in slaves:
                slave.poll()
    except KeyboardInterrupt:
        master.kill()
        for slave in slaves:
            slave.poll()


def main(argv=None):
    args = argument_parser().parse_args(argv)
    run(args.locustfile, args.host, args.num, args.web,
        args.concurrency, args.hatch_rate)


if __name__ == '__main__':
    main()
