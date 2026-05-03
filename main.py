import subprocess
import random
from datetime import datetime, timedelta
import argparse
import os

# ---------- DEFAULT CONFIG ----------
DEFAULT_FILE = "notes.md"

# ---------- UTIL ----------
def run(cmd, env=None):
    subprocess.run(cmd, shell=True, check=True, env=env)

def random_time(start_hour, end_hour):
    hour = random.randint(start_hour, end_hour)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:00"

def chunk_weeks(start, end):
    weeks = []
    cur = start
    while cur <= end:
        week = []
        for _ in range(7):
            if cur <= end:
                week.append(cur)
            cur += timedelta(days=1)
        weeks.append(week)
    return weeks

# ---------- MAIN ----------
def generate(args):
    random.seed(args.seed)

    start = datetime.strptime(args.from_date, "%Y-%m-%d")
    end = datetime.strptime(args.to_date, "%Y-%m-%d")

    # safety checks
    if len(args.week_weights) != 5:
        raise ValueError("weekWeights must have 5 values (for 0–4 days/week)")

    weeks = chunk_weeks(start, end)
    commit_plan = []

    for week in weeks:
        active_days = random.choices(
            population=[0, 1, 2, 3, 4],
            weights=args.week_weights
        )[0]

        chosen_days = random.sample(week, min(active_days, len(week)))

        for day in chosen_days:
            commits = random.randint(args.min_per_day, args.max_per_day)

            for _ in range(commits):
                timestamp = (
                    day.strftime("%Y-%m-%d") + " " +
                    random_time(args.start_hour, args.end_hour)
                )
                commit_plan.append(timestamp)

    commit_plan.sort()

    # ensure file exists
    if not os.path.exists(args.file):
        with open(args.file, "w") as f:
            f.write("# Notes\n")

    # create commits
    for i, ts in enumerate(commit_plan):
        with open(args.file, "a") as f:
            f.write(f"log {i} @ {ts}\n")

        run(f"git add {args.file}")

        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = ts
        env["GIT_COMMITTER_DATE"] = ts

        run(f'git commit -m "{args.message_prefix}: {ts}"', env=env)

    print(f"✅ Created {len(commit_plan)} commits")

    if args.auto_push:
        try:
            run("git push")
        except:
            print("⚠ Push failed — run manually")

# ---------- CLI ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--from", dest="from_date", required=True)
    parser.add_argument("--to", dest="to_date", required=True)

    parser.add_argument("--seed", default="default")

    # commit intensity
    parser.add_argument("--minPerDay", dest="min_per_day", type=int, default=1)
    parser.add_argument("--maxPerDay", dest="max_per_day", type=int, default=3)

    # working hours
    parser.add_argument("--startHour", dest="start_hour", type=int, default=9)
    parser.add_argument("--endHour", dest="end_hour", type=int, default=21)

    # weekly behavior
    parser.add_argument(
        "--weekWeights",
        dest="week_weights",   # ✅ FIXED HERE
        type=float,
        nargs=5,
        default=[0.1, 0.2, 0.3, 0.25, 0.15],
        help="weights for [0,1,2,3,4] active days/week"
    )

    # file + commit style
    parser.add_argument("--file", default=DEFAULT_FILE)
    parser.add_argument("--messagePrefix", dest="message_prefix", default="update")

    # push control
    parser.add_argument("--autoPush", action="store_true")

    args = parser.parse_args()
    generate(args)



