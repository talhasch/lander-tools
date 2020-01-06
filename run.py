import argparse
import os
import sys

assert sys.version_info[0] == 3 and sys.version_info[1] >= 5, 'Requires Python 3.5 or newer'

os.sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from lander.util import assert_env_vars

assert_env_vars('DB_URL', 'MONGO_URL')


def main():
    parser = argparse.ArgumentParser(description='')
    cmd_list = (
        'file-sync',
        'info'
    )

    parser.add_argument('cmd', choices=cmd_list, nargs='?', default='info')

    args = parser.parse_args()
    cmd = args.cmd

    if cmd == 'file-sync':
        from lander.file_sync import main
        main()

    if cmd == 'info':
        print("Lander Helper")


if __name__ == '__main__':
    main()
