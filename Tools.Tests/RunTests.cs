using System.Text.Json;
using Xunit;

namespace Tools.Tests;

public class RunTests
{
    [NeedsPythonFact]
    public void A_Failed_Job_Gives_Its_Annotations_And_Its_Steps_Last_Lines_In_A_File()
    {
        var folder = Directory.CreateTempSubdirectory("run-").FullName;
        try
        {
            // A run of two jobs as GitHub's API answers, the play job failing at its second step,
            // whose 100 lines lie between the set-up's and the next step's in the job's log.
            var log = new List<string> { "﻿2026-10-31T12:00:00.1000000Z set up 0" };
            for (int i = 1; i < 20; i++) log.Add($"2026-10-31T12:00:0{i % 2}.1000000Z set up {i}");
            log.Add("2026-10-31T12:01:00.0000000Z ##[group]Run build/play.sh");
            for (int i = 0; i < 100; i++) log.Add($"2026-10-31T12:01:{i % 60:00}.5000000Z play {i}");
            log.Add("2026-10-31T12:02:00.0000000Z ##[error]Process completed with exit code 1.");
            // The next step begins in the second the failing one ends, as GitHub's whole-second times
            // often have it, and its header is no line of the failing step's.
            log.Add("2026-10-31T12:02:00.5000000Z ##[group]Run actions/upload-artifact@v7");
            log.Add("2026-10-31T12:02:00.5000000Z ##[endgroup]");
            for (int i = 0; i < 10; i++) log.Add($"2026-10-31T12:02:05.0000000Z clean up {i}");
            var answers = new Dictionary<string, object>
            {
                ["repos/EggyStudio/Sample/actions/runs/7"] = new { name = "build", head_sha = "abc1234def", status = "completed", conclusion = "failure" },
                ["repos/EggyStudio/Sample/actions/runs/7/jobs?per_page=100&page=1"] = new
                {
                    total_count = 2,
                    jobs = new object[]
                    {
                        new { id = 11, name = "test (ubuntu-24.04)", status = "completed", conclusion = "success", started_at = "2026-10-31T11:58:00Z", completed_at = "2026-10-31T11:59:05Z" },
                        new
                        {
                            id = 12, name = "play", status = "completed", conclusion = "failure", started_at = "2026-10-31T12:00:00Z", completed_at = "2026-10-31T12:02:06Z",
                            steps = new object[]
                            {
                                new { name = "Set up job", conclusion = "success", started_at = "2026-10-31T12:00:00.000Z", completed_at = "2026-10-31T12:00:01.000Z" },
                                new { name = "Run build/play.sh", conclusion = "failure", started_at = "2026-10-31T12:01:00.000Z", completed_at = "2026-10-31T12:02:00.000Z" },
                                new { name = "Run actions/upload-artifact@v7", conclusion = "success", started_at = "2026-10-31T12:02:00.000Z", completed_at = "2026-10-31T12:02:06.000Z" },
                            },
                        },
                    },
                },
                ["repos/EggyStudio/Sample/check-runs/12/annotations?per_page=100"] = new object[]
                {
                    new { path = "build/play.sh", start_line = 12, annotation_level = "failure", message = "The seed's field took no text.\nmore" },
                },
                ["repos/EggyStudio/Sample/actions/jobs/12/logs"] = string.Join("\n", log) + "\n",
            };
            var recorded = Path.Combine(folder, "answers.json");
            File.WriteAllText(recorded, JsonSerializer.Serialize(answers));
            var logs = Path.Combine(folder, "logs");

            var printed = Programs.Script("run.py", new Dictionary<string, string> { ["RUN_ANSWERS"] = recorded }, "EggyStudio/Sample", "7", logs);

            Assert.Contains("run 7, build at abc1234, completed failure", printed);
            Assert.Contains("test (ubuntu-24.04)  success     1 min 5 s", printed);
            Assert.Contains("play failure at its step Run build/play.sh", printed);
            Assert.Contains("failure build/play.sh:12 The seed's field took no text.", printed);
            var file = Path.Combine(logs, "7-12.log");
            Assert.Contains($"the step's last 60 lines are in {file}", printed);
            Assert.DoesNotContain("play 99", printed);

            var lines = File.ReadAllLines(file);
            Assert.Equal(60, lines.Length);
            Assert.Equal("play 41", lines[0]);
            Assert.Equal("##[error]Process completed with exit code 1.", lines[^1]);
        }
        finally
        {
            Directory.Delete(folder, true);
        }
    }
}
