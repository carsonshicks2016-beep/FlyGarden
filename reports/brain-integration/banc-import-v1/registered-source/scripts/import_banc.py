"""Register or resume the separate BANC anatomical import; no neural simulations."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cns_audit.banc import Audit, load_protocol, register


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['register','run'])
    args = parser.parse_args()
    if args.action == 'register': register()
    else: Audit(load_protocol()).run()


if __name__ == '__main__': main()
