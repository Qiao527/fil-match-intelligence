'use strict';
const $ = id => document.getElementById(id);
let data = null, scope = null, controller = null, version = 0, hasRun = false;
let layer = 'shots', sequenceIds = null, activeId = null, selectedCard = null;
function el(tag, text, cls) {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (cls) n.className = cls;
  return n;
}
function names() {return {901: data.match.home_team.home_team_name, 902: data.match.away_team.away_team_name};}
function tab(id) {
  for (const x of ['report', 'evidence', 'baseline']) $(x).hidden = x !== id;
  document.querySelectorAll('[data-tab]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.tab === id)));
}
document.querySelectorAll('[data-tab]').forEach(b => b.onclick = () => tab(b.dataset.tab));
function inspect(ids, focusId) {
  scope = new Set(ids); $('search').value = ''; tab('evidence'); events();
  if (focusId && scope.has(focusId)) {$('event').value = focusId; raw();}
  $('evidence').scrollIntoView({block: 'start'});
}
function events() {
  const q = $('search').value.toLowerCase();
  const rows = data.events.filter(e => scope.has(e.id) && JSON.stringify([e.id, e.type.name, e.player?.name]).toLowerCase().includes(q));
  $('event').replaceChildren(...rows.map(e => {
    const n = el('option', `#${e.index} · P${e.period} ${e.timestamp} · ${e.type.name} · ${e.player?.name || 'Team record'}`);
    n.value = e.id; return n;
  }));
  $('event-count').textContent = `${rows.length} original actions · source order retained`;
  $('evidence-scope').textContent = 'Selection or opened sequence context. Sequence context can include actions outside the foreground team filter.';
  raw();
}
function raw() {
  const e = data.events.find(e => e.id === $('event').value);
  $('raw').textContent = e ? JSON.stringify(e, null, 2) : 'No actions match this selection.';
}
$('search').oninput = events; $('event').onchange = raw;
function spatialRows() {
  const ids = new Set(layer === 'sequence' && sequenceIds ? sequenceIds : data.report.selected_event_ids);
  return data.events.filter(e => ids.has(e.id));
}
function selectAction(id) {activeId = id; drawPitch();}
function drawPitch() {
  if (!data) return;
  const rows = spatialRows();
  const kinds = layer === 'shots' ? ['Shot'] : layer === 'passes' ? ['Pass'] : ['Pass', 'Shot'];
  const prepared = FILSpatial.prepare(rows, kinds);
  if (!rows.some(e => e.id === activeId)) activeId = null;
  $('pitch').replaceChildren(FILSpatial.pitch(prepared.events, {activeId, onSelect: selectAction}));
  $('pitch-title').textContent = layer === 'shots' ? 'Recorded shot locations' : layer === 'passes' ? 'Recorded pass endpoints' : sequenceIds ? 'One recorded sequence' : 'Selected actions, in source order';
  const sequenceContext = layer === 'sequence' && sequenceIds;
  $('pitch-note').textContent = `${prepared.events.length} plotted actions · ${prepared.unavailable} missing or invalid coordinates omitted. ` +
    (sequenceContext ? 'Whole native-membership context; may include actions outside the team filter. ' : 'Current match, period and team selection. ') +
    (layer === 'passes' ? 'Dashed passes have a recorded or unresolved outcome. ' : '') +
    'Coincident markers overlap; every action remains in Original evidence. ' +
    (!prepared.events.length ? 'No plottable events in this layer.' : 'Choose a marker or review sequence to inspect its source.');
  document.querySelectorAll('[data-layer]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.layer === layer)));
  $('sequence-controls').hidden = layer !== 'sequence';
  if (layer === 'sequence') {
    const i = rows.findIndex(e => e.id === activeId);
    $('step-label').textContent = rows.length ? `${i < 0 ? 0 : i + 1} / ${rows.length} source actions · discrete steps, not tracking` : 'No actions in this selection';
    $('previous').disabled = i <= 0;
    $('next').disabled = !rows.length || i >= rows.length - 1;
    $('action-strip').replaceChildren(...rows.map(e => {
      const b = el('button', `#${e.index} ${e.type.name}`);
      b.setAttribute('aria-pressed', String(e.id === activeId));
      b.onclick = () => selectAction(e.id); return b;
    }));
  }
  const e = data.events.find(e => e.id === activeId);
  $('action-detail').hidden = !e;
  if (e) {
    $('action-title').textContent = `#${e.index} · ${e.type.name} · ${e.player?.name || 'Team record'}`;
    const point = FILSpatial.validPoint(e.location) ? `[${e.location.slice(0, 2).join(', ')}]` : 'Unavailable';
    const endpoint = e.type.name === 'Pass' ? (FILSpatial.validPoint(e.pass?.end_location) ? ` → [${e.pass.end_location.slice(0, 2).join(', ')}]` : ' → Unavailable') : '';
    $('action-coordinates').textContent = `Period ${e.period} · source timestamp ${e.timestamp} · ${point}${endpoint}`;
    $('action-id').textContent = e.id;
    $('open-original').onclick = () => inspect(rows.map(x => x.id), e.id);
  }
}
for (const b of document.querySelectorAll('[data-layer]')) b.onclick = () => {
  layer = b.dataset.layer; activeId = null; drawPitch();
};
for (const [id, step] of [['previous', -1], ['next', 1]]) $(id).onclick = () => {
  const rows = spatialRows(), i = rows.findIndex(e => e.id === activeId);
  const next = rows[i + step]; if (next) selectAction(next.id);
};
function viewSequence(card, index) {
  selectedCard = index; sequenceIds = card.unit.context_event_ids; layer = 'sequence'; activeId = sequenceIds[0] || null;
  document.querySelectorAll('.card').forEach((n, i) => n.classList.toggle('is-selected', i === selectedCard));
  drawPitch(); tab('report'); $('pitch-title').scrollIntoView({block: 'nearest'});
}
function comparisons() {
  const r = data.report, n = names(), ids = new Set(r.selected_event_ids);
  $('team-comparison').replaceChildren(...[901, 902].map(team => {
    const panel = el('article', undefined, 'comparison-team');
    panel.append(el('h3', n[team]));
    const rows = data.events.filter(e => ids.has(e.id) && e.team?.id === team);
    const prepared = FILSpatial.prepare(rows, ['Shot']);
    panel.append(FILSpatial.pitch(prepared.events, {label: n[team] + ' shot locations'}));
    const totals = r.team_totals.find(t => t.team_id === team);
    panel.append(el('p', r.selection.team_id && r.selection.team_id !== team ? 'Excluded by current team filter.' :
      `${totals.shot_count} Shots · ${totals.shot_weight === null ? 'Unavailable' : totals.shot_weight} illustrative weight · ${prepared.unavailable} unplottable locations`));
    return panel;
  }));
}
function render() {
  const r = data.report, n = names();
  layer = 'shots'; sequenceIds = null; activeId = null; selectedCard = null;
  $('fixture').textContent = `${n[901]}  ${r.score.join(' – ')}  ${n[902]}`;
  $('scope').textContent = `Full-match score · ${$('period').selectedOptions[0].textContent} · ${$('team').selectedOptions[0].textContent}`;
  $('home-legend').textContent = n[901]; $('away-legend').textContent = n[902];
  $('metrics').replaceChildren(...[['Selected actions', r.selected_event_count], ['Recorded Shots', r.shot_count],
    ['Illustrative shot weight', r.shot_weight === null ? 'Unavailable' : Number(r.shot_weight).toFixed(3)],
    ['Completed passes', r.completed_pass_count]].map(([k, v]) => {
    const m = el('div', undefined, 'metric'); m.append(el('span', k), el('strong', String(v))); return m;
  }));
  $('cards').replaceChildren();
  if (r.abstention) $('cards').append(el('p', r.abstention, 'annotation'));
  r.review_cards.forEach((c, i) => {
    const a = el('article', undefined, 'card');
    a.append(el('p', `0${i + 1} / ${n[c.unit.team_id]} / PERIOD ${c.unit.period}`, 'eyebrow'),
      el('h3', `Native sequence ${c.unit.possession_id}`),
      el('p', `${c.unit.shot_weight} weight · ${c.unit.shot_count} Shot${c.unit.shot_count === 1 ? '' : 's'}`, 'card-number'));
    const buttons = el('div', undefined, 'card-actions');
    const view = el('button', 'View sequence ↗', 'view-sequence'); view.onclick = () => viewSequence(c, i);
    const inspectButton = el('button', 'Inspect original actions'); inspectButton.onclick = () => inspect(c.unit.context_event_ids);
    buttons.append(view, inspectButton); a.append(buttons);
    const d = el('details'); d.append(el('summary', 'Interpretation & counterevidence'), el('p', c.observation),
      el('p', `Other selected Shots: ${c.unit.complement_event_ids.length}. Complement home−away weight: ${c.unit.complement_difference}. Deleting records is accounting, not a counterfactual match.`),
      el('p', 'Untested review question: ' + c.question));
    c.alternatives.forEach(t => d.append(el('p', t)));
    d.append(el('p', 'Value falsifier: ' + c.falsifier));
    const cb = el('button', 'Inspect comparison Shots'); cb.onclick = () => inspect(c.unit.complement_event_ids);
    d.append(cb); a.append(d); $('cards').append(a);
  });
  function table(id, rows) {$(id).replaceChildren(...rows.map(row => {const tr = el('tr'); row.forEach(v => tr.append(el('td', String(v)))); return tr;}));}
  table('totals', r.team_totals.map(t => [n[t.team_id], t.shot_count, t.shot_weight]));
  table('units', r.native_units.map(u => [n[u.team_id], u.period, u.possession_id, u.shot_count, u.shot_weight, u.complement_difference]));
  $('standards').replaceChildren(...Object.entries(r.claim_standards).map(([k, v]) => {const p = el('p'); p.append(el('strong', k + '. '), document.createTextNode(v)); return p;}));
  $('limits').replaceChildren(...r.limitations.map(t => el('li', t)));
  $('provenance').textContent = JSON.stringify({version: r.version, definitions: r.definitions, source: r.provenance}, null, 2);
  scope = new Set(r.selected_event_ids); events(); drawPitch(); comparisons(); chart(r, n); $('result').hidden = false;
  document.body.classList.add('has-report');
}
function chart(r, n) {
  const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 560 230'); svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'Cumulative illustrative shot weights by original action index');
  if (r.shot_weight === null) {$('chart').replaceChildren(el('p', 'Unavailable: missing source shot weights.')); return;}
  const max = Math.max(1, ...r.team_totals.map(t => Number(t.shot_weight))), last = Math.max(1, ...r.shots.map(s => s.index));
  [901, 902].forEach((team, k) => {
    let sum = 0; const pts = ['30,190'];
    r.shots.filter(s => s.team_id === team).forEach(s => {
      const x = 30 + s.index / last * 500; pts.push(`${x},${190 - sum / max * 140}`);
      sum += Number(s.weight); pts.push(`${x},${190 - sum / max * 140}`);
    });
    const p = document.createElementNS(ns, 'polyline');
    for (const [a, v] of Object.entries({points: pts.join(' '), fill: 'none', stroke: ['#a9edc5', '#f4bd82'][k], 'stroke-width': '3'})) p.setAttribute(a, v);
    const t = document.createElementNS(ns, 'text');
    for (const [a, v] of Object.entries({x: '30', y: String(18 + k * 20), fill: ['#a9edc5', '#f4bd82'][k], 'font-size': '12'})) t.setAttribute(a, v);
    t.textContent = n[team]; svg.append(p, t);
  }); $('chart').replaceChildren(svg);
}
async function run() {
  hasRun = true; const v = ++version; controller?.abort(); controller = new AbortController();
  $('run').disabled = true; $('result').hidden = true; $('status').textContent = 'Computing source-checked analysis…'; const t = performance.now();
  try {
    const q = new URLSearchParams({match: $('match').value});
    for (const k of ['period', 'team']) if ($(k).value) q.set(k, $(k).value);
    const res = await fetch('/api/analyze?' + q, {signal: controller.signal});
    if (!res.ok) throw Error('The analysis service could not complete this selection. Please retry.');
    const next = await res.json(); if (v !== version) return;
    data = next; render(); tab('report');
    $('status').textContent = `Analysis complete · ${((performance.now() - t) / 1000).toFixed(2)}s request and rendering · synthetic records only`;
  } catch (e) {if (e.name !== 'AbortError' && v === version) $('status').textContent = e.message;}
  finally {if (v === version) $('run').disabled = false;}
}
$('run').onclick = run;
for (const id of ['period', 'team']) $(id).onchange = () => {if (hasRun) run();};
$('match').onchange = () => {
  version++; controller?.abort(); data = null; hasRun = false; $('result').hidden = true;
  $('period').value = ''; $('team').value = ''; $('run').disabled = false; teams();
  $('status').textContent = 'Match changed. Run analysis to compute a new report.';
};
function teams() {
  const text = $('match').selectedOptions[0].textContent.split(' vs ');
  $('team').replaceChildren(...[['', 'Both teams'], ['901', text[0]], ['902', text[1]]].map(([v, t]) => {const n = el('option', t); n.value = v; return n;}));
}
fetch('/api/matches').then(r => {if (!r.ok) throw Error(); return r.json();}).then(ms => {
  $('match').replaceChildren(...ms.map(m => {const n = el('option', `${m.home} vs ${m.away}`); n.value = m.id; return n;}));
  teams(); $('match').disabled = false; $('run').disabled = false; $('status').textContent = 'Choose a match, then run the analysis.';
}).catch(() => {
  $('match').replaceChildren(el('option', 'Matches unavailable')); $('match').disabled = true;
  $('run').disabled = true; $('status').textContent = 'Could not load matches. Reload to retry.';
});
