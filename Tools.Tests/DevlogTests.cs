using Xunit;

namespace Tools.Tests;

public class DevlogTests
{
    [NeedsPythonFact]
    public void A_Done_Item_Of_The_Review_Is_Listed_On_The_Day_Of_Its_Commit()
    {
        var repo = Directory.CreateTempSubdirectory("devlog-").FullName;
        try
        {
            // A repository of one commit, which the review's one item names as the commit that closed it.
            Git(repo, "init", "-q");
            File.WriteAllText(Path.Combine(repo, "README.md"), "# Sample\n");
            Git(repo, "add", "-A");
            Git(repo, "commit", "-q", "-m", "The first commit.");
            var hash = Git(repo, "rev-parse", "--short=7", "HEAD").Trim();
            var date = Git(repo, "log", "-1", "--format=%cs").Trim();
            Directory.CreateDirectory(Path.Combine(repo, ".github"));
            File.WriteAllText(Path.Combine(repo, ".github", "REVIEW.md"),
                $"# Review\n\n## Now\n\n1. **The first item.** Done at `{hash}`.\n\n## Verdicts\n\nNone yet.\n");

            Programs.Script("devlog.py", repo, "Sample");

            var devlog = File.ReadAllLines(Path.Combine(repo, "DEVLOG.md"));
            Assert.Equal("# Sample devlog", devlog[0]);
            var day = Array.IndexOf(devlog, $"## {date}");
            Assert.True(day > 0, $"no heading for {date}");
            Assert.Equal("Done that day", devlog[day + 2]);
            Assert.Equal($"- Item 1 at `{hash}`. The first item.", devlog[day + 4]);
        }
        finally
        {
            // Git writes its objects read-only, which Windows will not delete as they are.
            foreach (var file in Directory.EnumerateFiles(repo, "*", SearchOption.AllDirectories)) File.SetAttributes(file, FileAttributes.Normal);
            Directory.Delete(repo, true);
        }
    }

    // The machine's own settings left out, an identity given and signing off, so a commit is made
    // alike on a runner with no identity and on a desktop that signs.
    private static string Git(string repo, params string[] arguments) =>
        Programs.Run("git", repo, ["-c", "user.name=Tools", "-c", "user.email=tools@example.com", "-c", "commit.gpgsign=false", .. arguments]);
}
