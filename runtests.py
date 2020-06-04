#!/usr/bin/env python
import os
import sys
import pytest

BASE = os.path.dirname(os.path.realpath(__file__))


def main():
    args = [
        '-v',
        '--tb=short',
    ]

    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    else:
        args.append('--cov=.')

    if all(arg.startswith('-') for arg in args):
        args.append('tests')

    sys.path.append(BASE)

    from tests.conftest import install_loader_patcher
    install_loader_patcher()

    print('pytest %s' % ' '.join(args))
    raise SystemExit(pytest.main(args))


if __name__ == '__main__':
    main()
