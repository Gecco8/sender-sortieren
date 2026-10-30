using System.Runtime.InteropServices.JavaScript;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using ChanSort;
using ChanSort.Api;

namespace ChanSortWeb;

/// <summary>
/// Schnittstelle zwischen der Web-Oberflaeche (JavaScript) und den ChanSort-Loadern (C#).
/// Alle Methoden liefern JSON zurueck; Fehler werden als {"ok":false,"error":"..."} gemeldet.
/// Dateien werden als Base64 uebergeben, das ist fuer Senderlisten (wenige MB) schnell genug.
/// </summary>
public static partial class Bridge
{
  private const string WorkDir = "/work";        // hochgeladene Dateien
  private const string ConfigDir = "/chansort";  // .ini-Dateien der Loader

  private static List<ISerializerPlugin> plugins;
  private static SerializerBase serializer;
  private static string currentFile;
  private static string currentPlugin;
  private static byte[] pendingDownload;

  #region Dialoge: Frage-Antwort-Verfahren

  // Die Loader stellen Fragen synchron (MessageBox, Auswahldialog). Im Browser kann C# aber nicht auf einen
  // HTML-Dialog warten. Deshalb: Stellt ein Loader eine Frage, fuer die noch keine Antwort vorliegt, wird der
  // Vorgang mit DialogNeededException abgebrochen und die Frage an die Oberflaeche gemeldet. Die Oberflaeche zeigt
  // den Dialog und ruft den Vorgang mit allen bisherigen Antworten erneut auf (SetAnswers). Da Laden deterministisch
  // ist, stellt der Loader dieselben Fragen in derselben Reihenfolge und bekommt die Antworten aus der Warteschlange.
  private sealed class DialogNeededException : Exception
  {
    public string Title { get; }
    public string Text { get; }
    public string[] Options { get; }
    public DialogNeededException(string title, string text, string[] options) : base("Rueckfrage noetig")
    {
      Title = title; Text = text; Options = options;
    }
  }

  private static readonly Queue<int> answers = new();
  private static readonly List<(string Title, string Text)> messages = new();

  /// <summary>Antworten fuer den naechsten Aufruf setzen, JSON-Array mit Optionsindizes, z. B. [0,1].</summary>
  [JSExport]
  internal static void SetAnswers(string answersJson)
  {
    answers.Clear();
    using var doc = JsonDocument.Parse(string.IsNullOrEmpty(answersJson) ? "[]" : answersJson);
    foreach (var a in doc.RootElement.EnumerateArray())
      answers.Enqueue(a.GetInt32());
  }

  private static int Ask(string title, string text, string[] options)
  {
    if (answers.Count > 0)
      return answers.Dequeue();
    throw new DialogNeededException(title ?? "", text ?? "", options);
  }

  private static string Question(DialogNeededException q) => Json(w =>
  {
    w.WriteBoolean("needsAnswer", true);
    w.WriteStartObject("question");
    w.WriteString("title", q.Title);
    w.WriteString("message", q.Text);
    w.WriteStartArray("options");
    foreach (var o in q.Options)
      w.WriteStringValue(o);
    w.WriteEndArray();
    w.WriteEndObject();
  }, ok: false);

  private static void WriteMessages(Utf8JsonWriter w)
  {
    w.WriteStartArray("messages");
    foreach (var (title, text) in messages)
    {
      w.WriteStartObject();
      w.WriteString("title", title ?? "");
      w.WriteString("message", text ?? "");
      w.WriteEndObject();
    }
    w.WriteEndArray();
    messages.Clear();
  }

  #endregion

  #region Init()

  [JSExport]
  internal static string Init()
  {
    try
    {
      Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
      // Texte der Loader auf Deutsch (soweit ChanSort Uebersetzungen hat); Zahlenformate bleiben neutral
      try
      {
        System.Globalization.CultureInfo.DefaultThreadCurrentUICulture = new System.Globalization.CultureInfo("de-DE");
        System.Globalization.CultureInfo.CurrentUICulture = System.Globalization.CultureInfo.DefaultThreadCurrentUICulture;
        System.Globalization.CultureInfo.DefaultThreadCurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
        System.Globalization.CultureInfo.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
      }
      catch { /* ohne Kulturdaten bleibt es bei Englisch */ }
      WriteConfigFiles();
      WasmCompat.BaseDirectory = ConfigDir;
      WasmCompat.IsBrowser = true; // Datei-Zeitstempel setzen bringt die Browser-Laufzeit zum Absturz
      Directory.SetCurrentDirectory(ConfigDir); // manche Loader suchen ihre .ini relativ zum aktuellen Verzeichnis
      Directory.CreateDirectory(WorkDir);
      ManagedCompression.Install(); // native zlib stuerzt im Browser ab, siehe ManagedCompression.cs

      View.Default = new View
      {
        MessageBoxImpl = ShowMessageBox,
        CreateActionBox = message => new WebActionBox(message),
        ShowHtmlBoxImpl = (html, title, width, height, onUrlClick) => messages.Add((title ?? "", StripHtml(html)))
      };

      plugins = CreatePlugins();
      return Json(w => w.WriteNumber("plugins", plugins.Count));
    }
    catch (Exception ex)
    {
      return Error(ex.ToString());
    }
  }

  private static void WriteConfigFiles()
  {
    Directory.CreateDirectory(ConfigDir);
    var assembly = typeof(Bridge).Assembly;
    foreach (var name in assembly.GetManifestResourceNames())
    {
      if (!name.StartsWith("ini/"))
        continue;
      using var stream = assembly.GetManifestResourceStream(name);
      using var buffer = new MemoryStream();
      stream!.CopyTo(buffer);
      var fileName = name.Substring(4);
      File.WriteAllBytes(Path.Combine(ConfigDir, fileName), buffer.ToArray());
      // Einige Loader schreiben den Pfad klein (ToLowerInvariant), das Browser-Dateisystem unterscheidet Gross/Klein
      var lower = fileName.ToLowerInvariant();
      if (lower != fileName)
        File.WriteAllBytes(Path.Combine(ConfigDir, lower), buffer.ToArray());
    }
  }

  private static List<ISerializerPlugin> CreatePlugins()
  {
    var list = new List<ISerializerPlugin>
    {
      new RefSerializerPlugin(),
      new ChanSort.Loader.Amdb.AmdbPlugin(),
      new ChanSort.Loader.Android.AndroidPlugin(),
      new ChanSort.Loader.Chmax.ChmaxPlugin(),
      new ChanSort.Loader.CmdbBin.CmdbPlugin(),
      new ChanSort.Loader.DBM.DbmPlugin(),
      new ChanSort.Loader.DvbViewer.DvbViewerPlugin(),
      new ChanSort.Loader.Enigma2.Enigma2Plugin(),
      new ChanSort.Loader.Grundig.GrundigPlugin(),
      new ChanSort.Loader.Hisense.HisensePlugin(),
      new ChanSort.Loader.LG.LgPlugin(),
      new ChanSort.Loader.Loewe.LoewePlugin(),
      new ChanSort.Loader.M3u.M3uPlugin(),
      new ChanSort.Loader.MediaTek.MediatekPlugin(),
      new ChanSort.Loader.Medion.MedionPlugin(),
      new ChanSort.Loader.Panasonic.PanasonicPlugin(),
      new ChanSort.Loader.Philips.PhilipsPlugin(),
      new ChanSort.Loader.Samsung.SamsungPlugin(),
      new ChanSort.Loader.SatcoDX.SatcoDxPlugin(),
      new ChanSort.Loader.SdxJson.SdxJsonPlugin(),
      new ChanSort.Loader.Sharp.SharpPlugin(),
      new ChanSort.Loader.Sony.SonyPlugin(),
      new ChanSort.Loader.TCL.TclPlugin(),
      new ChanSort.Loader.Toshiba.ToshibaPlugin(),
      new ChanSort.Loader.Unsupported.UnsupportedPlugin(),
      new ChanSort.Loader.VDR.VdrPlugin(),
      new ChanSort.Loader.VisionEdge4K.VisionEdge4KPlugin(),
    };
    foreach (var plugin in list)
      plugin.DllName = plugin.GetType().Assembly.GetName().Name + ".dll";
    // gleiche Reihenfolge wie in der Desktop-Version
    list.Sort((a, b) => string.Compare(a.PluginName, b.PluginName, StringComparison.Ordinal));
    return list;
  }

  #endregion

  #region Arbeitsbereich: ResetWorkspace(), PutFile()

  [JSExport]
  internal static void ResetWorkspace()
  {
    try { serializer?.Dispose(); } catch { /* Aufraeumen darf nie das Neuladen blockieren */ }
    serializer = null;
    currentFile = null;
    currentPlugin = null;
    pendingDownload = null;
    try
    {
      if (Directory.Exists(WorkDir))
        Directory.Delete(WorkDir, true);
    }
    catch (Exception ex)
    {
      Console.WriteLine("ResetWorkspace: " + ex.Message);
    }
    Directory.CreateDirectory(WorkDir);
  }

  [JSExport]
  internal static string PutFile(string relativePath, string base64)
  {
    try
    {
      var path = ToWorkPath(relativePath);
      Directory.CreateDirectory(Path.GetDirectoryName(path)!);
      File.WriteAllBytes(path, Convert.FromBase64String(base64));
      return Json(w => w.WriteString("path", relativePath));
    }
    catch (Exception ex)
    {
      return Error(ex.Message);
    }
  }

  private static string ToWorkPath(string relativePath)
  {
    var clean = relativePath.Replace('\\', '/').TrimStart('/');
    if (clean.Split('/').Any(part => part == ".." || part == ""))
      throw new ArgumentException("Ungueltiger Dateipfad: " + relativePath);
    return WorkDir + "/" + clean;
  }

  private static string ToRelativePath(string fullPath) => Path.GetRelativePath(WorkDir, fullPath).Replace('\\', '/');

  #endregion

  #region Laden: OpenAuto(), Open()

  /// <summary>
  /// Probiert alle hochgeladenen Dateien durch (flachste Ordnerebene zuerst) und oeffnet die erste, die ein Loader versteht.
  /// </summary>
  [JSExport]
  internal static string OpenAuto()
  {
    messages.Clear();
    try
    {
      return OpenAutoCore();
    }
    catch (DialogNeededException q)
    {
      return Question(q);
    }
    catch (Exception ex)
    {
      return Error(ex.Message);
    }
  }

  private static string OpenAutoCore()
  {
    var files = Directory.GetFiles(WorkDir, "*", SearchOption.AllDirectories)
      .OrderBy(f => ToRelativePath(f).Count(c => c == '/'))
      .ThenBy(f => f, StringComparer.OrdinalIgnoreCase)
      .ToList();
    if (files.Count == 0)
      return Error("Es wurden keine Dateien hochgeladen.");

    var errors = new StringBuilder();
    foreach (var file in files)
    {
      var result = TryOpen(file, errors, out bool authoritative);
      if (result != null || authoritative)
        return result ?? Error(errors.ToString());
    }
    return Error("Keine der Dateien konnte als Senderliste erkannt werden.\n\n" + errors);
  }

  /// <summary>
  /// Oeffnet eine bestimmte hochgeladene Datei (z. B. wenn die automatische Auswahl die falsche Datei erwischt hat).
  /// </summary>
  [JSExport]
  internal static string Open(string relativePath)
  {
    messages.Clear();
    try
    {
      var errors = new StringBuilder();
      var result = TryOpen(ToWorkPath(relativePath), errors, out _);
      return result ?? Error("Die Datei konnte nicht geladen werden.\n\n" + errors);
    }
    catch (DialogNeededException q)
    {
      return Question(q);
    }
    catch (Exception ex)
    {
      return Error(ex.Message);
    }
  }

  private static string TryOpen(string path, StringBuilder errors, out bool authoritative)
  {
    authoritative = false;
    var fileName = Path.GetFileName(path).ToLowerInvariant();

    // gleiche Dateinamen-Erkennung wie in der Desktop-Version
    var candidates = plugins.Where(p => p.FileFilter.ToLowerInvariant().Split(';').Any(filter =>
      Regex.IsMatch(fileName, filter.Replace(".", "\\.").Replace("*", ".*").Replace("?", ".")))).ToList();

    foreach (var plugin in candidates)
    {
      SerializerBase ser = null;
      try
      {
        ser = plugin.CreateSerializer(path);
        if (ser == null)
          continue;
        ser.DefaultEncoding = Encoding.GetEncoding(1252); // wie ChanSort auf einem deutschen/westeuropaeischen Windows
        ser.Load();
        ser.DataRoot.ValidateAfterLoad();
        ser.DataRoot.ApplyCurrentProgramNumbers(); // entspricht "aktuelle Senderreihenfolge uebernehmen"

        serializer?.Dispose();
        serializer = ser;
        currentFile = ToRelativePath(path);
        currentPlugin = plugin.PluginName;
        return GetState();
      }
      catch (DialogNeededException)
      {
        ser?.Dispose();
        throw;
      }
      catch (LoaderException ex) when (ex.Recovery == LoaderException.RecoveryMode.Fail)
      {
        ser?.Dispose();
        errors.AppendLine($"{ToRelativePath(path)} ({plugin.PluginName}): {ex.Message}");
        authoritative = true;
        return null;
      }
      catch (Exception ex)
      {
        ser?.Dispose();
        errors.AppendLine($"{ToRelativePath(path)} ({plugin.PluginName}): {ex.Message}");
      }
    }
    return null;
  }

  #endregion

  #region GetState()

  /// <summary>
  /// Liefert die aktuell geladene Senderliste als JSON fuer die Oberflaeche.
  /// </summary>
  [JSExport]
  internal static string GetState()
  {
    if (serializer == null)
      return Error("Es ist keine Senderliste geladen.");

    var root = serializer.DataRoot;
    var features = serializer.Features;
    return Json(w =>
    {
      w.WriteString("file", currentFile);
      w.WriteString("plugin", currentPlugin);
      w.WriteString("model", serializer.TvModelName ?? "");
      w.WriteString("format", serializer.FileFormatVersion ?? "");
      w.WriteString("warnings", root.Warnings.ToString());
      WriteMessages(w);

      // alle Dateien, die der Loader fuer diese Senderliste liest/schreibt (fuer die Dateiliste in der Oberflaeche)
      w.WriteStartArray("dataFiles");
      try
      {
        foreach (var f in serializer.GetDataFilePaths().Where(p => !string.IsNullOrEmpty(p) && File.Exists(p)).Distinct())
          w.WriteStringValue(ToRelativePath(Path.GetFullPath(f)));
      }
      catch { /* nur Zusatzinformation */ }
      w.WriteEndArray();

      int favCount = FavCount();
      w.WriteStartObject("features");
      w.WriteBoolean("canDelete", features.DeleteMode != SerializerBase.DeleteMode.NotSupported);
      w.WriteBoolean("canHide", features.CanHideChannels);
      w.WriteString("favMode", root.FavoritesMode switch
      {
        FavoritesMode.Flags => "flags",
        FavoritesMode.OrderedPerSource => "ordered",
        FavoritesMode.MixedSource => "mixed",
        _ => "none",
      });
      w.WriteNumber("favCount", favCount);
      w.WriteEndObject();

      w.WriteStartArray("lists");
      int listId = 0;
      foreach (var list in root.ChannelLists)
      {
        w.WriteStartObject();
        w.WriteNumber("id", listId++);
        w.WriteString("caption", list.ShortCaption ?? "");
        w.WriteBoolean("readOnly", list.ReadOnly);
        w.WriteBoolean("isFavList", list.IsMixedSourceFavoritesList);
        w.WriteStartArray("favCaptions");
        for (int k = 0; k < favCount; k++)
          w.WriteStringValue(list.GetFavListCaption(k, true) ?? $"Fav {(char)('A' + k)}");
        w.WriteEndArray();
        w.WriteNumber("start", GetStartNumber(list));
        w.WriteBoolean("canRename", CanRename(list));
        w.WriteNumber("maxNameLength", list.MaxChannelNameLength);

        w.WriteStartArray("channels");
        for (int i = 0; i < list.Channels.Count; i++)
        {
          var ch = list.Channels[i];
          if (ch.IsProxy)
            continue;
          w.WriteStartObject();
          w.WriteNumber("id", i);
          w.WriteNumber("nr", ch.NewProgramNr);
          w.WriteNumber("oldNr", ch.OldProgramNr);
          w.WriteString("name", ch.Name ?? "");
          w.WriteString("type", ServiceType(ch));
          w.WriteBoolean("encrypted", ch.Encrypted == true);
          w.WriteBoolean("hidden", ch.Hidden);
          w.WriteBoolean("deleted", ch.IsDeleted);
          w.WriteString("satellite", ch.Satellite ?? "");
          w.WriteNumber("freq", ch.FreqInMhz);
          w.WriteNumber("sid", ch.ServiceId);
          w.WriteString("provider", ch.Provider ?? "");
          if (favCount > 0)
          {
            // je Favoritenliste: Position (>= 0) oder -1 = nicht enthalten. Bei reinen Markierungen 1 / -1.
            w.WriteStartArray("fav");
            for (int k = 1; k <= favCount; k++)
              w.WriteNumberValue(FavPosition(ch, k));
            w.WriteEndArray();
          }
          w.WriteEndObject();
        }
        w.WriteEndArray();
        w.WriteEndObject();
      }
      w.WriteEndArray();
    });
  }

  private static int FavCount() =>
    serializer.DataRoot.FavoritesMode == FavoritesMode.None ? 0 : Math.Max(0, serializer.DataRoot.FavListCount);

  private static int FavPosition(ChannelInfo ch, int k)
  {
    if (serializer.DataRoot.FavoritesMode == FavoritesMode.Flags)
      return k <= 8 && ((int)ch.Favorites & (1 << (k - 1))) != 0 ? 1 : -1;
    var pos = ch.GetPosition(k);
    return pos >= 0 ? pos : -1;
  }

  /// <summary>
  /// Favoriten einer Liste setzen. favs = je Favoritenliste die Kanal-IDs in Reihenfolge (Mitglieder).
  /// </summary>
  private static void ApplyFavorites(ChannelList list, JsonElement favs)
  {
    var root = serializer.DataRoot;
    int favCount = FavCount();
    bool sorted = root.FavoritesMode != FavoritesMode.Flags;
    var members = new List<Dictionary<int, int>>();
    foreach (var arr in favs.EnumerateArray())
    {
      var map = new Dictionary<int, int>();
      int pos = 1;
      foreach (var id in arr.EnumerateArray())
        map[id.GetInt32()] = pos++;
      members.Add(map);
    }

    for (int i = 0; i < list.Channels.Count; i++)
    {
      var ch = list.Channels[i];
      if (ch.IsProxy)
        continue;
      for (int k = 1; k <= favCount && k <= members.Count; k++)
      {
        bool isMember = members[k - 1].TryGetValue(i, out int pos);
        ch.SetPosition(k, isMember ? (sorted ? pos : 1) : -1);
        if (k <= 8)
        {
          var mask = (Favorites)(1 << (k - 1));
          ch.Favorites = isMember ? ch.Favorites | mask : ch.Favorites & ~mask;
        }
      }
    }
    root.NeedsSaving = true;
  }

  /// <summary>Wie in der Desktop-Version: Namen sind editierbar, wenn das Format es fuer diese Signalart erlaubt.</summary>
  private static bool CanRename(ChannelList list)
  {
    if (list.ReadOnly || list.IsMixedSourceFavoritesList)
      return false;
    var mode = serializer.Features.ChannelNameEdit;
    SignalSource src = 0;
    if ((mode & ChannelNameEditMode.Analog) != 0)
      src |= SignalSource.Analog;
    if ((mode & ChannelNameEditMode.Digital) != 0)
      src |= SignalSource.Dvb;
    return (list.SignalSource & src) != 0;
  }

  private static string ServiceType(ChannelInfo ch)
  {
    var type = ch.SignalSource & SignalSource.MaskTvRadioData;
    return type == SignalSource.Radio ? "radio" : type == SignalSource.Data ? "data" : "tv";
  }

  /// <summary>
  /// Erste Programmnummer beim Neunummerieren: kleinste bisher vergebene Nummer der Liste.
  /// So bleibt z. B. eine Radioliste, die bei 1000 beginnt, bei 1000.
  /// </summary>
  private static int GetStartNumber(ChannelList list)
  {
    var numbers = list.Channels
      .Where(c => !c.IsProxy && !c.IsDeleted && c.OldProgramNr >= list.FirstProgramNumber && c.OldProgramNr >= 0)
      .Select(c => c.OldProgramNr)
      .ToList();
    return numbers.Count > 0 ? numbers.Min() : Math.Max(1, list.FirstProgramNumber);
  }

  #endregion

  #region Save()

  /// <summary>
  /// Uebernimmt die neue Reihenfolge und speichert. Erwartet JSON:
  /// {"lists":[{"id":0,"order":[5,2,7,...],"names":{"5":"Neuer Name"}}, ...]}
  /// (Kanal-IDs in neuer Reihenfolge, fehlende IDs = geloescht; names optional: geaenderte Sendernamen)
  /// Die Datei selbst wird danach mit TakeDownload() abgeholt.
  /// </summary>
  [JSExport]
  internal static string Save(string editsJson)
  {
    if (serializer == null)
      return Error("Es ist keine Senderliste geladen.");
    messages.Clear();
    try
    {
      var root = serializer.DataRoot;
      var lists = root.ChannelLists.ToList();
      var features = serializer.Features;
      bool canDelete = features.DeleteMode != SerializerBase.DeleteMode.NotSupported;
      var edited = new HashSet<ChannelList>();

      using (var doc = JsonDocument.Parse(editsJson))
      {
        foreach (var edit in doc.RootElement.GetProperty("lists").EnumerateArray())
        {
          var list = lists[edit.GetProperty("id").GetInt32()];
          if (edit.TryGetProperty("favs", out var favs) && FavCount() > 0 && !list.ReadOnly)
            ApplyFavorites(list, favs);
          if (list.ReadOnly || list.IsMixedSourceFavoritesList)
            continue;
          if (edit.TryGetProperty("names", out var names) && CanRename(list))
          {
            foreach (var entry in names.EnumerateObject())
            {
              var ch = list.Channels[int.Parse(entry.Name)];
              var newName = entry.Value.GetString() ?? "";
              if (list.MaxChannelNameLength > 0 && newName.Length > list.MaxChannelNameLength)
                newName = newName.Substring(0, list.MaxChannelNameLength);
              if (newName != ch.Name)
              {
                ch.Name = newName;
                ch.IsNameModified = true;
              }
            }
          }
          if (edit.TryGetProperty("order", out var orderJson))
          {
            var order = orderJson.EnumerateArray().Select(e => e.GetInt32()).ToList();
            ApplyOrder(root, list, order, canDelete, features.CanHideChannels);
            edited.Add(list);
          }
        }
      }

      // Listen ohne Aenderung: Sender ohne Nummer hinten anhaengen (wie "Anhaengen" in der Desktop-Version)
      foreach (var list in lists.Where(l => !edited.Contains(l) && !l.IsMixedSourceFavoritesList))
      {
        int max = list.Channels.Where(c => !c.IsProxy).Select(c => c.NewProgramNr).DefaultIfEmpty(0).Max();
        foreach (var ch in list.Channels.Where(c => !c.IsProxy && !c.IsDeleted && c.NewProgramNr < 0).OrderBy(c => c.OldProgramNr))
          ch.NewProgramNr = ++max;
      }

      if (features.EnforceTvBeforeRadioBeforeData)
        new Editor { DataRoot = root }.EnforceTvBeforeRadioBeforeData();

      serializer.Save();
      root.ValidateAfterSave();

      // Ergebnis einsammeln: eine Datei direkt, mehrere als ZIP mit Ordnerstruktur
      var files = serializer.GetDataFilePaths().Where(File.Exists).Distinct().ToList();
      if (files.Count == 0)
        files.Add(serializer.FileName);

      string downloadName;
      bool isZip = files.Count > 1;
      if (!isZip)
      {
        pendingDownload = File.ReadAllBytes(files[0]);
        downloadName = Path.GetFileName(files[0]);
      }
      else
      {
        pendingDownload = ManagedCompression.ZipFiles(files.Select(f => (f, ToRelativePath(f))));
        downloadName = "Senderliste.zip";
      }

      return Json(w =>
      {
        w.WriteString("fileName", downloadName);
        w.WriteBoolean("zip", isZip);
        w.WriteStartArray("files");
        foreach (var f in files)
          w.WriteStringValue(ToRelativePath(f));
        w.WriteEndArray();
        WriteMessages(w);
      });
    }
    catch (DialogNeededException q)
    {
      return Question(q);
    }
    catch (Exception ex)
    {
      return Error("Speichern fehlgeschlagen: " + ex.Message);
    }
  }

  private static void ApplyOrder(DataRoot root, ChannelList list, List<int> order, bool canDelete, bool canHide)
  {
    int start = GetStartNumber(list);
    var keep = new HashSet<int>(order);

    // Nummern fuer behaltene Sender in der neuen Reihenfolge
    int nr = start;
    foreach (var id in order)
    {
      var ch = list.Channels[id];
      ch.IsDeleted = false;
      ch.NewProgramNr = nr++;
    }

    // Entfernte Sender: loeschen, wenn das Format es kann, sonst ausblenden und hinten anhaengen
    for (int i = 0; i < list.Channels.Count; i++)
    {
      var ch = list.Channels[i];
      if (ch.IsProxy || keep.Contains(i))
        continue;
      if (canDelete)
      {
        ch.IsDeleted = true;
        ch.NewProgramNr = root.DeletedChannelsNeedNumbers ? nr++ : 0;
      }
      else
      {
        if (canHide)
        {
          ch.Hidden = true;
          ch.Skip = true;
        }
        ch.NewProgramNr = nr++;
      }
    }
    root.NeedsSaving = true;
  }

  /// <summary>
  /// Liefert die beim letzten Save() erzeugte Datei als Base64.
  /// </summary>
  [JSExport]
  internal static string TakeDownload()
  {
    var data = pendingDownload;
    pendingDownload = null;
    return data == null ? "" : Convert.ToBase64String(data);
  }

  #endregion

  #region Dialoge

  private static View.DialogResult ShowMessageBox(string message, string caption, View.MessageBoxButtons buttons, View.MessageBoxIcon icon)
  {
    switch (buttons)
    {
      case View.MessageBoxButtons.OKCancel:
        return Ask(caption, message, new[] { "OK", "Abbrechen" }) == 0 ? View.DialogResult.OK : View.DialogResult.Cancel;
      case View.MessageBoxButtons.YesNo:
      case View.MessageBoxButtons.YesNoCancel:
        return Ask(caption, message, new[] { "Ja", "Nein" }) == 0 ? View.DialogResult.Yes : View.DialogResult.No;
      default:
        messages.Add((caption, message)); // reine Hinweise: nach dem Laden gesammelt anzeigen
        return View.DialogResult.OK;
    }
  }

  /// <summary>
  /// Auswahldialog der Loader. Besonderheiten im Browser:
  /// - Optionen, die eine Webseite oeffnen wuerden (Process.Start), werden ausgeblendet; das geht in der Sandbox nicht.
  /// - Keine Antwort/Abbrechen waehlt die letzte Option (bei ChanSort ist das "Abbrechen").
  /// - Manche Loader fragen in einer Schleife erneut; nach einigen Wiederholungen wird die letzte Option gewaehlt.
  /// </summary>
  private sealed class WebActionBox : IActionBoxDialog
  {
    private static readonly Regex WebLink = new(@"github|http|www\.|webpage|web page|webseite|website|wiki", RegexOptions.IgnoreCase);
    private readonly List<(string Text, int Result)> actions = new();
    private int shown;

    public WebActionBox(string message) { Message = message; }

    public string Message { get; set; }
    public int SelectedAction { get; private set; } = -1;

    public void AddAction(string text, int result) => actions.Add((text, result));

    public void ShowDialog()
    {
      var visible = actions.Where(a => !WebLink.IsMatch(a.Text ?? "")).ToList();
      if (visible.Count == 0)
        visible = actions.ToList();
      if (visible.Count == 0)
      {
        SelectedAction = -1;
        return;
      }

      if (++shown > 3)
      {
        SelectedAction = visible[^1].Result;
        return;
      }

      int index = Ask("", Message, visible.Select(a => a.Text).ToArray());
      SelectedAction = index >= 0 && index < visible.Count ? visible[index].Result : visible[^1].Result;
    }

    public void Dispose() { }
  }

  private static string StripHtml(string html)
  {
    var text = Regex.Replace(html ?? "", @"<br\s*/?>", "\n", RegexOptions.IgnoreCase);
    text = Regex.Replace(text, "<[^>]+>", "");
    return System.Net.WebUtility.HtmlDecode(text).Trim();
  }

  #endregion

  #region JSON-Hilfen

  private static string Json(Action<Utf8JsonWriter> body, bool ok = true)
  {
    using var buffer = new MemoryStream();
    using (var w = new Utf8JsonWriter(buffer))
    {
      w.WriteStartObject();
      w.WriteBoolean("ok", ok);
      body(w);
      w.WriteEndObject();
    }
    return Encoding.UTF8.GetString(buffer.ToArray());
  }

  private static string Error(string message)
  {
    using var buffer = new MemoryStream();
    using (var w = new Utf8JsonWriter(buffer))
    {
      w.WriteStartObject();
      w.WriteBoolean("ok", false);
      w.WriteString("error", message);
      w.WriteEndObject();
    }
    return Encoding.UTF8.GetString(buffer.ToArray());
  }

  #endregion
}
