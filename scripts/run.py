# Reads a GitHub Actions run, its jobs with their conclusions and times and, for each job that failed,
# timed out or was cancelled, the annotations of its check run and the last 60 lines of the step it
# stopped at. The lines go to a file whose path is printed, never to the terminal, since a job's log
# runs to thousands of lines and the end of one step is the part read.
#
#   python3 -I scripts/run.py <account/repo> <run id> <folder for the logs>
#
# It asks GitHub's API through gh, so the login gh holds serves and no token is handled here. Where
# RUN_ANSWERS names a JSON file of recorded answers, keyed by the API path asked, it reads them
# instead, which is how the tests run it with no network and no gh.
import json, os, re, subprocess, sys

repo, run, folder = sys.argv[1], sys.argv[2], sys.argv[3]
LINES = 60
COLOR = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
recorded = json.load(open(os.environ["RUN_ANSWERS"], encoding="utf-8")) if os.environ.get("RUN_ANSWERS") else None


# A job's log carries the colors its programs printed, which a newer gh refuses to print unless
# told to, a flag an older gh does not know, so the flag is given only where gh asks for it.
def api(path, text=False):
    if recorded is not None:
        return recorded[path]
    for flags in ([], ["--allow-escape-sequences"]):
        try:
            done = subprocess.run(["gh", "api", *flags, path], capture_output=True, encoding="utf-8", errors="replace")
        except FileNotFoundError:
            sys.exit("gh was not found. Install GitHub's command line and log in with gh auth login.")
        if done.returncode == 0 or "--allow-escape-sequences" not in done.stderr:
            break
    if done.returncode:
        sys.exit(f"gh api {path} failed. {done.stderr.strip()}")
    return done.stdout if text else json.loads(done.stdout)


# ISO times compare as strings, and a log line's time has seven decimals where a step's has none, so
# both are cut to the second.
def second(time): return (time or "")[:19]


def took(job):
    if not job.get("started_at") or not job.get("completed_at"):
        return job.get("status", "")
    from datetime import datetime
    start, end = (datetime.fromisoformat(second(job[k])) for k in ("started_at", "completed_at"))
    seconds = int((end - start).total_seconds())
    return f"{seconds // 60} min {seconds % 60} s" if seconds >= 60 else f"{seconds} s"


# The jobs come a hundred to a page, the most GitHub gives, and a page more is asked while some are missing.
jobs, page = [], 1
while True:
    answer = api(f"repos/{repo}/actions/runs/{run}/jobs?per_page=100&page={page}")
    jobs += answer["jobs"]
    if len(jobs) >= answer["total_count"] or not answer["jobs"]:
        break
    page += 1

head = api(f"repos/{repo}/actions/runs/{run}")
print(f"run {run}, {head['name']} at {head['head_sha'][:7]}, {head['status']}"
      + (f" {head['conclusion']}" if head.get("conclusion") else ""))
width = max((len(job["name"]) for job in jobs), default=0)
for job in jobs:
    print(f"  {job['name']:<{width}}  {job.get('conclusion') or job['status']:<10}  {took(job)}")

for job in jobs:
    if job.get("conclusion") not in ("failure", "timed_out", "cancelled"):
        continue
    steps = job.get("steps") or []
    stopped = next((s for s in steps if s.get("conclusion") in ("failure", "timed_out", "cancelled")), None)
    print()
    print(f"{job['name']} {job['conclusion']}" + (f" at its step {stopped['name']}" if stopped else ""))
    for note in api(f"repos/{repo}/check-runs/{job['id']}/annotations?per_page=100"):
        where = f"{note['path']}:{note['start_line']} " if note.get("path") and note["path"] != ".github" else ""
        print(f"  {note['annotation_level']} {where}{note['message'].splitlines()[0] if note['message'] else ''}")

    # Each log line begins with its time, so the step's lines are those within its start and end.
    # Where the step has no times, the log is read up to the first error that ended a step. The log
    # opens with a byte order mark, which would hide the first line's time, and the colors are taken
    # out so the file reads as text.
    log = COLOR.sub("", api(f"repos/{repo}/actions/jobs/{job['id']}/logs", text=True).lstrip("\ufeff")).splitlines()
    timed = [(line[:19], line[29:] if line[28:29] == " " else line) for line in log]
    kept = []
    if stopped and stopped.get("started_at") and stopped.get("completed_at"):
        start, end = second(stopped["started_at"]), second(stopped["completed_at"])
        inside = [i for i, (time, _) in enumerate(timed) if start <= time <= end]
        if inside:
            # A step's times are whole seconds, so the steps before and after it can share its first
            # and last second. Each step's lines begin with a header naming what it runs, so its own
            # header, the one bearing its name where one does, begins it and the next one ends it.
            first, last = inside[0], inside[-1]
            heads = [i for i in range(first, last + 1) if timed[i][1].startswith("##[group]Run ")]
            if heads:
                own = next((i for i in heads if timed[i][1] == "##[group]" + stopped["name"]), heads[0])
                first, last = own, next((i - 1 for i in heads if i > own), last)
            kept = [text for _, text in timed[first:last + 1]]
    if not kept:
        last = next((i for i, (_, text) in enumerate(timed) if text.startswith("##[error]Process completed")), len(timed) - 1)
        kept = [text for _, text in timed[:last + 1]]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{run}-{job['id']}.log")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(kept[-LINES:]) + "\n")
    print(f"  the step's last {min(LINES, len(kept))} lines are in {path}")
