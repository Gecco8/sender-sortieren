// Startet die .NET-Laufzeit im Browser und verbindet sie mit der Oberfläche (app.js).
import { dotnet } from './_framework/dotnet.js';
import { createApp } from './app.js';

const overlayText = document.getElementById('overlayText');

try {
  // de-DE: ChanSort bringt für viele Meldungen deutsche Übersetzungen mit (Satelliten-Ressourcen).
  const { getAssemblyExports, getConfig } = await dotnet
    .withApplicationCulture('de-DE')
    .withConfig({ loadAllSatelliteResources: true })
    .create();

  const exports = await getAssemblyExports(getConfig().mainAssemblyName);
  const bridge = exports.ChanSortWeb.Bridge;

  const init = JSON.parse(bridge.Init());
  if (!init.ok)
    throw new Error(init.error);

  createApp(bridge);
  document.getElementById('overlay').hidden = true;

  // Main() wird bewusst NICHT ausgeführt: Sowohl dotnet.run() als auch runMain() beenden nach Main()
  // den nativen Teil der Laufzeit (Emscripten), in dem SQLite läuft. Danach stürzen Samsung, Panasonic
  // usw. mit "called after runtime exit" ab. Die exportierten Funktionen funktionieren auch ohne Main().
} catch (err) {
  console.error(err);
  overlayText.textContent = 'Der Editor konnte nicht gestartet werden: ' + (err?.message ?? err);
}
