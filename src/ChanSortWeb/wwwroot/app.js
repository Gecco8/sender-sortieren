// Oberfläche des Senderlisten-Editors.
// Hält die Reihenfolge jeder Liste als Array von Kanal-IDs; beim Speichern wird nur diese
// Reihenfolge an den C#-Teil übergeben, der sie mit den ChanSort-Loadern in die Datei schreibt.

const $ = (id) => document.getElementById(id);
const TYPE_LABEL = { tv: 'TV', radio: 'Radio', data: 'Daten' };

export function createApp(bridge) {
  const ui = createDialogs();
  initThemeSwitch();

  let data = null;        // Antwort von GetState()
  let lists = [];         // [{ id, caption, readOnly, start, order:[ids], deleted:[ids], byId:Map, original }]
  let current = 0;        // Index in lists
  let sub = 0;            // 0 = Hauptliste, k = Favoritenliste k
  let favMode = 'none';   // none | flags | ordered | mixed
  let favCount = 0;
  let showDeleted = false;
  let selection = new Set();
  let anchorId = null;
  let filter = '';
  let undoStack = [];
  let uploadedPaths = [];

  // ---------------------------------------------------------------- Laden

  /**
   * Ruft eine Funktion der Brücke auf und beantwortet dabei Rückfragen der Loader.
   * Stellt ein Loader eine Frage, kommt {needsAnswer, question} zurück; dann wird der Dialog gezeigt
   * und der Aufruf mit allen bisherigen Antworten wiederholt (siehe Bridge.cs, "Frage-Antwort-Verfahren").
   */
  async function callBridge(fn, busyText) {
    const answers = [];
    for (let round = 0; round < 20; round++) {
      bridge.SetAnswers(JSON.stringify(answers));
      busy(busyText);
      await nextFrame();
      const result = JSON.parse(fn());
      if (!result.needsAnswer) return result;
      idle();
      const q = result.question;
      let index = await ui.choose(q.title, q.message, q.options);
      if (index < 0) index = q.options.length - 1; // Schließen = letzte Option (bei ChanSort "Abbrechen")
      answers.push(index);
    }
    return { ok: false, error: 'Zu viele Rückfragen, Vorgang abgebrochen.' };
  }

  async function loadEntries(entries) {
    if (entries.length === 0) return;
    if (isDirty() && !await ui.confirm('Andere Datei öffnen?', 'Ungespeicherte Änderungen gehen verloren.', 'Öffnen')) return;

    busy('Dateien werden eingelesen …');
    try {
      bridge.ResetWorkspace();
      uploadedPaths = [];
      for (const { path, file } of entries) {
        const result = JSON.parse(bridge.PutFile(path, toBase64(await file.arrayBuffer())));
        if (!result.ok) throw new Error(result.error);
        uploadedPaths.push(path);
      }
      const result = await callBridge(() => bridge.OpenAuto(), 'Senderliste wird erkannt …');
      idle();
      await applyState(result);
    } catch (err) {
      idle();
      await ui.info('Fehler beim Einlesen', err.message);
    } finally {
      idle();
    }
  }

  async function openSpecificFile(path) {
    if (data && path === data.file) return;
    if (isDirty() && !await ui.confirm('Andere Datei öffnen?', 'Ungespeicherte Änderungen an der aktuellen Liste gehen verloren.', 'Öffnen')) return;
    try {
      const result = await callBridge(() => bridge.Open(path), 'Datei wird geladen …');
      idle();
      await applyState(result);
    } finally {
      idle();
    }
  }

  async function applyState(state, keepNotice = false) {
    if (!state.ok) {
      await ui.info('Die Datei konnte nicht geöffnet werden', state.error);
      return;
    }
    data = state;
    favMode = state.features.favMode || 'none';
    favCount = state.features.favCount || 0;
    const sortedFav = favMode !== 'flags';

    // leere Listen (z. B. "DVB-T Radio" bei einem reinen Sat-Empfang) gar nicht erst als Reiter anzeigen
    lists = state.lists.filter((l) => l.channels.length > 0).map((l) => {
      const byId = new Map(l.channels.map((c) => [c.id, c]));
      const active = l.channels.filter((c) => !c.deleted);
      const assigned = active.filter((c) => c.nr >= 0).sort((a, b) => a.nr - b.nr);
      const unassigned = active.filter((c) => c.nr < 0).sort((a, b) => a.id - b.id);
      const order = [...assigned, ...unassigned].map((c) => c.id);
      const deleted = l.channels.filter((c) => c.deleted).map((c) => c.id);
      const mainIndex = new Map(order.map((id, i) => [id, i]));

      // Favoritenlisten: je Liste die Mitglieder in ihrer Reihenfolge
      const favs = [];
      for (let k = 0; k < favCount; k++) {
        favs.push(active.filter((c) => c.fav && c.fav[k] >= 0)
          .sort((a, b) => (sortedFav ? a.fav[k] - b.fav[k] : 0) || (mainIndex.get(a.id) - mainIndex.get(b.id)))
          .map((c) => c.id));
      }
      return {
        id: l.id, caption: l.caption, readOnly: l.readOnly, isFavList: l.isFavList, start: l.start, byId,
        order, deleted, original: order.join(','), deletedOriginal: deleted.join(','),
        canRename: l.canRename, maxNameLength: l.maxNameLength, names: new Map(),
        favCaptions: l.favCaptions || [], favs, favOriginal: JSON.stringify(favs),
      };
    });

    // die größte bearbeitbare Liste zuerst zeigen (z. B. DVB-S statt der meist leeren Analog-Liste)
    current = 0;
    lists.forEach((l, i) => {
      const best = lists[current];
      const rank = (x) => (x.readOnly || x.isFavList ? 0 : 1);
      if (rank(l) > rank(best) || (rank(l) === rank(best) && l.order.length > best.order.length))
        current = i;
    });
    sub = defaultSub(list());
    selection.clear();
    undoStack = [];
    showDeleted = false;
    filter = '';
    $('search').value = '';

    $('startView').hidden = true;
    $('editorView').hidden = false;
    renderFileInfo();
    renderAll();

    if (!keepNotice) {
      if (state.warnings && state.warnings.trim())
        showWarnings(state.warnings.trim());
      else if (!state.features.canDelete)
        showNotice('Dieses Format kann Sender nicht löschen. Gelöschte Sender werden stattdessen ausgeblendet und ans Ende gesetzt.', 'info');
      else
        hideNotice();
    }
    await showLoaderMessages(state.messages);
  }

  /** Hinweise der Loader (z. B. Philips: "nach dem Import Stecker ziehen") gesammelt anzeigen. */
  async function showLoaderMessages(messages) {
    for (const m of messages || [])
      await ui.info(m.title || 'Hinweis', m.message);
  }

  // ---------------------------------------------------------------- Ansichten: Hauptliste und Favoritenlisten
  //
  // sub = 0: Hauptliste (bei der gemischten Favoritenliste: "Alle Sender")
  // sub = k: Favoritenliste k (A = 1, B = 2, ...)

  const list = () => lists[current];
  const editable = () => list() && !list().readOnly;
  const nameOf = (l, ch) => (l.names.has(ch.id) ? l.names.get(ch.id) : ch.name);

  /** Favoritenlisten mit eigener Reihenfolge, die als eigene Ansicht gezeigt werden. */
  const hasFavViews = (l) => favCount > 0 && !l.readOnly && (l.isFavList || favMode === 'ordered');
  /** Spalte mit A/B/C/D-Schaltern in der Hauptansicht (bei gemischten Favoriten nur in der Favoritenliste). */
  const hasFavColumn = (l) => favCount > 0 && !l.readOnly && sub === 0 && (l.isFavList || favMode !== 'mixed');
  const defaultSub = (l) => (l && l.isFavList && favCount > 0 ? 1 : 0);
  const favLetter = (k) => String.fromCharCode(65 + k);
  const favCaption = (l, k) => {
    const c = l.favCaptions[k] || `Fav ${favLetter(k)}`;
    return c.startsWith('Fav ') ? `Favoriten ${favLetter(k)}` : c;
  };

  /** Die gerade bearbeitete Reihenfolge (Hauptliste oder Favoritenliste). */
  const cur = () => (sub === 0 ? list().order : list().favs[sub - 1]);
  function setCur(arr) {
    if (sub === 0) list().order = arr;
    else list().favs[sub - 1] = arr;
  }
  const curStart = () => (sub === 0 ? list().start : 1);
  /** Darf in der aktuellen Ansicht sortiert werden? (nicht in "Alle Sender" der gemischten Favoritenliste) */
  const canReorder = () => editable() && !showDeleted && !(sub === 0 && list().isFavList);

  const orderChanged = (l) => l.order.join(',') !== l.original || l.deleted.join(',') !== l.deletedOriginal;
  const favsChanged = (l) => JSON.stringify(l.favs) !== l.favOriginal;
  const isChanged = (l) => !l.readOnly && ((!l.isFavList && orderChanged(l)) || l.names.size > 0 || favsChanged(l));

  function snapshot() {
    const l = list();
    undoStack.push({
      index: current, sub, order: [...l.order], deleted: [...l.deleted], names: new Map(l.names), favs: l.favs.map((f) => [...f]),
    });
    if (undoStack.length > 200) undoStack.shift();
  }

  function undo() {
    const step = undoStack.pop();
    if (!step) return;
    current = step.index;
    sub = step.sub;
    Object.assign(list(), { order: step.order, deleted: step.deleted, names: step.names, favs: step.favs });
    selection.clear();
    renderAll();
  }

  function selectedInOrder(arr) {
    return arr.filter((id) => selection.has(id));
  }

  function moveSelectedTo(targetIndex) {
    const o = cur();
    const moving = selectedInOrder(o);
    if (moving.length === 0) return;
    snapshot();
    // Zielindex um die vorher entfernten Elemente korrigieren
    const before = o.slice(0, targetIndex).filter((id) => !selection.has(id)).length;
    const rest = o.filter((id) => !selection.has(id));
    rest.splice(before, 0, ...moving);
    setCur(rest);
    renderRows();
    scrollToId(moving[0]);
  }

  function moveStep(direction) {
    if (selection.size === 0) return;
    snapshot();
    const o = [...cur()];
    if (direction < 0) {
      for (let i = 1; i < o.length; i++)
        if (selection.has(o[i]) && !selection.has(o[i - 1])) [o[i - 1], o[i]] = [o[i], o[i - 1]];
    } else {
      for (let i = o.length - 2; i >= 0; i--)
        if (selection.has(o[i]) && !selection.has(o[i + 1])) [o[i + 1], o[i]] = [o[i], o[i + 1]];
    }
    setCur(o);
    renderRows();
    scrollToId(selectedInOrder(o)[0]);
  }

  async function moveToPosition() {
    if (selection.size === 0 || !canReorder()) return;
    const o = cur();
    const start = curStart();
    const first = start + Math.max(0, o.findIndex((id) => selection.has(id)));
    const nr = await ui.askNumber('An Position verschieben',
      `Neue ${sub === 0 ? 'Programmnummer' : 'Position in ' + favCaption(list(), sub - 1)} für ${selection.size === 1 ? 'den ausgewählten Sender' : `${selection.size} ausgewählte Sender`} (${start} bis ${start + o.length - 1}):`,
      first, start, start + o.length - 1);
    if (!Number.isInteger(nr)) return;
    moveSelectedTo(Math.min(Math.max(nr - start, 0), o.length));
  }

  /** Ausgewählten Sender umbenennen (nur wenn das Format es erlaubt). */
  async function renameSelected() {
    const l = list();
    if (!l.canRename || selection.size !== 1 || showDeleted) return;
    const ch = l.byId.get([...selection][0]);
    const oldName = nameOf(l, ch);
    const limit = l.maxNameLength > 0 ? `\nDieses Format erlaubt höchstens ${l.maxNameLength} Zeichen.` : '';
    const name = await ui.askText('Sender umbenennen', `Neuer Name für „${oldName || '(ohne Namen)'}“:${limit}`, oldName, l.maxNameLength);
    if (name === null || name === oldName) return;
    snapshot();
    if (name === ch.name) l.names.delete(ch.id);
    else l.names.set(ch.id, name);
    renderRows();
  }

  /** Hauptliste: Sender löschen. Favoritenansicht: Sender aus dieser Favoritenliste entfernen. */
  function deleteSelected() {
    const l = list();
    const ids = selectedInOrder(cur());
    if (ids.length === 0 || !canReorder()) return;
    snapshot();
    if (sub === 0) {
      l.order = l.order.filter((id) => !selection.has(id));
      l.deleted = [...l.deleted, ...ids];
      l.favs = l.favs.map((f) => f.filter((id) => !selection.has(id))); // gelöschte Sender auch aus den Favoriten nehmen
    } else {
      l.favs[sub - 1] = l.favs[sub - 1].filter((id) => !selection.has(id));
    }
    selection.clear();
    renderAll();
  }

  function restoreSelected() {
    const l = list();
    const ids = selectedInOrder(l.deleted);
    if (ids.length === 0) return;
    snapshot();
    l.deleted = l.deleted.filter((id) => !selection.has(id));
    l.order = [...l.order, ...ids];
    selection.clear();
    renderAll();
  }

  /** Favoriten-Schalter A/B/C/D: für den Sender (oder alle ausgewählten, wenn er dazugehört) an- bzw. abwählen. */
  function toggleFavorite(id, k) {
    const l = list();
    const ids = selection.has(id) && selection.size > 1 ? selectedInOrder(l.order) : [id];
    const add = !l.favs[k].includes(id);
    snapshot();
    if (add) l.favs[k] = [...l.favs[k], ...ids.filter((x) => !l.favs[k].includes(x))];
    else l.favs[k] = l.favs[k].filter((x) => !ids.includes(x));
    renderAll();
  }

  function isDirty() {
    return lists.some(isChanged);
  }

  // ---------------------------------------------------------------- Speichern

  async function save() {
    const changed = lists.filter(isChanged);
    if (changed.length === 0 && !await ui.confirm('Keine Änderungen', 'Es gibt keine Änderungen. Trotzdem speichern?', 'Speichern')) return;

    try {
      const edits = JSON.stringify({
        lists: changed.map((l) => ({
          id: l.id,
          order: !l.isFavList && orderChanged(l) ? l.order : undefined,
          names: Object.fromEntries(l.names),
          favs: favsChanged(l) ? l.favs : undefined,
        })),
      });
      const result = await callBridge(() => bridge.Save(edits), 'Senderliste wird gespeichert …');
      if (!result.ok) {
        idle();
        await ui.info('Speichern fehlgeschlagen', result.error);
        return;
      }
      download(fromBase64(bridge.TakeDownload()), result.fileName);
      showNotice(result.zip
        ? `Gespeichert als ${result.fileName}. Bitte entpacken und die Dateien mit genau dieser Ordnerstruktur auf den USB-Stick kopieren.`
        : `Gespeichert als ${result.fileName}. Bitte mit genau diesem Dateinamen auf den USB-Stick kopieren und am Fernseher importieren.`, 'info');
      const state = JSON.parse(bridge.GetState());
      idle();
      await showLoaderMessages(result.messages);
      const keep = { index: current, sub };
      await applyState(state, true);
      if (keep.index < lists.length) { current = keep.index; sub = keep.sub; renderAll(); }
    } catch (err) {
      idle();
      await ui.info('Speichern fehlgeschlagen', err.message);
    } finally {
      idle();
    }
  }

  function download(bytes, fileName) {
    const url = URL.createObjectURL(new Blob([bytes], { type: 'application/octet-stream' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  // ---------------------------------------------------------------- Darstellung

  function renderAll() {
    renderTabs();
    renderRows();
    renderToolbar();
    $('btnSave').disabled = !data;
  }

  function renderFileInfo() {
    const details = [data.plugin, data.model, data.format && `Format ${data.format}`].filter(Boolean).join(' · ');
    $('fileInfo').innerHTML = `${escapeHtml(data.file.split('/').pop())}<span class="sub"> — ${escapeHtml(details)}</span>`;
    $('fileInfo').title = data.file;
    const guide = guideFor(data.plugin, data.file);
    $('guideLink').hidden = !guide;
    if (guide) $('guideLink').href = `anleitung/${guide}.html`;
    renderFilePanel();
  }

  /** Seitenleiste mit allen hochgeladenen Dateien, nach Ordnern gruppiert. */
  function renderFilePanel() {
    const panel = $('filePanel');
    if (uploadedPaths.length <= 1) {
      panel.hidden = true;
      return;
    }
    const related = new Set(data.dataFiles || []);
    const byDir = new Map();
    for (const p of [...uploadedPaths].sort((a, b) => a.localeCompare(b, 'de'))) {
      const i = p.lastIndexOf('/');
      const dir = i >= 0 ? p.slice(0, i) : '';
      if (!byDir.has(dir)) byDir.set(dir, []);
      byDir.get(dir).push(p);
    }

    // gemeinsamen Hauptordner einmal oben anzeigen, darunter nur die Unterordner
    const dirs = [...byDir.keys()];
    let root = dirs.reduce((a, b) => {
      const pa = a.split('/'), pb = b.split('/');
      let i = 0;
      while (i < pa.length && i < pb.length && pa[i] === pb[i]) i++;
      return pa.slice(0, i).join('/');
    });

    let html = `<div class="fp-head">Hochgeladene Dateien <span class="count">${uploadedPaths.length}</span></div>` +
      (root ? `<div class="fp-root" title="${escapeHtml(root)}">📂 ${escapeHtml(root)}</div>` : '') +
      `<p class="fp-hint">Die Senderliste wurde aus der markierten Datei geladen. Eine andere Datei anklicken, um sie stattdessen zu öffnen.</p>`;
    for (const [dir, files] of byDir) {
      const label = root ? dir.slice(root.length).replace(/^\//, '') : dir;
      if (label || byDir.size > 1)
        html += `<div class="fp-dir" title="${escapeHtml(dir)}">📁 ${escapeHtml(label || '(Hauptordner)')}</div>`;
      html += '<ul>';
      for (const p of files) {
        const active = p === data.file;
        const used = !active && related.has(p);
        const badge = active ? '<span class="fp-badge active">geöffnet</span>' : used ? '<span class="fp-badge used">gehört dazu</span>' : '';
        html += `<li><button class="fp-file${active ? ' active' : ''}${used ? ' used' : ''}" data-path="${escapeHtml(p)}" title="${escapeHtml(p)}">` +
          `<span class="fp-name">${escapeHtml(p.slice(p.lastIndexOf('/') + 1))}</span>${badge}</button></li>`;
      }
      html += '</ul>';
    }
    panel.innerHTML = html;
    panel.hidden = false;
  }

  function renderTabs() {
    $('tabsLabel').textContent = lists.length > 1 ? `${lists.length} Senderlisten` : 'Senderliste';
    $('tabs').innerHTML = lists.map((l, i) =>
      `<button type="button" role="tab" data-index="${i}" class="${i === current ? 'active' : ''}${l.readOnly ? ' readonly' : ''}" aria-selected="${i === current}"
        title="${l.readOnly ? 'Nur lesbar' : 'Diese Liste bearbeiten'}">${l.readOnly ? '🔒 ' : l.isFavList ? '★ ' : ''}${escapeHtml(l.isFavList ? 'Favoriten' : l.caption)}<span class="count">${l.order.length}</span></button>`).join('');

    // zweite Leiste: Hauptliste / Favoritenlisten der gewählten Liste
    const l = list();
    const show = l && hasFavViews(l);
    $('subSwitcher').hidden = !show;
    if (!show) return;
    const views = [{ k: 0, label: l.isFavList ? 'Alle Sender' : 'Senderliste', count: l.order.length }]
      .concat(l.favs.map((f, k) => ({ k: k + 1, label: favCaption(l, k), count: f.length })));
    $('subTabs').innerHTML = views.map((v) =>
      `<button type="button" role="tab" data-sub="${v.k}" class="${v.k === sub ? 'active' : ''}" aria-selected="${v.k === sub}"
        title="${v.k === 0 ? (l.isFavList ? 'Alle Sender, Favoriten per A/B/C/D an- und abwählen' : 'Hauptliste sortieren') : 'Diese Favoritenliste sortieren'}">${v.k > 0 ? '★ ' : ''}${escapeHtml(v.label)}<span class="count">${v.count}</span></button>`).join('');
  }

  function renderToolbar() {
    const l = list();
    const reorder = l && canReorder();
    $('listTools').hidden = showDeleted || !reorder;
    $('deletedTools').hidden = !showDeleted;
    const del = document.querySelector('.toolbar [data-action="delete"]');
    del.hidden = showDeleted || !reorder;
    del.textContent = sub === 0 ? 'Löschen' : 'Aus Favoriten entfernen';
    $('btnShowDeleted').hidden = !l || sub !== 0 || l.isFavList;
    $('btnShowDeleted').textContent = showDeleted ? '← Zurück zur Liste' : `Gelöschte (${l ? l.deleted.length : 0})`;
    for (const btn of document.querySelectorAll('.toolbar [data-action]'))
      btn.disabled = !editable() || (btn.dataset.action === 'undo' ? undoStack.length === 0 : false);
    const rename = document.querySelector('.toolbar [data-action="rename"]');
    rename.hidden = !l || !l.canRename;
    rename.disabled = !editable() || selection.size !== 1 || showDeleted;
  }

  function renderRows() {
    const l = list();
    const tbody = $('rows');
    if (!l) { tbody.innerHTML = ''; return; }

    const favCol = hasFavColumn(l) && !showDeleted;
    $('channelTable').classList.toggle('with-fav', favCol);
    const favSets = favCol ? l.favs.map((f) => new Set(f)) : [];
    const ids = showDeleted ? l.deleted : cur();
    const allView = sub === 0 && l.isFavList; // gemischte Favoritenliste, Ansicht "Alle Sender"
    const draggable = canReorder() && !filter;
    const start = curStart();
    const needle = filter.toLowerCase();
    const rows = [];
    for (let i = 0; i < ids.length; i++) {
      const ch = l.byId.get(ids[i]);
      const name = nameOf(l, ch);
      if (needle && !name.toLowerCase().includes(needle)) continue;
      const nr = showDeleted || allView ? '–' : start + i;
      const old = sub === 0 ? ch.oldNr : (ch.fav && ch.fav[sub - 1] >= 0 ? ch.fav[sub - 1] : -1);
      const src = [ch.satellite, ch.freq ? `${ch.freq} MHz` : ''].filter(Boolean).join(' · ');
      const chips = favCol
        ? `<td class="col-fav">${favSets.map((set, k) =>
          `<button type="button" class="fav-chip${set.has(ch.id) ? ' on' : ''}" data-fav="${k}" title="${escapeHtml(favCaption(l, k))}">${favLetter(k)}</button>`).join('')}</td>`
        : '<td class="col-fav"></td>';
      rows.push(`<tr data-id="${ch.id}" draggable="${draggable}" class="${selection.has(ch.id) ? 'selected' : ''}${ch.hidden ? ' hidden-ch' : ''}">` +
        `<td class="col-nr">${nr}</td>` +
        `<td class="col-old">${old >= 0 ? old : '–'}</td>` +
        `<td class="col-name${l.names.has(ch.id) ? ' renamed' : ''}"${l.names.has(ch.id) ? ` title="Bisher: ${escapeHtml(ch.name)}"` : ''}>${escapeHtml(name) || '<span class="muted">(ohne Namen)</span>'}</td>` +
        chips +
        `<td class="col-type"><span class="badge ${ch.type}">${TYPE_LABEL[ch.type]}</span></td>` +
        `<td class="col-enc">${ch.encrypted ? '🔒' : ''}</td>` +
        `<td class="col-src">${escapeHtml(src)}</td>` +
        `<td class="col-sid">${ch.sid || ''}</td></tr>`);
    }
    tbody.innerHTML = rows.join('');

    const empty = $('emptyHint');
    empty.hidden = rows.length > 0;
    empty.textContent = showDeleted ? 'Keine gelöschten Sender.'
      : filter ? 'Kein Sender gefunden.'
      : sub > 0 ? `${favCaption(l, sub - 1)} ist leer. Sender fügst du in der Ansicht „${l.isFavList ? 'Alle Sender' : 'Senderliste'}“ über die Schalter A, B, C … hinzu.`
      : 'Diese Liste ist leer.';

    renderStatus();
    renderToolbar();
  }

  function renderStatus() {
    const l = list();
    const o = cur();
    const tv = o.filter((id) => l.byId.get(id).type === 'tv').length;
    const radio = o.filter((id) => l.byId.get(id).type === 'radio').length;
    let text = sub > 0
      ? `${o.length} Sender in ${favCaption(l, sub - 1)} (${tv} TV, ${radio} Radio)`
      : `${o.length} Sender (${tv} TV, ${radio} Radio)` + (l.isFavList ? '' : ` · ${l.deleted.length} gelöscht`);
    if (l.names.size) text += ` · ${l.names.size} umbenannt`;
    if (selection.size) text += ` · ${selection.size} ausgewählt`;
    if (l.readOnly) text += ' · Diese Liste ist nur lesbar';
    else if (sub === 0 && l.isFavList) text += ' · Favoriten per A/B/C/D an- und abwählen, sortieren in den Favoritenansichten';
    else if (hasFavColumn(l)) text += ' · Favoriten per A/B/C/D an- und abwählen';
    if (filter && !showDeleted && canReorder()) text += ' · Verschieben per Ziehen ist während der Suche deaktiviert';
    $('statusbar').textContent = text;
  }

  function scrollToId(id) {
    const row = document.querySelector(`#rows tr[data-id="${id}"]`);
    if (row) row.scrollIntoView({ block: 'nearest' });
  }

  function showNotice(text, kind = 'warn') {
    const n = $('notice');
    n.textContent = text;
    n.classList.toggle('info', kind === 'info');
    n.hidden = false;
  }

  function hideNotice() { $('notice').hidden = true; }

  /** Technische Hinweise des Loaders zugeklappt anzeigen, damit sie nicht wie ein Fehler wirken. */
  function showWarnings(text) {
    const lines = text.split('\n').filter((l) => l.trim());
    const n = $('notice');
    n.classList.remove('info');
    n.innerHTML = `<details><summary>${lines.length} technische ${lines.length === 1 ? 'Hinweis' : 'Hinweise'} beim Laden (meist unkritisch, z. B. doppelte Nummern bei gelöschten Sendern)</summary>` +
      `<pre class="warnings">${escapeHtml(lines.join('\n'))}</pre></details>`;
    n.hidden = false;
  }

  function busy(text) {
    $('overlayText').textContent = text;
    $('overlay').hidden = false;
  }

  function idle() { $('overlay').hidden = true; }

  // ---------------------------------------------------------------- Ereignisse

  // Datei-Auswahl
  $('fileInput').addEventListener('change', (e) => {
    loadEntries([...e.target.files].map((file) => ({ path: file.name, file })));
    e.target.value = '';
  });
  $('folderInput').addEventListener('change', (e) => {
    loadEntries([...e.target.files].map((file) => ({ path: file.webkitRelativePath || file.name, file })));
    e.target.value = '';
  });

  // Drag & Drop von Dateien/Ordnern auf die Startseite (oder später auf das ganze Fenster)
  const dropZone = $('dropZone');
  for (const target of [dropZone, document.body]) {
    target.addEventListener('dragover', (e) => {
      if (!e.dataTransfer.types.includes('Files')) return;
      e.preventDefault();
      dropZone.classList.add('over');
    });
    target.addEventListener('dragleave', () => dropZone.classList.remove('over'));
    target.addEventListener('drop', async (e) => {
      if (!e.dataTransfer.types.includes('Files')) return;
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('over');
      loadEntries(await collectDroppedFiles(e.dataTransfer));
    });
  }

  $('btnNew').addEventListener('click', async () => {
    if (isDirty() && !await ui.confirm('Andere Datei öffnen?', 'Ungespeicherte Änderungen gehen verloren.', 'Fortfahren')) return;
    data = null;
    lists = [];
    $('editorView').hidden = true;
    $('startView').hidden = false;
    $('btnSave').disabled = true;
  });

  $('btnSave').addEventListener('click', save);

  $('filePanel').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-path]');
    if (btn) openSpecificFile(btn.dataset.path);
  });

  $('tabs').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-index]');
    if (!btn) return;
    current = Number(btn.dataset.index);
    sub = defaultSub(list());
    selection.clear();
    showDeleted = false;
    renderAll();
  });

  $('subTabs').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-sub]');
    if (!btn) return;
    sub = Number(btn.dataset.sub);
    selection.clear();
    showDeleted = false;
    renderAll();
  });

  $('search').addEventListener('input', (e) => {
    filter = e.target.value.trim();
    renderRows();
  });

  $('btnShowDeleted').addEventListener('click', () => {
    showDeleted = !showDeleted;
    selection.clear();
    renderRows();
  });

  document.querySelector('.toolbar').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn || btn.disabled) return;
    const actions = {
      top: () => moveSelectedTo(0),
      bottom: () => moveSelectedTo(cur().length),
      up: () => moveStep(-1),
      down: () => moveStep(1),
      moveTo: moveToPosition,
      rename: renameSelected,
      delete: deleteSelected,
      restore: restoreSelected,
      undo,
    };
    actions[btn.dataset.action]?.();
  });

  // Auswahl per Klick, Strg+Klick und Umschalt+Klick
  const tbody = $('rows');
  tbody.addEventListener('click', (e) => {
    const row = e.target.closest('tr[data-id]');
    if (!row) return;
    const chip = e.target.closest('.fav-chip');
    if (chip) {
      toggleFavorite(Number(row.dataset.id), Number(chip.dataset.fav));
      return;
    }
    const id = Number(row.dataset.id);
    if (e.shiftKey && anchorId !== null) {
      const visible = [...tbody.querySelectorAll('tr[data-id]')].map((r) => Number(r.dataset.id));
      const b = visible.indexOf(id);
      const a = visible.includes(anchorId) ? visible.indexOf(anchorId) : b;
      if (!e.ctrlKey && !e.metaKey) selection.clear();
      for (let i = Math.min(a, b); i <= Math.max(a, b); i++) selection.add(visible[i]);
    } else if (e.ctrlKey || e.metaKey) {
      selection.has(id) ? selection.delete(id) : selection.add(id);
      anchorId = id;
    } else {
      selection.clear();
      selection.add(id);
      anchorId = id;
    }
    updateSelectionClasses();
  });

  tbody.addEventListener('dblclick', (e) => {
    const row = e.target.closest('tr[data-id]');
    if (!row || !editable() || showDeleted || e.target.closest('.fav-chip')) return;
    selection.clear();
    selection.add(Number(row.dataset.id));
    updateSelectionClasses();
    if (e.target.closest('.col-name') && list().canRename) renameSelected();
    else if (canReorder()) moveToPosition();
  });

  function updateSelectionClasses() {
    for (const row of tbody.querySelectorAll('tr[data-id]'))
      row.classList.toggle('selected', selection.has(Number(row.dataset.id)));
    renderStatus();
    renderToolbar();
  }

  // Sender per Drag & Drop verschieben
  let dropTarget = null;
  tbody.addEventListener('dragstart', (e) => {
    const row = e.target.closest('tr[data-id]');
    if (!row) return;
    const id = Number(row.dataset.id);
    if (!selection.has(id)) {
      selection.clear();
      selection.add(id);
      anchorId = id;
      updateSelectionClasses();
    }
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/x-channel', String(id));
  });
  tbody.addEventListener('dragover', (e) => {
    if (!e.dataTransfer.types.includes('text/x-channel')) return;
    e.preventDefault();
    const row = e.target.closest('tr[data-id]');
    clearDropMarker();
    if (!row) return;
    const after = e.clientY > row.getBoundingClientRect().top + row.offsetHeight / 2;
    row.classList.add(after ? 'drop-after' : 'drop-before');
    dropTarget = { id: Number(row.dataset.id), after };
  });
  tbody.addEventListener('dragleave', (e) => {
    if (!tbody.contains(e.relatedTarget)) clearDropMarker();
  });
  tbody.addEventListener('drop', (e) => {
    if (!e.dataTransfer.types.includes('text/x-channel') || !dropTarget) return;
    e.preventDefault();
    e.stopPropagation();
    const index = cur().indexOf(dropTarget.id) + (dropTarget.after ? 1 : 0);
    clearDropMarker();
    moveSelectedTo(index);
  });
  tbody.addEventListener('dragend', clearDropMarker);

  function clearDropMarker() {
    for (const row of tbody.querySelectorAll('.drop-before, .drop-after'))
      row.classList.remove('drop-before', 'drop-after');
    dropTarget = null;
  }

  // Tastatur
  document.addEventListener('keydown', (e) => {
    if ($('editorView').hidden || $('dialog').open || e.target.matches('input, select, textarea')) return;
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); }
    else if (ctrl && e.key.toLowerCase() === 'a') {
      e.preventDefault();
      for (const row of tbody.querySelectorAll('tr[data-id]')) selection.add(Number(row.dataset.id));
      updateSelectionClasses();
    }
    else if (!editable()) return;
    else if (e.key === 'Delete' && canReorder()) deleteSelected();
    else if (e.key === 'F2') { e.preventDefault(); renameSelected(); }
    else if (!canReorder()) return;
    else if (e.altKey && e.key === 'ArrowUp') { e.preventDefault(); moveStep(-1); }
    else if (e.altKey && e.key === 'ArrowDown') { e.preventDefault(); moveStep(1); }
    else if (e.key === 'Home' && selection.size) { e.preventDefault(); moveSelectedTo(0); }
    else if (e.key === 'End' && selection.size) { e.preventDefault(); moveSelectedTo(cur().length); }
  });

  window.addEventListener('beforeunload', (e) => {
    if (isDirty()) { e.preventDefault(); e.returnValue = ''; }
  });
}

// ---------------------------------------------------------------- Dialoge

/**
 * Eigene Dialoge im Stil eines macOS-Hinweisfensters (statt alert/confirm/prompt des Browsers).
 * Alle Funktionen liefern ein Promise.
 */
function createDialogs() {
  const dlg = $('dialog');
  const title = $('dialogTitle');
  const message = $('dialogMessage');
  const input = $('dialogInput');
  const buttons = $('dialogButtons');
  let resolveCurrent = null;
  let cancelValue = null;

  dlg.addEventListener('cancel', (e) => { e.preventDefault(); finish(cancelValue); });
  $('dialogForm').addEventListener('submit', (e) => e.preventDefault());

  function finish(value) {
    if (!resolveCurrent) return;
    const r = resolveCurrent;
    resolveCurrent = null;
    dlg.close();
    r(value);
  }

  /** buttons: [{ label, value, primary, danger }]; Enter löst den primären Knopf aus. */
  function open({ heading, text, options, cancel, withInput }) {
    title.textContent = heading || '';
    message.textContent = text || '';
    message.hidden = !text;
    input.hidden = !withInput;
    buttons.innerHTML = '';
    buttons.classList.toggle('row', options.length <= 2 && options.every((o) => o.label.length < 18));
    cancelValue = cancel;
    for (const o of options) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn' + (o.primary ? ' btn-primary' : '') + (o.danger ? ' btn-danger' : '');
      b.textContent = o.label;
      b.addEventListener('click', () => finish(typeof o.value === 'function' ? o.value() : o.value));
      buttons.appendChild(b);
    }
    return new Promise((resolve) => {
      resolveCurrent = resolve;
      dlg.showModal();
      (withInput ? input : buttons.querySelector('.btn-primary') || buttons.firstChild)?.focus();
    });
  }

  return {
    info: (heading, text) => open({ heading, text, options: [{ label: 'OK', value: true, primary: true }], cancel: true }),

    confirm: (heading, text, okLabel = 'OK') => open({
      heading, text, cancel: false,
      options: [{ label: 'Abbrechen', value: false }, { label: okLabel, value: true, primary: true }],
    }),

    /** Auswahl aus den Optionen eines Loaders; liefert den Index oder -1. */
    choose: (heading, text, options) => open({
      heading: heading || 'Rückfrage', text, cancel: -1,
      options: options.map((label, i) => ({ label, value: i, primary: i === 0 })),
    }),

    askText: (heading, text, value, maxLength) => {
      input.type = 'text';
      input.removeAttribute('min');
      input.removeAttribute('max');
      if (maxLength > 0) input.maxLength = maxLength; else input.removeAttribute('maxlength');
      input.value = value;
      const read = () => input.value;
      input.onkeydown = (e) => { if (e.key === 'Enter') { e.preventDefault(); finish(read()); } };
      const p = open({
        heading, text, cancel: null, withInput: true,
        options: [{ label: 'Abbrechen', value: null }, { label: 'Umbenennen', value: read, primary: true }],
      });
      input.select();
      return p;
    },

    askNumber: (heading, text, value, min, max) => {
      input.type = 'number';
      input.removeAttribute('maxlength');
      input.value = value;
      input.min = min;
      input.max = max;
      const read = () => { const n = parseInt(input.value, 10); return Number.isInteger(n) ? n : null; };
      input.onkeydown = (e) => { if (e.key === 'Enter') { e.preventDefault(); finish(read()); } };
      return open({
        heading, text, cancel: null, withInput: true,
        options: [{ label: 'Abbrechen', value: null }, { label: 'Verschieben', value: read, primary: true }],
      });
    },
  };
}

// ---------------------------------------------------------------- Hell / Dunkel

/** Passende Anleitungsseite (anleitung/<name>.html) zum erkannten Loader bzw. Dateinamen. */
function guideFor(plugin, file) {
  const p = (plugin || '').toLowerCase();
  const f = (file || '').toLowerCase();
  const rules = [
    ['samsung', 'samsung'], ['lg ', 'lg'], ['lg(', 'lg'], ['sony', 'sony'], ['philips', 'philips'],
    ['panasonic', 'panasonic'], ['tcl', 'tcl'], ['hisense', 'hisense'], ['grundig', 'grundig'],
    ['sharp', 'sharp'], ['cmdb', 'sharp'], ['toshiba', 'toshiba'], ['satcodx', 'telefunken-medion'],
    ['medion', 'telefunken-medion'], ['loewe', 'loewe'], ['enigma2', 'receiver'], ['vdr', 'receiver'],
    ['m3u', 'receiver'], ['dbm', 'receiver'], ['dvbviewer', 'receiver'], ['vision edge', 'receiver'], ['chmax', 'receiver'],
  ];
  for (const [key, slug] of rules) if (p.startsWith(key) || p.includes(key)) return slug;
  if (/\.tll$/.test(f)) return 'lg';
  if (f.includes('philipschannelmaps') || f.includes('/repair/')) return 'philips';
  return null;
}

function initThemeSwitch() {
  const toggle = $('themeToggle');
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
}

// ---------------------------------------------------------------- Hilfsfunktionen

function toBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk)
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  return btoa(binary);
}

function fromBase64(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

function escapeHtml(text) {
  return String(text ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const nextFrame = () => new Promise((r) => setTimeout(r, 30));

/** Liest gezogene Dateien und Ordner (rekursiv) mit relativem Pfad ein. */
async function collectDroppedFiles(dataTransfer) {
  const entries = [...dataTransfer.items].map((item) => item.webkitGetAsEntry?.()).filter(Boolean);
  if (entries.length === 0)
    return [...dataTransfer.files].map((file) => ({ path: file.name, file }));

  const result = [];
  async function walk(entry, prefix) {
    if (entry.isFile) {
      const file = await new Promise((res, rej) => entry.file(res, rej));
      result.push({ path: prefix + file.name, file });
    } else if (entry.isDirectory) {
      const reader = entry.createReader();
      let batch;
      do {
        batch = await new Promise((res, rej) => reader.readEntries(res, rej));
        for (const child of batch) await walk(child, prefix + entry.name + '/');
      } while (batch.length > 0);
    }
  }
  for (const entry of entries) await walk(entry, '');
  return result;
}
