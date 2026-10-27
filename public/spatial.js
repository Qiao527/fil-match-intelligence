'use strict';
/* Native-coordinate event geometry only. No mirroring, interpolation or tracking. */
const FILSpatial = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  function validPoint(point) {
    return Array.isArray(point) && point.length >= 2 &&
      typeof point[0] === 'number' && typeof point[1] === 'number' &&
      Number.isFinite(point[0]) && Number.isFinite(point[1]) &&
      point[0] >= 0 && point[0] <= 120 && point[1] >= 0 && point[1] <= 80;
  }
  function prepare(events, kinds) {
    let unavailable = 0;
    const plotted = [];
    for (const event of events) {
      if (!kinds.includes(event.type?.name)) continue;
      if (!validPoint(event.location) ||
          (event.type.name === 'Pass' && !validPoint(event.pass?.end_location))) {
        unavailable++;
        continue;
      }
      plotted.push(event);
    }
    return {events: plotted, unavailable};
  }
  function node(tag, attrs = {}, text) {
    const n = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attrs)) n.setAttribute(key, String(value));
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function pitch(events, {activeId, onSelect, label = 'Recorded action locations'} = {}) {
    const svg = node('svg', {viewBox: '-5 -5 130 90', role: 'group', 'aria-label': label});
    const lines = node('g', {class: 'pitch-lines', 'aria-hidden': 'true'});
    lines.append(node('rect', {x: 0, y: 0, width: 120, height: 80}),
      node('path', {d: 'M60 0V80 M0 18H18V62H0 M120 18H102V62H120 M0 30H6V50H0 M120 30H114V50H120 M0 36H-2V44H0 M120 36H122V44H120'}),
      node('circle', {cx: 60, cy: 40, r: 10}), node('circle', {cx: 60, cy: 40, r: .4}),
      node('circle', {cx: 12, cy: 40, r: .4}), node('circle', {cx: 108, cy: 40, r: .4}));
    svg.append(lines);
    for (const e of events) {
      const [x, y] = e.location;
      const pass = e.type.name === 'Pass';
      const color = e.team?.id === 901 ? '#a9edc5' : '#f4bd82';
      const description = `#${e.index} ${e.type.name}, ${e.player?.name || 'Unknown player'}, ${e.id}`;
      const g = node('g', {'data-event-id': e.id,
        class: 'pitch-event' + (e.id === activeId ? ' is-active' : ''),
        ...(onSelect ? {tabindex: 0, role: 'button', 'aria-label': description,
          'aria-pressed': String(e.id === activeId)} : {})});
      g.append(node('title', {}, description));
      if (pass) {
        const [ex, ey] = e.pass.end_location;
        g.append(node('path', {d: `M${x} ${y}L${ex} ${ey}`, stroke: color,
          'stroke-width': .55, fill: 'none', class: 'mark',
          ...('outcome' in e.pass ? {'stroke-dasharray': '1.3 1'} : {})}));
        const angle = Math.atan2(ey - y, ex - x), size = 1.8;
        if (ex !== x || ey !== y) g.append(node('path', {
          d: `M${ex - size * Math.cos(angle - .5)} ${ey - size * Math.sin(angle - .5)}L${ex} ${ey}L${ex - size * Math.cos(angle + .5)} ${ey - size * Math.sin(angle + .5)}`,
          stroke: color, 'stroke-width': .55, fill: 'none', class: 'mark'}));
        g.append(node('circle', {cx: x, cy: y, r: .7, fill: color, class: 'mark'}));
      } else {
        g.append(node('circle', {cx: x, cy: y, r: 1.65, stroke: color, 'stroke-width': .6,
          fill: e.shot?.outcome?.name === 'Goal' ? color : '#122d2b', class: 'mark'}));
      }
      if (e.id === activeId) g.append(node('circle', {cx: x, cy: y, r: 3,
        fill: 'none', stroke: '#fff', 'stroke-width': .45}));
      if (onSelect) {
        g.append(node('circle', {cx: x, cy: y, r: 3.1, fill: 'transparent',
          stroke: 'transparent', class: 'hit-target'}));
        g.onclick = () => onSelect(e.id);
        g.onkeydown = event => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault(); onSelect(e.id);
            document.querySelector('#pitch [data-event-id="' + CSS.escape(e.id) + '"]')?.focus();
          }
        };
      }
      svg.append(g);
    }
    return svg;
  }
  return {validPoint, prepare, pitch};
})();
if (typeof module !== 'undefined') module.exports = FILSpatial;
