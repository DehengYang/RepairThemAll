import os
import argparse

from core.utils import get_benchmark

parser = argparse.ArgumentParser(prog="checkout", description='Checkout bug')
parser.add_argument("--benchmark", "-b", required=True, default="Defects4J",
                        help="The benchmark to repair")
parser.add_argument("--id", "-i", required=True, help="The bug id")
parser.add_argument("--working_directory", "-w", required=True, help="The working directory")

# e.g., 
# /usr/bin/python /mnt/repairthemall/script/checkout.py  
# --benchmark Bears --id webfirmframework-wff-453188520-453188718 --working_directory /mnt/workingDir
if __name__ == "__main__":
    # receive -b, -i, -w parameters
    args = parser.parse_args()

    # get whole benchmark
    args.benchmark = get_benchmark(args.benchmark)

    # get single bug
    bug = args.benchmark.get_bug(args.id)

    # identify workdir
    bug_path = os.path.join(args.working_directory,
                            "%s_%s_%s" % (bug.benchmark.name, bug.project, bug.bug_id))
    # checkout bug and cp to workdir
    bug.checkout(bug_path)