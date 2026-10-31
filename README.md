# Tools

Tools is a library both engines, 3DEngine and BevyCSharp, take as a git submodule, for what the
repositories otherwise copy by hand, the devlog's generator, the composer of reading sheets, the run
reader, the texture recipes, and the text STYLE.md, COMMITS.md and NORM.md share. It references no
engine, and each engine implements the interfaces it declares where it binds the module.

## Taking it into an engine

An engine adds the repository as a git submodule under `modules/` and references its project, here
from a project one folder below the engine's root.

```bash
git submodule add https://github.com/EggyStudio/Tools.git modules/Tools
```

```xml
<ProjectReference Include="..\modules\Tools\Tools\Tools.csproj" />
```

A clone of the engine fetches the module with `git clone --recurse-submodules`, or with
`git submodule update --init` in a clone made without it, and a workflow checks it out with
`submodules: true` on `actions/checkout`. A change the engine uses is committed and pushed here
before the engine's commit that moves its pointer, so the engine's history never names a commit
this repository does not have.

## The devlog

`scripts/devlog.py` writes a repository's `DEVLOG.md`, what landed by day and newest first. It
takes the pictures under `.github/devlog` or `.github/assets/readings` with their captions and the
notes beside them, the captures under `.github/assets`, and the items of `.github/REVIEW.md` and
`.github/REVIEW-ARCHIVE.md` marked done, each on the day of the commit that closed it. A repository
runs it with its path and its name, and with a list of the pictures sent on the way where it keeps
one, which needs Pillow to save them as WebP.

```bash
python3 -I scripts/devlog.py <repo path> <Name> [sent-pictures.json]
```

It prints the days, pictures and items it wrote, and any line that breaks STYLE.md's mechanical
rules.

## Building and testing

With the .NET 10 SDK:

```bash
dotnet build Tools.slnx
dotnet test Tools.Tests
```

## License

The Mozilla Public License 2.0, in [LICENSE](LICENSE).
