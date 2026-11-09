using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Win32;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

[assembly: AssemblyTitle("CacheNorth Offline Intelligence")]
[assembly: AssemblyDescription("CacheNorth Offline Intelligence")]
[assembly: AssemblyCompany("Security With Sam")]
[assembly: AssemblyProduct("CacheNorth")]
[assembly: AssemblyCopyright("Copyright 2026 Security With Sam")]
[assembly: AssemblyVersion("1.0.1.0")]
[assembly: AssemblyFileVersion("1.0.1.0")]

internal static class LaunchCacheNorth
{
    private const string AppUserModelId = "SecurityWithSam.CacheNorth";
    [DllImport("shell32.dll", SetLastError = true)]
    private static extern int SetCurrentProcessExplicitAppUserModelID([MarshalAs(UnmanagedType.LPWStr)] string appID);

    [STAThread]
    private static int Main()
    {
        SetCurrentProcessExplicitAppUserModelID(AppUserModelId);
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        string root = CacheNorthPaths.ResolveRoot(AppDomain.CurrentDomain.BaseDirectory);
        string runtime = Path.Combine(root, "Apps", "Offline AI", "Runtime", "SecurityWithSamOfflineAI.exe");
        if (!Environment.Is64BitOperatingSystem) return Fail("CacheNorth requires 64-bit Windows 10 or Windows 11.", 2);
        if (Environment.OSVersion.Platform != PlatformID.Win32NT || GetWindowsBuild() < 10240) return Fail("CacheNorth requires Windows 10 or Windows 11.", 2);
        if (!File.Exists(runtime)) return Fail("The CacheNorth runtime is missing.\n\nExpected:\n" + runtime, 3);
        bool created;
        using (Mutex mutex = new Mutex(true, "CacheNorth_" + StableId(root), out created))
        {
            if (!created) return Fail("CacheNorth is already running from this drive.", 4);
            try { Application.Run(new CacheNorthWindow(root, runtime)); return 0; }
            catch (UnauthorizedAccessException) { return Fail("Windows blocked access to CacheNorth. Check file permissions and Windows Security, then try again.", 6); }
            catch (Exception ex) { return Fail("CacheNorth could not start.\n\n" + ex.Message, 7); }
        }
    }

    private static int Fail(string message, int code)
    {
        MessageBox.Show(message, "CacheNorth by Security With Sam", MessageBoxButtons.OK, MessageBoxIcon.Error);
        return code;
    }

    private static string StableId(string value)
    {
        using (SHA256 sha = SHA256.Create())
        {
            byte[] hash = sha.ComputeHash(Encoding.UTF8.GetBytes(value.ToUpperInvariant()));
            return BitConverter.ToString(hash, 0, 8).Replace("-", "");
        }
    }

    private static int GetWindowsBuild()
    {
        try
        {
            using (RegistryKey key = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion"))
            {
                object value = key == null ? null : key.GetValue("CurrentBuildNumber");
                int build;
                return value != null && Int32.TryParse(value.ToString(), out build) ? build : 0;
            }
        }
        catch { return 0; }
    }
}

internal static class CacheNorthPaths
{
    internal static string ResolveRoot(string baseDirectory)
    {
        if (String.IsNullOrWhiteSpace(baseDirectory))
            throw new ArgumentException("The CacheNorth base directory is unavailable.", "baseDirectory");

        return Path.GetFullPath(baseDirectory);
    }

    internal static string QuoteArgument(string value)
    {
        if (value == null) throw new ArgumentNullException("value");
        StringBuilder quoted = new StringBuilder(value.Length + 2);
        quoted.Append('"');
        int backslashes = 0;
        foreach (char character in value)
        {
            if (character == '\\')
            {
                backslashes++;
                continue;
            }

            if (character == '"')
            {
                quoted.Append('\\', backslashes * 2 + 1);
                quoted.Append('"');
            }
            else
            {
                quoted.Append('\\', backslashes);
                quoted.Append(character);
            }
            backslashes = 0;
        }
        quoted.Append('\\', backslashes * 2);
        quoted.Append('"');
        return quoted.ToString();
    }
}

internal sealed class CacheNorthWindow : Form
{
    private readonly string root;
    private readonly string runtime;
    private readonly string sessionFile;
    private readonly Label status;
    private readonly Panel splash;
    private readonly WebView2 webView;
    private readonly Button browserButton;
    private readonly LauncherLog log;
    private readonly CancellationTokenSource startupCancellation = new CancellationTokenSource();
    private Process backend;
    private string dashboardUrl;
    private bool closing;
    private int startupStarted;

    public CacheNorthWindow(string rootPath, string runtimePath)
    {
        root = rootPath;
        runtime = runtimePath;
        sessionFile = Path.Combine(root, "Apps", "Offline AI", "Data", "cache-north-session.json");
        log = new LauncherLog(root);
        log.Write("Launcher window constructed. Root=" + root + "; runtime=" + runtime);
        Text = "CacheNorth by Security With Sam";
        Width = 1440;
        Height = 900;
        MinimumSize = new Size(1060, 680);
        StartPosition = FormStartPosition.CenterScreen;
        BackColor = Color.FromArgb(5, 9, 14);
        Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
        webView = new WebView2 { Dock = DockStyle.Fill, Visible = false };
        Controls.Add(webView);
        splash = new Panel { Dock = DockStyle.Fill, BackColor = Color.FromArgb(5, 12, 20) };
        Controls.Add(splash);
        splash.BringToFront();

        TableLayoutPanel layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 7, Padding = new Padding(40), BackColor = Color.Transparent };
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        layout.RowStyles.Add(new RowStyle(SizeType.Percent, 35));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 132));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 54));
        layout.RowStyles.Add(new RowStyle(SizeType.Percent, 35));
        splash.Controls.Add(layout);

        PictureBox logo = new PictureBox { Width = 116, Height = 116, SizeMode = PictureBoxSizeMode.Zoom, Anchor = AnchorStyles.None };
        string logoPath = Path.Combine(root, "Apps", "Offline AI", "Dashboard", "cache-north-logo.png");
        if (File.Exists(logoPath)) logo.Image = Image.FromFile(logoPath);
        layout.Controls.Add(logo, 0, 1);
        layout.Controls.Add(MakeLabel("SECURITY WITH SAM", Color.FromArgb(69, 216, 255), new Font("Consolas", 10, FontStyle.Bold)), 0, 2);
        layout.Controls.Add(MakeLabel("CacheNorth", Color.White, new Font("Segoe UI Semibold", 28)), 0, 3);
        status = MakeLabel("Starting CacheNorth...", Color.FromArgb(169, 185, 200), new Font("Segoe UI", 11));
        layout.Controls.Add(status, 0, 4);
        browserButton = new Button { Text = "Open dashboard in browser", Width = 220, Height = 38, Anchor = AnchorStyles.None, Visible = false, FlatStyle = FlatStyle.Flat, BackColor = Color.FromArgb(8, 123, 164), ForeColor = Color.White };
        browserButton.FlatAppearance.BorderColor = Color.FromArgb(69, 216, 255);
        browserButton.Click += delegate { OpenBrowser(); };
        layout.Controls.Add(browserButton, 0, 5);
        FormClosing += OnClosing;
    }

    protected override void OnHandleCreated(EventArgs e)
    {
        base.OnHandleCreated(e);
        BeginInvoke((MethodInvoker)delegate { StartOnce(); });
    }

    private async void StartOnce()
    {
        if (Interlocked.CompareExchange(ref startupStarted, 1, 0) != 0)
        {
            log.Write("Duplicate startup request ignored.");
            return;
        }

        log.Write("Startup scheduled after window handle creation.");
        try
        {
            await StartAsync(startupCancellation.Token);
            log.Write("Startup completed successfully.");
        }
        catch (OperationCanceledException)
        {
            log.Write("Startup cancelled because the launcher is closing.");
        }
        catch (Exception ex)
        {
            log.Write("Startup failed: " + ex);
            if (!closing && !IsDisposed)
            {
                status.Text = "CacheNorth could not start. See Apps\\Offline AI\\Data\\Logs\\launcher.log for details.";
                MessageBox.Show(
                    ex.Message + "\n\nDiagnostic log:\n" + log.Path,
                    "CacheNorth startup error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }
    }

    private static Label MakeLabel(string text, Color color, Font font)
    {
        return new Label { Text = text, ForeColor = color, Font = font, TextAlign = ContentAlignment.MiddleCenter, Dock = DockStyle.Fill };
    }

    private async Task StartAsync(CancellationToken cancellationToken)
    {
        log.Write("Preparing writable data directory and session file.");
        Directory.CreateDirectory(Path.GetDirectoryName(sessionFile));
        if (File.Exists(sessionFile)) File.Delete(sessionFile);
        cancellationToken.ThrowIfCancellationRequested();
        status.Text = "Loading offline AI...";
        if (backend != null) throw new InvalidOperationException("The CacheNorth backend startup was already requested.");
        log.Write("Starting the managed backend process.");
        backend = Process.Start(new ProcessStartInfo
        {
            FileName = runtime,
            Arguments = "--headless --root " + CacheNorthPaths.QuoteArgument(root) + " --session-file " + CacheNorthPaths.QuoteArgument(sessionFile) + " --parent-pid " + Process.GetCurrentProcess().Id,
            WorkingDirectory = Path.GetDirectoryName(runtime),
            UseShellExecute = false,
            CreateNoWindow = true,
            WindowStyle = ProcessWindowStyle.Hidden,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        });
        if (backend == null) throw new InvalidOperationException("Windows could not start the CacheNorth backend.");
        backend.EnableRaisingEvents = true;
        backend.Exited += delegate
        {
            log.Write("Managed backend process exited.");
            if (!closing && IsHandleCreated && !IsDisposed)
            {
                try { BeginInvoke((MethodInvoker)delegate { if (!closing) Close(); }); } catch { }
            }
        };
        backend.OutputDataReceived += delegate(object sender, DataReceivedEventArgs e) { if (!String.IsNullOrEmpty(e.Data)) LogBackendLine("stdout", e.Data); };
        backend.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs e) { if (!String.IsNullOrEmpty(e.Data)) log.Write("Backend stderr: " + e.Data); };
        backend.BeginOutputReadLine();
        backend.BeginErrorReadLine();
        log.Write("Backend started. PID=" + backend.Id);
        status.Text = "Preparing your library...";
        DateTime deadline = DateTime.UtcNow.AddMinutes(4);
        while (!File.Exists(sessionFile) && DateTime.UtcNow < deadline)
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (backend.HasExited)
            {
                log.Write("Backend exited during startup. ExitCode=" + backend.ExitCode);
                throw new InvalidOperationException("The CacheNorth backend stopped during startup. Open Apps\\Offline AI\\Data\\Logs for details.");
            }
            await Task.Delay(200);
        }
        if (!File.Exists(sessionFile)) throw new TimeoutException("CacheNorth startup timed out. Check available memory and the diagnostic log.");
        cancellationToken.ThrowIfCancellationRequested();
        log.Write("Backend session file detected.");
        JavaScriptSerializer serializer = new JavaScriptSerializer();
        var session = serializer.Deserialize<System.Collections.Generic.Dictionary<string, object>>(File.ReadAllText(sessionFile));
        dashboardUrl = Convert.ToString(session["url"]);
        status.Text = "Ready";
        try
        {
            log.Write("Initializing the native WebView2 dashboard.");
            CoreWebView2Environment.GetAvailableBrowserVersionString();
            string userData = Path.Combine(root, "Apps", "Offline AI", "Data", "WebView2");
            CoreWebView2Environment environment = await CoreWebView2Environment.CreateAsync(null, userData);
            cancellationToken.ThrowIfCancellationRequested();
            await webView.EnsureCoreWebView2Async(environment);
            cancellationToken.ThrowIfCancellationRequested();
            ConfigureWebView();
            webView.Source = new Uri(dashboardUrl);
            webView.Visible = true;
            splash.Visible = false;
            webView.Focus();
            log.Write("Native WebView2 dashboard initialized.");
        }
        catch (WebView2RuntimeNotFoundException)
        {
            log.Write("WebView2 Runtime is unavailable; activating browser fallback.");
            status.Text = "Microsoft WebView2 is unavailable. CacheNorth can open in your default browser.";
            browserButton.Visible = true;
            OpenBrowser();
        }
        catch (Exception ex)
        {
            log.Write("WebView2 initialization failed; activating browser fallback. " + ex);
            status.Text = "The native dashboard could not start. CacheNorth can open in your default browser.";
            browserButton.Visible = true;
            OpenBrowser();
            MessageBox.Show(ex.Message, "CacheNorth browser fallback", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }

    private void ConfigureWebView()
    {
        string allowedOrigin = new Uri(dashboardUrl).GetLeftPart(UriPartial.Authority);
        webView.CoreWebView2.Settings.AreDevToolsEnabled = false;
        webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
        webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
        webView.CoreWebView2.NavigationStarting += delegate(object sender, CoreWebView2NavigationStartingEventArgs e)
        {
            Uri target;
            if (!Uri.TryCreate(e.Uri, UriKind.Absolute, out target) || target.GetLeftPart(UriPartial.Authority) != allowedOrigin) e.Cancel = true;
        };
        webView.CoreWebView2.NewWindowRequested += delegate(object sender, CoreWebView2NewWindowRequestedEventArgs e) { e.Handled = true; };
        webView.CoreWebView2.PermissionRequested += delegate(object sender, CoreWebView2PermissionRequestedEventArgs e) { e.State = CoreWebView2PermissionState.Deny; };
        webView.CoreWebView2.DownloadStarting += delegate(object sender, CoreWebView2DownloadStartingEventArgs e) { e.Cancel = true; };
        webView.CoreWebView2.WebMessageReceived += delegate(object sender, CoreWebView2WebMessageReceivedEventArgs e)
        {
            string message = null;
            try { message = e.TryGetWebMessageAsString(); } catch { }
            if (message == "cache-north-close")
            {
                log.Write("Dashboard requested native launcher shutdown.");
                BeginInvoke((MethodInvoker)delegate { Close(); });
            }
        };
    }

    private void OpenBrowser()
    {
        if (!String.IsNullOrEmpty(dashboardUrl)) Process.Start(new ProcessStartInfo { FileName = dashboardUrl, UseShellExecute = true });
    }

    private void LogBackendLine(string stream, string line)
    {
        int token = line.IndexOf("#token=", StringComparison.OrdinalIgnoreCase);
        if (token >= 0) line = line.Substring(0, token) + "#token=[redacted]";
        log.Write("Backend " + stream + ": " + line);
    }

    private void OnClosing(object sender, FormClosingEventArgs e)
    {
        if (closing) return;
        closing = true;
        startupCancellation.Cancel();
        log.Write("Launcher close requested; stopping managed processes.");
        try
        {
            if (!String.IsNullOrEmpty(dashboardUrl))
            {
                Uri uri = new Uri(dashboardUrl);
                string token = uri.Fragment.StartsWith("#token=") ? Uri.UnescapeDataString(uri.Fragment.Substring(7)) : "";
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(uri.GetLeftPart(UriPartial.Authority) + "/api/shutdown");
                request.Method = "POST";
                request.Headers["X-SWS-Token"] = token;
                request.Timeout = 2500;
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse()) { }
            }
        }
        catch { }
        try { if (backend != null && !backend.HasExited && !backend.WaitForExit(8000)) backend.Kill(); } catch { }
        try
        {
            if (File.Exists(sessionFile))
            {
                File.Delete(sessionFile);
                log.Write("Stale launcher session file removed.");
            }
        }
        catch (Exception ex) { log.Write("Could not remove the launcher session file: " + ex.Message); }
        log.Write("Launcher shutdown sequence completed.");
    }
}

internal sealed class LauncherLog
{
    private readonly object sync = new object();
    internal string Path { get; private set; }

    internal LauncherLog(string root)
    {
        string preferred = System.IO.Path.Combine(root, "Apps", "Offline AI", "Data", "Logs", "launcher.log");
        string fallback = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "CacheNorth", "launcher.log");
        Path = Prepare(preferred) ? preferred : fallback;
        Prepare(Path);
    }

    private static bool Prepare(string path)
    {
        try
        {
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path));
            return true;
        }
        catch
        {
            return false;
        }
    }

    internal void Write(string message)
    {
        try
        {
            lock (sync)
            {
                File.AppendAllText(Path, DateTimeOffset.Now.ToString("o") + " [PID " + Process.GetCurrentProcess().Id + "] " + message + Environment.NewLine);
            }
        }
        catch { }
    }
}
