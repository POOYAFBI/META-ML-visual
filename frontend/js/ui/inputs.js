function formatSummaryValue(item){
  if(item.name === 'Actual SalePrice') return formatMoney(item.value);
  if(String(item.name || '').startsWith('Neighborhood_')) return item.value;
  return formatNumber(item.value);
}
function renderPreviewCard(targetId, item, emptyText){
  if(!item){ $(targetId).innerHTML = `<p class="muted">${escapeHtml(emptyText)}</p>`; return; }
  const summary = (item.summary || []).slice(0, 6).map(x=>`
    <li><b>${escapeHtml(x.label)}</b><span>${escapeHtml(formatSummaryValue(x))}</span><small>${escapeHtml(x.name)}</small></li>`).join('');
  $(targetId).innerHTML = `<h3>${escapeHtml(item.label)}</h3><p>${escapeHtml(item.description || 'این انتخاب یک بردار کامل ویژگی برای مدل می‌سازد.')}</p><ul class="summary-list">${summary}</ul>`;
}
function renderPresetPreview(){ renderPreviewCard('presetPreview', currentPresets.find(p=>p.id===$('preset').value) || currentPresets[0], 'برای این انتخاب پریستی وجود ندارد.'); }
function renderSamplePreview(){ renderPreviewCard('samplePreview', currentSamples.find(s=>s.id===$('sample').value) || currentSamples[0], 'نمونه‌ای برای نمایش وجود ندارد.'); }
function groupedFeatures(features){
  const oneHotGroups = {};
  const groups = {};
  features.forEach(f=>{
    if(f.inputKind === 'oneHotOption'){ (oneHotGroups[f.oneHotGroup] ||= []).push(f); return; }
    (groups[f.group || 'featureهای فنی'] ||= []).push(f);
  });
  Object.entries(oneHotGroups).forEach(([groupName, opts])=>{
    const group = opts[0]?.group || 'featureهای فنی';
    (groups[group] ||= []).push({kind:'oneHotSelect', name:groupName, labelFa: groupName === 'Neighborhood' ? 'محله' : groupName, rawName: groupName, options: opts});
  });
  return groups;
}
function renderAdvancedForm(features){
  const order = ['مشخصات کلی','مساحت‌ها','کیفیت و وضعیت','محله','امکانات','featureهای فنی'];
  const groups = groupedFeatures(features);
  $('form').innerHTML = order.filter(g=>groups[g]?.length).map(group=>`
    <section class="feature-group"><h3>${escapeHtml(group)}</h3><div class="feature-grid">${groups[group].map(f=>{
      if(f.kind === 'oneHotSelect') return `<label>${escapeHtml(f.labelFa)} <small>${escapeHtml(f.rawName)}</small><select data-onehot-group="${escapeHtml(f.name)}"><option value="">هیچ‌کدام / پایه</option>${f.options.map(o=>`<option value="${escapeHtml(o.rawName)}">${escapeHtml(o.oneHotValue)} (${escapeHtml(o.rawName)})</option>`).join('')}</select></label>`;
      return `<label>${escapeHtml(f.labelFa)} <small>${escapeHtml(f.rawName)}</small><input name="${escapeHtml(f.name)}" title="${escapeHtml(f.help || '')}" type="number" step="any" value="${escapeHtml(f.default ?? 0)}"></label>`;
    }).join('')}</div></section>`).join('');
}

async function loadOptions(){
  const data = await api('/api/options');
  function fill(){
    const task = $('task').value, cfg = data.tasks[task];
    $('dataset').innerHTML = cfg.datasets.map(d=>`<option value="${d.id}">${d.name}</option>`).join('');
    $('model').innerHTML = cfg.models.map(m=>`<option value="${m}">${modelLabel(m)}</option>`).join('');
  }
  $('task').onchange = () => { fill(); loadAll(); };
  $('dataset').onchange = loadAll; $('model').onchange = loadAll; $('inputMode').onchange = switchMode;
  fill(); await loadAll();
}

function switchMode(){
  const mode = activeMode();
  $('presetPanel').hidden = mode !== 'preset';
  $('samplePanel').hidden = mode !== 'dataset';
  $('advancedPanel').hidden = mode !== 'advanced';
}

async function loadAll(){
  const schema = await api('/api/features?'+params()); currentFeatures = schema.features;
  $('featureCount').textContent = `${currentFeatures.length} ویژگی کامل برای مدل انتخاب‌شده آماده می‌شود`;
  renderAdvancedForm(currentFeatures);

  currentPresets = (await api(`/api/presets?task=${$('task').value}&dataset=${$('dataset').value}`)).presets;
  $('preset').innerHTML = currentPresets.map(p=>`<option value="${escapeHtml(p.id)}">${escapeHtml(p.label)}</option>`).join('');
  renderPresetPreview();
  $('preset').onchange = renderPresetPreview;

  currentSamples = (await api('/api/samples?'+params()+'&limit=10')).samples;
  $('sample').innerHTML = currentSamples.map(s=>`<option value="${escapeHtml(s.id)}">${escapeHtml(s.label)}</option>`).join('');
  renderSamplePreview();
  $('sample').onchange = renderSamplePreview;

  const metrics = await api('/api/metrics?'+params());
  renderMetrics(metrics.metrics);
  switchMode(); await drawCharts();
}

