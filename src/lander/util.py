import os


def assert_env_vars(*args):
    for a in args:
        if os.environ.get(a) is None:
            raise AssertionError('{} environment variable required'.format(a))
