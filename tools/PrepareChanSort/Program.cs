// Bereitet einen ChanSort-Klon fuer WebAssembly vor. Das Programm ist idempotent:
// Mehrfaches Ausfuehren schadet nicht, bereits gepatchte Stellen werden uebersprungen.
//
// Was geaendert wird:
//  1. Zielframework net48 -> modernes .NET (Standard: net10.0)
//  2. Neue Datei ChanSort.Api/Utils/WasmCompat.cs
//  3. "Assembly.Location" (im Browser leer) -> WasmCompat.Location(...), damit die .ini-Dateien gefunden werden
//  4. LG: Die optionale Windows-Oberflaeche (ChanSort.Loader.LG.UI) wird nicht mehr zwingend geladen
//
// Auf dem Desktop verhaelt sich ChanSort nach dem Patch exakt wie vorher, die Aenderungen
// koennten also auch als Pull-Request an das Originalprojekt gehen.

using System.Text;
using System.Text.RegularExpressions;

var root = args.Length > 0 ? args[0] : "chansort";
var tfm = args.Length > 1 ? args[1] : "net10.0";
var src = Path.Combine(root, "source");

// Unsichtbare Zeichen entfernen, die beim Kopieren von Befehlen aus Webseiten/Chats mitkommen koennen
root = new string(root.Where(c => c < 128 && !char.IsControl(c)).ToArray()).Trim();
tfm = new string(tfm.Where(c => c < 128 && !char.IsWhiteSpace(c) && !char.IsControl(c)).ToArray());
src = Path.Combine(root, "source");
if (!Regex.IsMatch(tfm, @"^net\d+\.\d+$"))
{
  Console.Error.WriteLine($"FEHLER: '{tfm}' ist kein gueltiges Zielframework. Beispiel: net10.0");
  return 1;
}

if (!File.Exists(Path.Combine(src, "Solution.props")))
{
  Console.Error.WriteLine($"FEHLER: In '{Path.GetFullPath(root)}' wurde kein ChanSort-Klon gefunden (source/Solution.props fehlt).");
  Console.Error.WriteLine("Bitte zuerst ausfuehren:  git clone https://github.com/PredatH0r/ChanSort.git chansort");
  return 1;
}

int changedFiles = 0;

// 1. Zielframework, dazu die Hilfspakete fuer das alte .NET Framework entfernen (unter .NET 10 nur Warnungen NU1510)
Patch(Path.Combine(src, "Solution.props"), s =>
{
  s = Regex.Replace(s, @"<TargetFramework>[^<]+</TargetFramework>", $"<TargetFramework>{tfm}</TargetFramework>");
  // Bekannte, harmlose Warnungen ausblenden: System.IO.Hashing (Vorabversion, offiziell erst ab .NET 10)
  // und ins Leere laufende Verweise auf Framework-Bibliotheken aus den alten Projektdateien (MSB3245/MSB3243)
  if (!s.Contains("SuppressTfmSupportBuildWarnings"))
    s = Regex.Replace(s, @"(<TargetFramework>[^<]+</TargetFramework>)",
      "$1\n    <SuppressTfmSupportBuildWarnings>true</SuppressTfmSupportBuildWarnings>\n    <MSBuildWarningsAsMessages>$(MSBuildWarningsAsMessages);MSB3245;MSB3243</MSBuildWarningsAsMessages>");
  return Regex.Replace(s, @"[ \t]*<PackageReference Include=""System\.(Runtime\.CompilerServices\.Unsafe|Numerics\.Vectors|Buffers|Memory)""[^>]*/>\r?\n?", "");
});

// 2. Hilfsklasse
var compatFile = Path.Combine(src, "ChanSort.Api", "Utils", "WasmCompat.cs");
const string compatCode = """
namespace ChanSort.Api
{
  /// <summary>
  /// Hilfsklasse fuer den Einsatz im Browser (WebAssembly). Ohne Konfiguration verhaelt sich alles wie bisher.
  /// - Location(): Assembly.Location ist im Browser leer; mit BaseDirectory wird ein Ersatzpfad gebildet.
  /// - Zip/Deflate-Funktionen: koennen durch eine rein verwaltete Implementierung ersetzt werden,
  ///   weil die native Kompression im Browser-Build abstuerzt.
  /// </summary>
  public static class WasmCompat
  {
    public static string BaseDirectory { get; set; }

    /// <summary>
    /// Im Browser gesetzt. Dort bringt das Setzen von Datei-Zeitstempeln/-Attributen die Laufzeit zum Absturz,
    /// deshalb werden solche Aufrufe dann uebersprungen.
    /// </summary>
    public static bool IsBrowser { get; set; }

    public static string Location(System.Reflection.Assembly assembly)
    {
      var location = assembly.Location;
      if (!string.IsNullOrEmpty(location) || string.IsNullOrEmpty(BaseDirectory))
        return location;
      return System.IO.Path.Combine(BaseDirectory, assembly.GetName().Name + ".dll");
    }

    public static System.Action<string, string> ExtractZip { get; set; } =
      (zipFile, targetDir) => System.IO.Compression.ZipFile.ExtractToDirectory(zipFile, targetDir);

    public static System.Action<string, string, bool> CreateZip { get; set; } =
      (sourceDir, zipFile, compress) => System.IO.Compression.ZipFile.CreateFromDirectory(sourceDir, zipFile,
        compress ? System.IO.Compression.CompressionLevel.Optimal : System.IO.Compression.CompressionLevel.NoCompression, false);

    public static System.Func<System.IO.Stream, System.IO.Stream> CreateInflateStream { get; set; } =
      input => new System.IO.Compression.DeflateStream(input, System.IO.Compression.CompressionMode.Decompress);

    public static System.Func<System.IO.Stream, bool, System.IO.Stream> CreateDeflateStream { get; set; } =
      (output, leaveOpen) => new System.IO.Compression.DeflateStream(output,
#if NETFRAMEWORK
        System.IO.Compression.CompressionLevel.Optimal,
#else
        System.IO.Compression.CompressionLevel.SmallestSize,
#endif
        leaveOpen);
  }
}

""";
if (!File.Exists(compatFile) || File.ReadAllText(compatFile) != compatCode)
{
  File.WriteAllText(compatFile, compatCode, new UTF8Encoding(true));
  Console.WriteLine("  neu:      " + Rel(compatFile));
  changedFiles++;
}

// 3. Assembly.Location ersetzen (nur in Api und Loadern, nicht in der Windows-Oberflaeche)
var locationRegex = new Regex(@"(this\.GetType\(\)\.Assembly|Assembly\.GetExecutingAssembly\(\)|typeof\([\w.]+\)\.Assembly)\.Location");
var dirs = Directory.GetDirectories(src, "ChanSort.Loader.*")
  .Where(d => !d.EndsWith(".UI", StringComparison.OrdinalIgnoreCase))
  .Append(Path.Combine(src, "ChanSort.Api"));
foreach (var dir in dirs)
{
  foreach (var file in Directory.GetFiles(dir, "*.cs", SearchOption.AllDirectories))
  {
    if (Path.GetFileName(file) == "WasmCompat.cs")
      continue;
    Patch(file, s => locationRegex.Replace(s, "global::ChanSort.Api.WasmCompat.Location($1)"));
  }
}

// 4. LG: Laden der optionalen UI-Assembly abfangen
var tllFile = Path.Combine(src, "ChanSort.Loader.LG", "Binary", "TllFileSerializer.cs");
if (File.Exists(tllFile))
{
  Patch(tllFile, s => s.Contains("/* no UI in browser */")
    ? s
    : Regex.Replace(s, @"(?<!void )this\.InitUiFactory\(\);", "try { this.InitUiFactory(); } catch { /* no UI in browser */ }"));
}

// 4b. LG: Forschungsdatei ohne Produktivnutzung (braucht SQL Server / System.Data.SqlClient) aus dem Build nehmen
var lgProj = Path.Combine(src, "ChanSort.Loader.LG", "ChanSort.Loader.LG.csproj");
if (File.Exists(lgProj))
{
  Patch(lgProj, s => s.Contains("TllFileSerializer.sql.cs")
    ? s
    : Regex.Replace(s, @"</Project>\s*$", "  <ItemGroup>\r\n    <Compile Remove=\"Binary\\TllFileSerializer.sql.cs\" />\r\n  </ItemGroup>\r\n</Project>\r\n"));
}

// 4c. Kompression ueber WasmCompat umleiten (native zlib stuerzt im Browser-Build ab)
PatchIfExists(Path.Combine(src, "ChanSort.Api", "Controller", "SerializerBase.cs"), s => s
  .Replace("ZipFile.ExtractToDirectory(this.FileName, this.TempPath);",
           "global::ChanSort.Api.WasmCompat.ExtractZip(this.FileName, this.TempPath);")
  .Replace("ZipFile.CreateFromDirectory(this.TempPath, this.FileName, compress ? CompressionLevel.Optimal : CompressionLevel.NoCompression, false);",
           "global::ChanSort.Api.WasmCompat.CreateZip(this.TempPath, this.FileName, compress);"));
PatchIfExists(Path.Combine(src, "ChanSort.Loader.MediaTek", "SvlTable.cs"), s =>
{
  s = s.Replace("new DeflateStream(input, CompressionMode.Decompress)", "global::ChanSort.Api.WasmCompat.CreateInflateStream(input)");
  return Regex.Replace(s, @"new DeflateStream\(comp, CompressionLevel\.\w+, true\)", "global::ChanSort.Api.WasmCompat.CreateDeflateStream(comp, true)");
});

// 4c2. Panasonic: Namen als Ausdruck lesen. Mit "rowid" in der Abfrage nutzt Microsoft.Data.Sqlite fuer GetBytes()
//      das Blob-Streaming, das im Browser nur Nullbytes liefert (leere Sendernamen). cast(... as blob) liefert dieselben Bytes.
PatchIfExists(Path.Combine(src, "ChanSort.Loader.Panasonic", "SvlSerializer.cs"),
  s => s.Replace("s.physical_ch,s.sname,t.freq", "s.physical_ch,cast(s.sname as blob) as sname,t.freq"));

// 4d. Windows-Pfadtrenner in Pfadangaben durch "/" ersetzen (funktioniert auch unter Windows)
PatchIfExists(Path.Combine(src, "ChanSort.Loader.Samsung", "Zip", "DbSerializer.cs"),
  s => s.Replace("this.TempPath + \"\\\\sat\"", "this.TempPath + \"/sat\""));
PatchIfExists(Path.Combine(src, "ChanSort.Loader.Philips", "XmlSerializer.cs"),
  s => Regex.Replace(s, @"@""(channellib|s2channellib)\\", @"@""$1/"));
PatchIfExists(Path.Combine(src, "ChanSort.Loader.Toshiba", "ChmgtDbSerializer.cs"),
  s => Regex.Replace(s, @"(private const string FILE_\w+ = "")([^""]+)("";)", m => m.Groups[1].Value + m.Groups[2].Value.Replace("\\\\", "/") + m.Groups[3].Value));

// 4e. Datei-Zeitstempel/-Attribute setzen bringt die Browser-Laufzeit zum Absturz -> im Browser ueberspringen
var setFileMeta = new Regex(@"(?<!IsBrowser\) )\b((?:File|Directory)\.Set(?:LastWriteTime|LastWriteTimeUtc|CreationTime|CreationTimeUtc|LastAccessTime|LastAccessTimeUtc|Attributes)\()");
foreach (var dir in Directory.GetDirectories(src, "ChanSort.Loader.*").Where(d => !d.EndsWith(".UI", StringComparison.OrdinalIgnoreCase)).Append(Path.Combine(src, "ChanSort.Api")))
{
  foreach (var file in Directory.GetFiles(dir, "*.cs", SearchOption.AllDirectories))
  {
    if (Path.GetFileName(file) == "WasmCompat.cs")
      continue;
    Patch(file, s => setFileMeta.Replace(s, "if (!global::ChanSort.Api.WasmCompat.IsBrowser) $1"));
  }
}

// 5. Windows-Forms-Schalter aus Loader-Projekten entfernen (z. B. VDR setzt ihn, nutzt Forms aber nicht).
//    Sonst bricht der Browser-Build mit NETSDK1136 ab.
foreach (var csproj in Directory.GetFiles(src, "ChanSort.Loader.*.csproj", SearchOption.AllDirectories))
{
  if (csproj.Contains(".UI", StringComparison.OrdinalIgnoreCase))
    continue;
  Patch(csproj, s => Regex.Replace(s, @"[ \t]*<(UseWindowsForms|UseWPF|ImportWindowsDesktopTargets)>true</\1>\r?\n?", ""));
}

Console.WriteLine(changedFiles == 0
  ? "ChanSort ist bereits vorbereitet, nichts zu tun."
  : $"Fertig: {changedFiles} Datei(en) angepasst, Zielframework {tfm}.");
return 0;


void Patch(string file, Func<string, string> transform)
{
  var bytes = File.ReadAllBytes(file);
  bool hasBom = bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
  var text = Encoding.UTF8.GetString(bytes, hasBom ? 3 : 0, bytes.Length - (hasBom ? 3 : 0));
  var patched = transform(text);
  if (patched == text)
    return;
  File.WriteAllText(file, patched, new UTF8Encoding(hasBom));
  Console.WriteLine("  geaendert: " + Rel(file));
  changedFiles++;
}

void PatchIfExists(string file, Func<string, string> transform)
{
  if (File.Exists(file))
    Patch(file, transform);
  else
    Console.WriteLine("  WARNUNG: nicht gefunden: " + Rel(file));
}

string Rel(string path) => Path.GetRelativePath(root, path);
