#!/usr/bin/env python

import os

from core.utils import get_benchmark, parser
from core.runner.RepairTask import RepairTask
from core.runner.get_runner import get_runner


if __name__ == "__main__":
    # Arja -b Bugs.jar -i Wicket-295e73bd
    # Arja -b Defects4J -i Chart-1
    args = parser.parse_args()

    if "benchmark" in args:
        args.benchmark = get_benchmark(args.benchmark)

        tasks = []

        # if without bug-id parameter, use all bug-ids.
        bugs = args.benchmark.get_bugs()
        if args.id is not None:
            bugs = []
            for bug_id in args.id:
                bugs.append(args.benchmark.get_bug(bug_id))

        for bug in bugs:
            args.bug = bug

            # Arja init (identify Arja main, jar file)
            tool = args.func(args)
            task = RepairTask(tool, args.benchmark, bug)
            if not args.continue_execution or not os.path.exists(os.path.join(task.log_dir(), "repair.log")):
                tasks.append(task)

        get_runner(tasks, args).execute()
