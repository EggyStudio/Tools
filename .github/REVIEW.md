# Review

Reviewed up to `13c8202`, item 2, pushed at 12:31 on 2026-10-31 with `e28b3b4`, item 1, after the
owner's first commit, its run green at 12:32, the first of this repository. After it `7532128`, item
3's first part, the devlog generator, pushed at 12:35, its run green at 12:35 as well;
scripts/devlog.py as the reviewing session's byte for byte, the README saying how a repository runs
it, DevlogTests making a one-commit scratch repository with git's identity given on the command line
and reading the Done line the script writes, Python found as python3 or python and the test skipped
with its reason where neither runs; 2 of 2 tests, the strict build clean. After it `321de49`, item
3's second part, the run reader, pushed at 12:38, its run green at 12:41; scripts/run.py prints a
run's jobs with their conclusions and times and, for a job that failed, timed out or was cancelled,
the step it stopped at and the check run's annotations, writing the step's last 60 lines to a file
under the folder given and printing the path, no log text reaching the terminal; the step is bounded
by its own group header and the next, since steps carry whole-second times and the first version
took the next step's header in; gh's escape flag added only where gh asks; the test reads recorded
answers keyed by API path, so it skips only where Python is missing; 3 of 3 tests, the strict build
clean. Both commits keep the form, the three-mark subject, one sentence, the owner's identity as
author and committer, no trailer (N 7.2 and N 7.6 kept at the first commit); the library references
no engine (N 2.1). The documents are the engines' with the engine's name replaced and the
engine-only lines dropped, COMMITS.md the game's with N 7.1's pointer rule in place of the legacy
branch line, .gitignore with the dump folder, .claude and .ref; AGENTS.md's devlog row carries no
link until DEVLOG.md exists and its table of areas gains the rows item 2 adds. The skeleton sets
ImportDirectoryBuildTargets false, since a submodule under modules/ would inherit an engine's
Directory.Build.targets, makes a missing summary an error, loads the assembly by name in its one
test, and build/version.sh prints 0.1.0; the strict build 0 warnings and 0 errors, the test passing.
After it `1c0015a`, the norm alone, the seven repositories named, pushed at 14:51 on 2026-11-03,
with no run since the build passes over the review's files; it keeps the form. Before it `2340033`,
the owner's first commit alone.

## Now

The order the owner set on 2026-10-31 for the six modules, this one holding the scripts and the
documents' sources the repositories duplicate by hand, the devlog generator, the sheet composer of
3DEngine's item 136, the run reader, the texture recipes of `build/textures.py`, and STYLE.md,
COMMITS.md and the common rules of NORM.md. The documents first, then the rest as the other projects
have it, then the engines taking the module. Items 1 and 2 are the game's session's, being free
while the game waits on the engine's package; item 3 is the session's that owns the code today; item
4 is each engine's session's. Among the six this module comes first, since it needs no engine code
and every repository gains from it at once.

1. **The documents, one commit.** AGENTS.md on the game's shape (one paragraph saying what the
    module is and that no engine is referenced, N 2.1; the documents table with STYLE, COMMITS,
    REVIEW, NORM and DEVLOG; building and testing; Where things are with a row a folder; the
    conventions, the commit form among them), README.md (what the module is, how an engine takes it
    as a submodule, `dotnet build` and `dotnet test`), `.github/STYLE.md`, `COMMITS.md` and
    `CODE_OF_CONDUCT.md` as the engines' with the engine's name replaced, `.gitignore` of the
    engines' shape with `/.github/dump/` in it, `.gitattributes`. The game's AGENTS.md and the
    engines' documents are the models; nothing is written that the module does not have yet. This
    commit is the first test of the commit form here, N 7.2 and N 7.6, read by the reviewing session
    before it is pushed. Done at `e28b3b4`.

2. **The skeleton, one commit after item 1.** `Tools.slnx`, `Tools/Tools.csproj` as a class library
    on net10.0 with `Nullable` and `ImplicitUsings` in `Directory.Build.props`, `Tools.Tests/` on
    xunit with one test that the library loads, `build/version.txt` at `0.1` and `build/version.sh`
    as the engines', and `.github/workflows/build.yml` on a push, `test (os)` on ubuntu-24.04,
    windows-latest and macos-15 with `dotnet build Tools.slnx -warnaserror` and `dotnet test
    Tools.Tests --no-build`, a time limit on every job with its reason, `permissions` read and the
    engines' concurrency group. Green on the three systems before item 3. Done at `13c8202`.

3. **The code's move.** The source is the reviewing session's devlog.py and run reader, the engine
    sessions' scripts, and the documents as they stand in the engines; each repository then carries
    a copy its build checks against the source. One commit a part, the tests coming with the code,
    the strict build and the suite green, a Shared line in the engines' REVIEW.md when a part lands.
    Items written by the reviewing session when item 2 is green and the owning session is free.
    First part done at `7532128`, the devlog generator with its test; Second part done at `321de49`,
    the run reader; the sheet composer is the part left, from 3DEngine's session.

4. **The engines take the module.** Each engine adds this repository as a git submodule under
`modules/` and references its project, its workflows checking submodules out, its own folder for
this code becoming the binding of the module's interfaces (N 2.1) and the rest deleted; a change
used by an engine is committed here first and pushed before the engine's commit that moves the
pointer. One commit an engine, after item 3's first part.

## Verdicts

None yet.

## Decisions

1. **The repository's birth.** The owner made this repository on 2026-10-31 at 12:08 among six,
Modeling, Vegetation, Levels, Landscape, RadianceCascades beside it, after the ideas recorded as
3DEngine's Decision 78 and BevyCSharp's Decision 71, to hold the scripts and the documents' sources
the repositories duplicate by hand, the devlog generator, the sheet composer of 3DEngine's item 136,
the run reader, the texture recipes of `build/textures.py`, and STYLE.md, COMMITS.md and the common
rules of NORM.md as one library both engines use rather than one implementation an engine. The owner
set the order the same day, the documents first, then the rest as the other projects have it, then
the engines taking the module, and said the modules may be tried at once beside the engine's global
illumination work (3DEngine Decision 79).

2. **A git submodule, not a package.** The owner chose on 2026-10-31 that the engines take the
module as a git submodule built as a project of their own, since a package's upload, wait, test and
pack is slower to iterate than a commit. A change is committed here first; the reviewing session
pushes this repository before the engine's commit that moves its pointer; the workflows check
submodules out. The game keeps using the engine through the engine's package.

3. **The module knows no engine.** N 2.1. The module references no engine, package or bridge; what
it needs of a renderer, a world, a scheduler or a file system it takes through interfaces it
declares, which each engine implements where it binds the module. A type of an engine's in this
repository is a fault.

4. **The repository's terms are the owner's.** The repository was made by the owner with its terms
   file in place, which stands as the owner set it and is spoken of nowhere else.

5. **Who writes here.** The game's session writes items 1 and 2 for the six modules, being free
while the game waits on the engine's package; the session that owns the code today moves it (item
3), BevyCSharp's for Vegetation and Levels, 3DEngine's for Modeling and the cascades, the reviewing
session's scripts going into Tools; each engine's session binds the module (item 4). Every session
reads REVIEW.md's head, its items and the Replies before a batch, as N 7.7 says, and the reviewing
session pushes.

## Replies
