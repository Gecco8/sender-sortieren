using ChanSort.Api;
using ICSharpCode.SharpZipLib.Zip;
using ICSharpCode.SharpZipLib.Zip.Compression;
using ICSharpCode.SharpZipLib.Zip.Compression.Streams;

namespace ChanSortWeb;

/// <summary>
/// Ersetzt die native Kompression von .NET (zlib), die im Browser-Build abstuerzt ("unreachable executed"),
/// durch SharpZipLib, das komplett in C# geschrieben ist.
/// </summary>
internal static class ManagedCompression
{
  public static void Install()
  {
    WasmCompat.ExtractZip = ExtractZip;
    WasmCompat.CreateZip = CreateZip;
    WasmCompat.CreateInflateStream = input => new InflaterInputStream(input, new Inflater(true));
    WasmCompat.CreateDeflateStream = (output, leaveOpen) =>
      new DeflaterOutputStream(output, new Deflater(Deflater.BEST_COMPRESSION, true)) { IsStreamOwner = !leaveOpen };
  }

  public static void ExtractZip(string zipFile, string targetDir)
  {
    Directory.CreateDirectory(targetDir);
    // keine Zeitstempel/Attribute setzen: das bringt die Browser-Laufzeit zum Absturz
    new FastZip { RestoreDateTimeOnExtract = false, RestoreAttributesOnExtract = false }.ExtractZip(zipFile, targetDir, null);
  }

  /// <summary>Packt den Inhalt eines Ordners (ohne den Ordner selbst) in eine Zip-Datei.</summary>
  public static void CreateZip(string sourceDir, string zipFile, bool compress)
  {
    var fastZip = new FastZip
    {
      CompressionLevel = compress ? Deflater.CompressionLevel.DEFAULT_COMPRESSION : Deflater.CompressionLevel.NO_COMPRESSION,
      CreateEmptyDirectories = true,
    };
    fastZip.CreateZip(zipFile, sourceDir, true, null);
  }

  /// <summary>Packt einzelne Dateien mit relativen Pfaden in eine Zip-Datei im Speicher.</summary>
  public static byte[] ZipFiles(IEnumerable<(string FullPath, string EntryName)> files)
  {
    using var buffer = new MemoryStream();
    using (var zip = new ZipOutputStream(buffer) { IsStreamOwner = false })
    {
      zip.SetLevel(6);
      foreach (var (fullPath, entryName) in files)
      {
        zip.PutNextEntry(new ZipEntry(ZipEntry.CleanName(entryName)) { DateTime = DateTime.Now });
        using (var input = File.OpenRead(fullPath))
          input.CopyTo(zip);
        zip.CloseEntry();
      }
      zip.Finish();
    }
    return buffer.ToArray();
  }
}
