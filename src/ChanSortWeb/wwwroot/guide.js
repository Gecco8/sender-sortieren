// Hell/Dunkel-Schalter für die Anleitungsseiten (gleiche Logik wie im Editor)
(function () {
  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  const effective = () => document.documentElement.dataset.theme || (media.matches ? 'dark' : 'light');
  const sync = () => { toggle.checked = effective() === 'dark'; };
  sync();
  media.addEventListener?.('change', sync);
  toggle.addEventListener('change', () => {
    const theme = toggle.checked ? 'dark' : 'light';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('theme', theme); } catch { /* ohne Speicher gilt die Wahl nur bis zum Neuladen */ }
  });
})();
