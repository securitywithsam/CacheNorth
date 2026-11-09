using System;
using System.IO;

internal static class LauncherPathResolutionTests
{
    private static int failures;

    private static void Equal(string expected, string actual, string name)
    {
        if (!String.Equals(expected, actual, StringComparison.OrdinalIgnoreCase))
        {
            Console.Error.WriteLine("FAIL " + name + ": expected '" + expected + "', received '" + actual + "'.");
            failures++;
        }
        else
        {
            Console.WriteLine("PASS " + name + ": " + actual);
        }
    }

    private static void True(bool value, string name)
    {
        if (!value)
        {
            Console.Error.WriteLine("FAIL " + name);
            failures++;
        }
        else
        {
            Console.WriteLine("PASS " + name);
        }
    }

    private static int Main()
    {
        Equal(@"D:\", CacheNorthPaths.ResolveRoot(@"D:\"), "D drive root");
        Equal(@"E:\", CacheNorthPaths.ResolveRoot(@"E:\"), "different drive root");

        string spaced = Path.Combine(Path.GetTempPath(), "CacheNorth path with spaces") + Path.DirectorySeparatorChar;
        Equal(Path.GetFullPath(spaced), CacheNorthPaths.ResolveRoot(spaced), "path containing spaces");

        string originalDirectory = Environment.CurrentDirectory;
        string basePath = Path.Combine(Path.GetTempPath(), "CacheNorth fixed base") + Path.DirectorySeparatorChar;
        try
        {
            Environment.CurrentDirectory = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
            Equal(Path.GetFullPath(basePath), CacheNorthPaths.ResolveRoot(basePath), "independent of working directory");
        }
        finally
        {
            Environment.CurrentDirectory = originalDirectory;
        }

        string runtime = Path.Combine(CacheNorthPaths.ResolveRoot(@"D:\"), "Apps", "Offline AI", "Runtime", "SecurityWithSamOfflineAI.exe");
        Equal(@"D:\Apps\Offline AI\Runtime\SecurityWithSamOfflineAI.exe", runtime, "USB-root runtime path");
        True(Path.IsPathRooted(runtime), "runtime path remains rooted");
        Equal("\"D:\\\\\"", CacheNorthPaths.QuoteArgument(@"D:\"), "drive-root command-line quoting");
        Equal("\"C:\\CacheNorth Stage\\session file.json\"", CacheNorthPaths.QuoteArgument(@"C:\CacheNorth Stage\session file.json"), "space-containing command-line quoting");

        Console.WriteLine(failures == 0 ? "All launcher path regression tests passed." : failures + " launcher path regression test(s) failed.");
        return failures == 0 ? 0 : 1;
    }
}
