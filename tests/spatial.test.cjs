'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {validPoint, prepare} = require('../public/spatial.js');
test('native coordinates include boundary points and reject absent or malformed positions', () => {
  for (const p of [[0,0], [120,80], [27.5,42]]) assert.equal(validPoint(p), true);
  for (const p of [null, [], [0], [null,40], ['20',40], [NaN,0], [Infinity,0], [-1,0], [121,40], [20,81]]) assert.equal(validPoint(p), false);
});
test('pass endpoints must be supported independently; omissions never become zero coordinates', () => {
  const events = [
    {id:'shot',type:{name:'Shot'},location:[100,30]},
    {id:'pass',type:{name:'Pass'},location:[25,20],pass:{end_location:[45,30]}},
    {id:'missing',type:{name:'Pass'},location:[25,20],pass:{}},
    {id:'outside',type:{name:'Shot'},location:[121,40]},
    {id:'start',type:{name:'Half Start'}}
  ];
  const before=JSON.stringify(events);
  const r=prepare(events,['Pass','Shot']);
  assert.deepEqual(r.events.map(e=>e.id),['shot','pass']);
  assert.equal(r.unavailable,2);
  assert.equal(JSON.stringify(events),before);
  assert.deepEqual(r.events[1].location,[25,20]);
  assert.deepEqual(r.events[1].pass.end_location,[45,30]);
  assert.deepEqual(prepare(events,['Shot']).events.map(e=>e.id),['shot']);
});
test('provider order, original IDs and both teams retain their native coordinate frame', () => {
  const rows=[901,902].map((team,i)=>({id:`original-${i}`,index:i+1,team:{id:team},type:{name:'Shot'},location:[95,32]}));
  const r=prepare(rows,['Shot']);
  assert.deepEqual(r.events.map(e=>e.id),['original-0','original-1']);
  assert.deepEqual(r.events.map(e=>e.location),[[95,32],[95,32]]);
  assert.equal(r.unavailable,0);
});
