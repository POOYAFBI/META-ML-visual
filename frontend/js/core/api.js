async function api(path, options){ const r = await fetch(path, options); if(!r.ok) throw new Error(await r.text()); return r.json(); }
function params(){ return `task=${$('task').value}&dataset=${$('dataset').value}&model=${$('model').value}`; }
function destroy(name){ if(charts[name]) charts[name].destroy(); }
function activeMode(){ return $('inputMode').value; }
function currentTask(){ return $('task').value; }
