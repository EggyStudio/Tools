using System.ComponentModel;
using System.Diagnostics;
using Xunit;

namespace Tools.Tests;

/// <summary>Skipped where no Python 3 runs, so a run's summary says the script's tests did not run.</summary>
public sealed class NeedsPythonFactAttribute : FactAttribute
{
    public NeedsPythonFactAttribute()
    {
        if (Programs.Python.Value is null) Skip = "No Python 3 runs here as python3 or python.";
    }
}

/// <summary>Runs the module's scripts and the programs they call.</summary>
public static class Programs
{
    /// <summary>
    /// The command that runs Python 3, <c>python3</c> as Linux and macOS name it, or <c>python</c>
    /// as Windows does, or null where neither runs.
    /// </summary>
    public static readonly Lazy<string?> Python = new(() => new[] { "python3", "python" }.FirstOrDefault(Runs));

    /// <summary>Runs a script copied beside the tests with Python's isolated mode, as a repository runs it, and returns what it printed.</summary>
    public static string Script(string name, params string[] arguments) => Script(name, [], arguments);

    /// <summary>Runs a script as <see cref="Script(string, string[])"/> does, with variables set in its environment.</summary>
    public static string Script(string name, Dictionary<string, string> environment, params string[] arguments) =>
        Run(Python.Value!, AppContext.BaseDirectory, environment, ["-I", Path.Combine(AppContext.BaseDirectory, "scripts", name), .. arguments]);

    /// <summary>Runs a program in a folder and returns what it printed, failing the test where it exits with an error.</summary>
    public static string Run(string program, string folder, params string[] arguments) => Run(program, folder, [], arguments);

    private static string Run(string program, string folder, Dictionary<string, string> environment, string[] arguments)
    {
        var start = new ProcessStartInfo(program) { WorkingDirectory = folder, RedirectStandardOutput = true, RedirectStandardError = true };
        foreach (var argument in arguments) start.ArgumentList.Add(argument);
        foreach (var (key, value) in environment) start.Environment[key] = value;
        using var process = Process.Start(start)!;
        var error = process.StandardError.ReadToEndAsync();
        var output = process.StandardOutput.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, $"{program} {string.Join(' ', arguments)} exited with {process.ExitCode}. {error.Result}");
        return output;
    }

    // Windows names a Store installer python3 where no Python is installed, which prints where to get
    // one and exits with an error, so the version it prints is read rather than its being found.
    private static bool Runs(string command)
    {
        try
        {
            var start = new ProcessStartInfo(command, "--version") { RedirectStandardOutput = true, RedirectStandardError = true };
            using var process = Process.Start(start)!;
            var printed = process.StandardOutput.ReadToEnd() + process.StandardError.ReadToEnd();
            process.WaitForExit();
            return process.ExitCode == 0 && printed.StartsWith("Python 3", StringComparison.Ordinal);
        }
        catch (Win32Exception)
        {
            return false;
        }
    }
}
