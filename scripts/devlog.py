import subprocess, re, json, sys, os, textwrap
repo, name, sent_json = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else None)
PIC_DIRS = [d for d in (".github/devlog", ".github/assets/readings") if os.path.isdir(os.path.join(repo, d))]
pic_dir = os.path.join(repo, PIC_DIRS[0]) if PIC_DIRS else os.path.join(repo, ".github", "devlog")
def git(*a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
fl = lambda s: " ".join(l.strip() for l in s.split("\n"))
BAD = re.compile(r"—|–|\bjust\b|\bsimply\b|\bwants?\b| now |\bnow\.|\bowner\b|[a-z\)`]: [a-z]" + (r"|\bdriv(e|en|es|ing)\b|glowing|gives? off" if name == "Voxel-Sandbox" else ""))
FIX = [(r", Blockout unless the owner names it otherwise", ", Blockout"), (r"the radiance cascades' faults the owner sees in the voxel game", "the radiance cascades' faults seen in the voxel game"),
 (r"What the owner saw on 2026-10-10 \(Decision 27\), before item 3's remainder\.", "Four things seen in the voxel game on 2026-10-10 (Decision 27), before item 3's remainder."),
 (r"compared for the owner's choice", "compared for the choice"), (r"the modpack's shader settings the owner set", "the modpack's shader settings as chosen"),
 (r"they are boards now\.", "they became boards after."), (r"Glass under Bare Bones now: the streaks are gone and panes", "Glass under Bare Bones, the streaks gone, where panes"),
 (r" Which saturation do you want\?$", ""), (r", not committed yet", ""), (r"colour", "color"), (r"for want of", "lacking"), (r", for the owner to choose\.", ", the choice open."), (r"the shadow now the ground darker", "the shadow then the ground darker"), (r"whose arrows, now entities", "whose arrows, since then entities"), (r"as raylib's does now\.", "as raylib's does."), (r"so the march now runs only by", "so the march runs only by"), (r"are drawn now that the bridge builds them", "are drawn since the bridge builds them"), (r"by the reviewer's call, open to\s+the owner's word, since", "by the reviewer's call, since"), (r"The README's words under the header are the owner's\.", "The README's words under the header, as given.")]
def fix(s):
    for a, b in FIX: s = re.sub(a, b, s)
    return s
days = {}  # date -> {"pictures": [(sortkey, path, caption, hash)], "done": [(num, hash, title)]}
def day(d): return days.setdefault(d, {"pictures": [], "notes": [], "done": []})
in_pic_dir = lambda rel: any(rel.startswith(d + "/") for d in PIC_DIRS)
# captions the sessions wrote, a line a file, the file's name then a bar then one sentence
captions = {}
for d in PIC_DIRS:
    cm = os.path.join(repo, d, "captions.md")
    if os.path.exists(cm):
        for line in open(cm):
            if " | " in line:
                f, c = line.split(" | ", 1); captions[d + "/" + f.strip()] = fix(c.strip())
# pictures sent on the way; those outside the repository are saved under the pictures folder as WebP
if sent_json:
    from PIL import Image
    os.makedirs(pic_dir, exist_ok=True)
    for r in json.load(open(sent_json)):
        d = r["ts"][:10] or "2026-10-20"; cap = fix(r["caption"])
        for src in r["files"]:
            if not os.path.exists(src): continue
            if os.path.abspath(src).startswith(os.path.abspath(repo) + os.sep):
                captions.setdefault(os.path.relpath(src, repo), cap); cap = ""; continue
            base = os.path.splitext(os.path.basename(src))[0].replace("_", "-"); dst = f"{d}-{base}.webp"
            if not os.path.exists(os.path.join(pic_dir, dst)):
                im = Image.open(src); im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                small = src.endswith(".png") and os.path.getsize(src) < 200_000 and im.size[0] <= 800
                im.save(os.path.join(pic_dir, dst), "WEBP", lossless=small, quality=85, method=6)
            captions.setdefault(os.path.relpath(pic_dir, repo) + "/" + dst, cap); cap = ""
# the pictures folders, each picture on the day its name says, captioned by the sessions' line or its commit's sentence
for d in PIC_DIRS:
    for f in sorted(os.listdir(os.path.join(repo, d))):
        if not f.endswith(".webp"): continue
        rel = d + "/" + f; m = re.match(r"(\d{4}-\d{2}-\d{2})", f)
        added = git("log", "--diff-filter=A", "-1", "--format=%cs|%ct|%h", "--", rel).strip().split("|")
        date = m.group(1) if m else (added[0] if added[0] else None)
        if not date: continue
        cap = captions.get(rel); h = None
        if cap is None and len(added) == 3: cap, h = fix(fl(git("log", "-1", "--format=%b", added[2])).strip()), added[2]
        when = int(added[1]) if len(added) == 3 else 1 << 40
        day(date)["pictures"].append(((0, when, f), rel, cap or "", h))
# notes the sessions wrote for the devlog, a Markdown file a note beside the pictures, named by the day and the item
for d in PIC_DIRS:
    for f in sorted(os.listdir(os.path.join(repo, d))):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-.*\.md$", f)
        if not m or f in ("captions.md", "README.md"): continue
        text = open(os.path.join(repo, d, f)).read().strip("\n")
        if text: day(m.group(1))["notes"].append((f, fix(text)))
# committed captures elsewhere under .github/assets, by the commit that added them
log = git("log", "--reverse", "--diff-filter=A", "--format=@@%cs|%h", "--name-only", "--", ".github/assets/*.webp", ".github/assets/*/*.webp", ".github/assets/*/*/*.webp")
cur = None; order = 0
for line in log.split("\n"):
    if line.startswith("@@"): cur = line[2:].split("|"); order += 1; continue
    if not line.strip() or cur is None or "/gallery/" in line or not line.endswith(".webp") or in_pic_dir(line): continue
    if not os.path.exists(os.path.join(repo, line)): continue
    body = fix(fl(git("log", "-1", "--format=%b", cur[1])).strip())
    day(cur[0])["pictures"].append(((1, order, line), line, body, cur[1]))
# the items done, from the archive and the current review
paras = []
for f in ("REVIEW-ARCHIVE.md", "REVIEW.md"):
    p = os.path.join(repo, ".github", f)
    if os.path.exists(p):
        t = open(p).read(); sec = t.split("## Verdicts")[0] if f == "REVIEW.md" else t.split("## Verdicts settled")[0]
        paras += [(f, q) for q in sec.split("\n\n") if re.match(r"\d+\. \*\*", q)]
seen = set()
for f, q in paras:
    s = fl(q); m = re.match(r"(\d+)\. \*\*(.+?)\*\*", s); num, title = int(m.group(1)), m.group(2)
    if num in seen: continue
    if f == "REVIEW.md" and not re.search(r"[Dd]one at `|item \d+ done|; done\b", s): continue
    hashes = re.findall(r"(?:Done at|Done again at|On main as|Capture done at|done at) `([0-9a-f]{7,8})`", s) or re.findall(r"`([0-9a-f]{7,8})`", s)
    date = None; h = None
    for cand in reversed(hashes):
        d = git("log", "-1", "--format=%cs", cand).strip()
        if d: date, h = d, cand; break
    if not date: continue
    seen.add(num)
    title = re.sub(r",? done at `[0-9a-f]+`[^.]*", "", title).strip()
    title = fix(title).replace(": ", ", ").rstrip(";., ") + "."
    day(date)["done"].append((num, h, title))
# write
folder = ", ".join(f"`{d}`" for d in PIC_DIRS)
intro = (f"What landed in {name}, by day and newest first, with the pictures taken on the way, the captures the repository "
 "keeps under `.github/assets`" + (f" and the pictures made while an item was built, kept under {folder} as WebP files named by their day, each on the day its name says, and the notes written beside them as Markdown files named the same way" if PIC_DIRS else "")
 + ". A line under Done names the item of .github/REVIEW.md or .github/REVIEW-ARCHIVE.md and the commit that closed it.")
lines = [f"# {name} devlog", ""] + textwrap.wrap(intro, 100, break_on_hyphens=False) + [""]
for d in sorted(days, reverse=True):
    e = days[d]
    if not e["pictures"] and not e["done"] and not e["notes"]: continue
    lines += [f"## {d}", ""]
    groups = []
    for key, path, cap, h in sorted(e["pictures"], key=lambda r: r[0]):
        if groups and h is not None and groups[-1][2] == h and groups[-1][1] == cap: groups[-1][0].append(path)
        else: groups.append(([path], cap, h))
    for paths, cap, h in groups:
        for path in paths: lines.append(f"![]({path})")
        if cap: lines += textwrap.wrap(cap + (f" (`{h}`)" if h else ""), 100)
        lines.append("")
    for f, text in sorted(e["notes"]):
        lines += text.split("\n") + [""]
    if e["done"]:
        lines.append("Done that day"); lines.append("")
        for num, h, title in sorted(e["done"]):
            lines += textwrap.wrap(f"- Item {num} at `{h}`. {title}", 100, subsequent_indent="  ")
        lines.append("")
text = "\n".join(lines).rstrip("\n") + "\n"
open(os.path.join(repo, "DEVLOG.md"), "w").write(text)
bad = [l for l in text.split("\n") if BAD.search(l) and not l.startswith("![")]
print(name, "days", len([d for d in days if days[d]["pictures"] or days[d]["done"]]), "pictures", sum(len(e["pictures"]) for e in days.values()), "done", sum(len(e["done"]) for e in days.values()), "bad lines", len(bad))
for l in bad[:12]: print("  BAD:", l[:140])
