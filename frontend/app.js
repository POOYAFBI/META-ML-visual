const $ = id => document.getElementById(id);
let charts = {}, currentFeatures = [], currentPresets = [], currentSamples = [], vizState = null, lastPrediction = null;
const modelDisplay = {
  linear_regression: {labelFa: 'رگرسیون خطی', labelEn: 'Linear Regression', raw: 'linear_regression', short: 'Linear'},
  logistic_regression: {labelFa: 'رگرسیون لجستیک', labelEn: 'Logistic Regression', raw: 'logistic_regression', short: 'Logistic'},
  random_forest: {labelFa: 'جنگل تصادفی', labelEn: 'Random Forest', raw: 'random_forest', short: 'RF'},
  xgboost: {labelFa: 'ایکس‌جی‌بوست', labelEn: 'XGBoost', raw: 'xgboost', short: 'XGBoost'}
};
const faModel = modelDisplay;
const datasetDisplay = {
  baseline_dataset: {labelFa: 'دیتاست پایه', labelEn: 'baseline_dataset', raw: 'baseline_dataset', short: 'Baseline'},
  enhanced_dataset: {labelFa: 'دیتاست ویژگی‌سازی‌شده', labelEn: 'enhanced_dataset', raw: 'enhanced_dataset', short: 'Enhanced'},
  A: {labelFa: 'دیتاست A — پایه', labelEn: 'Dataset A / baseline_dataset', raw: 'A', short: 'A'},
  B: {labelFa: 'دیتاست B — ویژگی‌سازی حداقلی', labelEn: 'Dataset B / enhanced_dataset', raw: 'B', short: 'B'},
  C: {labelFa: 'دیتاست C — ویژگی‌سازی طبقه‌بندی', labelEn: 'Dataset C / enhanced_dataset', raw: 'C', short: 'C'}
};
const featureDisplay = {
  OverallQual: {labelFa: 'کیفیت کلی ساختمان', labelEn: 'OverallQual', raw: 'OverallQual', short: 'OverallQual'},
  GrLivArea: {labelFa: 'زیربنای قابل سکونت', labelEn: 'GrLivArea', raw: 'GrLivArea', short: 'GrLivArea'},
  Neighborhood: {labelFa: 'محله', labelEn: 'Neighborhood', raw: 'Neighborhood', short: 'Neighborhood'}
};
const faTask = {regression:'رگرسیون', classification:'طبقه‌بندی'};
const faDataset = Object.fromEntries(Object.entries(datasetDisplay).map(([k, v]) => [k, `${v.labelFa} (${v.labelEn})`]));
const reliabilityFa = {high:'بالا', medium:'متوسط', low:'پایین'};
const severityFa = {low:'کم', medium:'متوسط', high:'زیاد'};

async function api(path){ const r = await fetch(path); if(!r.ok) throw new Error(await r.text()); return r.json(); }
function params(){ return `task=${$('task').value}&dataset=${$('dataset').value}&model=${$('model').value}`; }
function destroy(name){ if(charts[name]) charts[name].destroy(); }
function activeMode(){ return $('inputMode').value; }
function currentTask(){ return $('task').value; }
function isRegression(){ return currentTask() === 'regression'; }
function formatNumber(value){ return Number(value).toLocaleString('fa-IR', {maximumFractionDigits: 2}); }
function formatSigned(value){ const n = Number(value); return `${n > 0 ? '+' : ''}${formatNumber(n)}`; }
function formatMoney(value){ return `$${Number(value).toLocaleString('en-US', {maximumFractionDigits: 0})}`; }
function formatSignedMoney(value){ const n = Number(value); return `${n > 0 ? '+' : n < 0 ? '-' : ''}$${Math.abs(n).toLocaleString('en-US', {maximumFractionDigits: 0})}`; }
function valueText(value){ return isRegression() ? formatMoney(value) : `کلاس ${formatNumber(value)}`; }
function percent(value){ return `${Math.round(Number(value || 0) * 100).toLocaleString('fa-IR')}٪`; }

function formatDisplayMeta(meta, fallback){
  if(!meta) return fallback || '-';
  const fa = meta.labelFa || fallback || meta.raw || '-';
  const en = meta.labelEn || meta.raw || fallback || '-';
  return `${fa} (${en})`;
}
function modelLabel(model){ return formatDisplayMeta(modelDisplay[model], model); }
function datasetLabel(dataset, datasetType){ return formatDisplayMeta(datasetDisplay[dataset] || datasetDisplay[datasetType], dataset || datasetType); }
function humanizeFeatureName(feature){
  const raw = String(feature?.raw_feature || feature?.rawFeature || feature?.feature || feature || '');
  if(feature && typeof feature === 'object'){
    const fa = feature.display_name_fa || feature.labelFa || raw;
    const en = feature.display_name_en || feature.labelEn || raw;
    return `${fa} (${en})`;
  }
  if(featureDisplay[raw]) return formatDisplayMeta(featureDisplay[raw], raw);
  const neighborhood = raw.match(/^Neighborhood_(.+)$/);
  if(neighborhood) return `محله: ${neighborhood[1]} (${raw})`;
  const cleaned = raw.replace(/_/g, ' ');
  return `${cleaned} (${raw})`;
}
function escapeHtml(value){ return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function direction(error){ if(Number(error) > 0) return 'بیش‌برآورد'; if(Number(error) < 0) return 'کم‌برآورد'; return 'دقیق'; }
function severity(error, maxAbs){ const ratio = maxAbs ? Math.abs(error) / maxAbs : 0; if(ratio >= .66) return 'high'; if(ratio >= .33) return 'medium'; return 'low'; }
function pointColor(level, selected){ if(selected) return '#7c3aed'; return {low:'#22c55e', medium:'#f97316', high:'#ef4444'}[level] || '#22c55e'; }
function pointBorderColor(level, selected){ return selected ? '#4c1d95' : 'rgba(15, 23, 42, 0.18)'; }
function classOutcome(p){ return p.is_correct ?? Number(p.actual) === Number(p.predicted); }
function setPanel(id, html){ $(id).innerHTML = html; }

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
      return `<label>${escapeHtml(f.labelFa)} <small>${escapeHtml(f.rawName)}</small><input name="${escapeHtml(f.name)}" title="${escapeHtml(f.help || '')}" type="number" step="any" value="0"></label>`;
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

const metricDisplay = {
  rmse: {title: 'میانگین خطا', original: 'RMSE', format: formatMoney, caption: 'کمتر بهتر است؛ میانگین اندازه خطای مدل را نشان می‌دهد.'},
  r2: {title: 'قدرت توضیح مدل', original: 'R²', format: percent, caption: 'بیشتر بهتر است؛ سهم توضیح‌داده‌شده از تغییرات قیمت.'},
  accuracy: {title: 'دقت طبقه‌بندی', original: 'Accuracy', format: percent, caption: 'بیشتر بهتر است؛ سهم پیش‌بینی‌های درست را نشان می‌دهد.'},
  f1: {title: 'امتیاز F1', original: 'F1 Score', format: percent, caption: 'بیشتر بهتر است؛ تعادل دقت و پوشش کلاس‌ها را خلاصه می‌کند.'}
};

function renderMetrics(metrics){
  $('metrics').innerHTML = Object.entries(metrics).map(([k,v])=>{
    const meta = metricDisplay[k] || {title: k, original: k, format: value=>Number(value).toFixed(4), caption: 'معیار تکمیلی مدل برای ارزیابی عملکرد.'};
    return `<button class="metric-card" data-metric="${escapeHtml(k)}"><span class="metric-label">${escapeHtml(meta.title)} <small class="metric-raw">(${escapeHtml(meta.original)})</small></span><span class="metric-value">${escapeHtml(meta.format(v))}</span><span class="metric-caption">${escapeHtml(meta.caption)}</span></button>`;
  }).join('');
  document.querySelectorAll('.metric-card').forEach(btn=>btn.onclick=()=>explainMetric(btn.dataset.metric, metrics[btn.dataset.metric]));
}
function explainMetric(metric, value){
  const text = metric === 'rmse' ? 'RMSE خلاصه‌ای از اندازه خطاهای رگرسیون است؛ اگر بزرگ باشد، ابر نقطه‌ها پخش‌تر و هیستوگرام پهن‌تر دیده می‌شود.'
    : metric === 'r2' ? 'R² نشان می‌دهد مدل چه مقدار از تغییرات مقدار واقعی را توضیح می‌دهد؛ آن را کنار نمودار واقعی/پیش‌بینی بخوانید.'
    : metric === 'accuracy' ? 'Accuracy سهم پیش‌بینی‌های درست طبقه‌بندی است؛ در نمودار نقطه‌ای یعنی چند مورد کلاس درست گرفته‌اند.'
    : 'F1 دقت و پوشش طبقه‌ها را ترکیب می‌کند و برای خطاهای کلاس‌بندی از accuracy آموزشی‌تر است.';
  setPanel('pointPanel', `<b>${escapeHtml(metric)} = ${Number(value).toFixed(4)}</b><p>${text}</p>`);
}

async function drawCharts(){
  const v = await api('/api/visualization?'+params());
  destroy('scatter'); destroy('errors'); destroy('importance');
  const maxAbsError = Math.max(...v.errors.map(e=>Math.abs(Number(e))), 1);
  const points = isRegression()
    ? v.actual.map((a,i)=>({x:a,y:v.predicted[i], actual:a, predicted:v.predicted[i], error:v.errors[i], index:i, severity:severity(v.errors[i], maxAbsError)})).slice(0,400)
    : v.actual.map((a,i)=>{ const ok = v.is_correct?.[i] ?? Number(a) === Number(v.predicted[i]); return {x:ok ? 'درست' : 'غلط', y:ok ? 1 : 0, actual:v.actual_class?.[i] ?? a, predicted:v.predicted_class?.[i] ?? v.predicted[i], error:v.errors[i], index:i, is_correct:ok, severity:ok ? 'low' : 'high'}; }).slice(0,400);
  const bins = isRegression() ? histogram(v.errors, 20, formatMoney) : classificationSummary(v);
  vizState = {raw:v, points, bins, maxAbsError, selectedPoint:null, selectedBin:null, selectedFeature:null};
  $('taskLesson').textContent = isRegression() ? 'رگرسیون یعنی فاصله عدد پیش‌بینی‌شده با مقدار واقعی را می‌آموزیم.' : 'طبقه‌بندی یعنی درستی کلاس و احتمال انتخاب‌شده را بررسی می‌کنیم.';
  $('scatterTitle').textContent = isRegression() ? 'قیمت واقعی در برابر قیمت پیش‌بینی‌شده' : 'خلاصه درست/غلط طبقه‌بندی';
  $('errorTitle').textContent = isRegression() ? 'توزیع خطای پیش‌بینی (Prediction Error Distribution)' : 'تعداد پیش‌بینی‌های درست و غلط';
  $('errorHelp').textContent = isRegression() ? v.error_definition ? `تعریف خطا: ${v.error_definition}؛ واحد: ${v.error_unit || 'نامشخص'}.` : 'عدد منفی یعنی کم‌برآورد؛ عدد مثبت یعنی بیش‌برآورد.' : 'این نمودار به جای خطای عددی، تعداد پاسخ‌های درست و غلط طبقه‌بندی را نشان می‌دهد.';
  $('scatterHelp').textContent = isRegression() ? v.ideal_line_description || 'هر نقطه یک خانه است. هرچه به خط ایده‌آل نزدیک‌تر باشد، پیش‌بینی دقیق‌تر است.' : 'هر ستون نشان می‌دهد چند خانه در طبقه‌بندی درست یا غلط پیش‌بینی شده‌اند.';
  resetPanels();
  drawScatter(); drawErrors(); drawImportance();
}

function scatterBounds(points){
  const xs = points.map(p=>Number(p.x)), ys = points.map(p=>Number(p.y));
  const min = Math.min(...xs, ...ys), max = Math.max(...xs, ...ys);
  const pad = Math.max((max - min) * 0.06, isRegression() ? 1000 : 0.5);
  return {min:min - pad, max:max + pad};
}
function referenceLine(bounds){ return [{x:bounds.min, y:bounds.min}, {x:bounds.max, y:bounds.max}]; }

function drawScatter(){
  if(!isRegression()) return drawClassificationSummary();
  const ctx = $('scatter');
  const bounds = scatterBounds(vizState.points);
  charts.scatter = new Chart(ctx, {
    type:'scatter',
    data:{datasets:[
      {label:'خط پیش‌بینی ایده‌آل (Ideal Prediction Line)', data:referenceLine(bounds), type:'line', borderColor:'rgba(15, 23, 42, 0.35)', borderDash:[6,6], borderWidth:2, pointRadius:0, pointHitRadius:0, fill:false, order:0},
      {label:'خانه‌ها بر اساس سطح خطا', data:vizState.points, order:1, pointRadius:p=>p.raw.index===vizState.selectedPoint?7:4, pointHoverRadius:7, pointHitRadius:10, backgroundColor:p=>pointColor(p.raw.severity, p.raw.index===vizState.selectedPoint), borderColor:p=>pointBorderColor(p.raw.severity, p.raw.index===vizState.selectedPoint), borderWidth:p=>p.raw.index===vizState.selectedPoint?3:1.25}
    ]},
    options:{
      parsing:false, maintainAspectRatio:false, animation:false, interaction:{mode:'nearest', intersect:true},
      plugins:{legend:{display:true}, tooltip:{filter:item=>item.datasetIndex === 1, callbacks:{label:c=>tooltipForPoint(c.raw)}}},
      onClick:(evt)=>{ const hit=charts.scatter.getElementsAtEventForMode(evt,'nearest',{intersect:true},true).find(item=>item.datasetIndex===1); if(hit) selectPoint(hit.index); },
      scales:{
        x:{min:bounds.min, max:bounds.max, grace:0, title:{display:true,text:'قیمت واقعی (Actual SalePrice)'}, ticks:{callback:v=>formatMoney(v)}, grid:{color:'rgba(148, 163, 184, 0.22)'}},
        y:{min:bounds.min, max:bounds.max, grace:0, title:{display:true,text:'قیمت پیش‌بینی‌شده (Predicted SalePrice)'}, ticks:{callback:v=>formatMoney(v)}, grid:{color:'rgba(148, 163, 184, 0.22)'}}
      }
    }
  });
}
function drawClassificationSummary(){
  const counts = [vizState.points.filter(classOutcome).length, vizState.points.filter(p=>!classOutcome(p)).length];
  charts.scatter = new Chart($('scatter'), {
    type:'bar',
    data:{labels:['درست','غلط'], datasets:[{label:'نتیجه طبقه‌بندی', data:counts, backgroundColor:['#22c55e','#ef4444']}]},
    options:{maintainAspectRatio:false, animation:false, plugins:{tooltip:{callbacks:{label:c=>`${formatNumber(c.raw)} خانه ${c.label} پیش‌بینی شده است`}}}, onClick:(evt)=>{ const hit=charts.scatter.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectBin(hit.index, false); }, scales:{x:{title:{display:true,text:'نتیجه پیش‌بینی'}}, y:{beginAtZero:true,title:{display:true,text:'تعداد خانه‌ها'}}}}
  });
}
function tooltipForPoint(p){
  if(isRegression()) return [`قیمت واقعی: ${formatMoney(p.actual)}`, `قیمت پیش‌بینی‌شده: ${formatMoney(p.predicted)}`, `خطا: ${formatSignedMoney(p.error)}`, `نوع خطا: ${direction(p.error)}`, `سطح خطا: ${severityFa[p.severity]}`];
  return classOutcome(p) ? `درست | کلاس ${formatNumber(p.actual)}` : `غلط | واقعی ${formatNumber(p.actual)}، پیش‌بینی ${formatNumber(p.predicted)}`;
}
function selectPoint(index){
  const p = vizState.points[index];
  vizState.selectedPoint = p.index;
  const binIndex = isRegression() ? findBin(p.error) : findClassBin(p);
  setPanel('pointPanel', `<b>${isRegression()?'جزئیات پیش‌بینی':'جزئیات طبقه‌بندی'}</b><div class="fact-grid"><span>واقعی</span><strong>${valueText(p.actual)}</strong><span>پیش‌بینی</span><strong>${valueText(p.predicted)}</strong><span>خطا</span><strong>${isRegression()?formatSignedMoney(p.error):formatSigned(p.error)}</strong><span>برداشت</span><strong>${isRegression()?direction(p.error):(classOutcome(p)?'درست':'غلط')}</strong></div><p>${isRegression()?`این نمونه ${severityFa[p.severity]} خطا دارد و به بازه خطای انتخاب‌شده وصل شد.`:'در طبقه‌بندی، درست بودن کلاس از فاصله عددی مهم‌تر است.'}</p>`);
  selectBin(binIndex, false);
  charts.scatter.update();
}

function drawErrors(){
  charts.errors = new Chart($('errors'), {
    type:'bar',
    data:{labels:vizState.bins.labels, datasets:[{label:isRegression()?'توزیع خطا':'درست/غلط', data:vizState.bins.counts, backgroundColor:(c)=>isRegression()?binColor(c.dataIndex):['#22c55e','#ef4444'][c.dataIndex], borderColor:(c)=>c.dataIndex===vizState.selectedBin?'#7c3aed':'transparent', borderWidth:2}]},
    options:{maintainAspectRatio:false, plugins:{tooltip:{callbacks:{label:c=>`${formatNumber(c.raw)} پیش‌بینی در ${vizState.bins.labels[c.dataIndex]}`}}}, onClick:(evt)=>{ const hit=charts.errors.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectBin(hit.index, true); }, scales:{x:{title:{display:true,text:isRegression()?'اختلاف پیش‌بینی با واقعیت (Predicted - Actual)':'نتیجه طبقه‌بندی'}}, y:{title:{display:true,text:'تعداد'}}}}
  });
}
function binColor(i){ if(i===vizState.selectedBin) return '#7c3aed'; const mid=vizState.bins.centers[i]; if(Math.abs(mid) < vizState.bins.step) return '#22c55e'; return mid < 0 ? '#38bdf8' : '#f97316'; }
function selectBin(index, renderScatterLink){
  vizState.selectedBin = index;
  const examples = vizState.bins.members[index].slice(0,6).map(i=>({i, actual:vizState.raw.actual_class?.[i] ?? vizState.raw.actual[i], predicted:vizState.raw.predicted_class?.[i] ?? vizState.raw.predicted[i], error:vizState.raw.errors[i]}));
  const center = vizState.bins.centers[index];
  const label = isRegression() ? (Math.abs(center) < vizState.bins.step ? 'نزدیک به دقیق' : center < 0 ? 'کم‌برآورد' : 'بیش‌برآورد') : (index === 0 ? 'پیش‌بینی درست' : 'پیش‌بینی غلط');
  const title = isRegression() ? `بازه ${escapeHtml(vizState.bins.labels[index])} — ${label}` : `${label}: ${formatNumber(vizState.bins.counts[index])} خانه`;
  setPanel('binPanel', `<b>${title}</b><div class="mini-list">${examples.map(e=>`<button onclick="selectPointByRawIndex(${e.i})"><span>#${e.i}</span><span>${valueText(e.actual)} → ${valueText(e.predicted)}</span><b>${isRegression()?formatSignedMoney(e.error):(Number(e.error)===0?'درست':'غلط')}</b></button>`).join('') || '<p>نمونه‌ای در این بازه نیست.</p>'}</div>`);
  charts.errors?.update();
  if(renderScatterLink) charts.scatter?.update();
}
function selectPointByRawIndex(rawIndex){ const i = vizState.points.findIndex(p=>p.index===rawIndex); if(i >= 0) selectPoint(i); }

function drawImportance(){
  const items = vizState.raw.feature_importance || [];
  charts.importance = new Chart($('importance'), {
    type:'bar',
    data:{labels:items.map(x=>humanizeFeatureName(x)), datasets:[{label:'اهمیت ویژگی', data:items.map(x=>x.importance), backgroundColor:(c)=>c.dataIndex===vizState.selectedFeature?'#7c3aed':'#14b8a6'}]},
    options:{maintainAspectRatio:false, indexAxis:'y', plugins:{tooltip:{callbacks:{title:items=>items.length ? humanizeFeatureName(vizState.raw.feature_importance[items[0].dataIndex]) : '', label:c=>`اهمیت: ${formatNumber(c.raw)} — نام فنی: ${vizState.raw.feature_importance[c.dataIndex].feature}`}}}, onClick:(evt)=>{ const hit=charts.importance.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectFeature(hit.index); }}
  });
}
function selectFeature(index){
  vizState.selectedFeature = index;
  const f = vizState.raw.feature_importance[index];
  const model = $('model').value;
  const modelText = model.includes('linear') || model.includes('logistic') ? 'در مدل خطی/لجستیک، این عدد از اندازه ضریب می‌آید.' : 'در مدل درختی، این عدد نشان می‌دهد ویژگی چقدر در تقسیم‌ها و تصمیم‌های مدل استفاده شده است.';
  setPanel('featurePanel', `<b>${escapeHtml(humanizeFeatureName(f))}</b><div class="fact-grid"><span>نام فنی</span><strong>${escapeHtml(f.feature)}</strong><span>رتبه</span><strong>${formatNumber(index+1)}</strong><span>اهمیت</span><strong>${formatNumber(f.importance)}</strong></div><p>${modelText}</p><p class="warn">هشدار آموزشی: اهمیت کلی ویژگی به معنی علت قطعی یا توضیح یک پیش‌بینی خاص نیست.</p>`);
  const context = $('featureContext');
  if(context) context.textContent = `ویژگی انتخاب‌شده: ${humanizeFeatureName(f)} | نام فنی: ${f.feature}. این یک نشانه کلی از رفتار مدل است، نه دلیل قطعی همین پیش‌بینی.`;
  charts.importance.update();
}

function histogram(values, n, formatter=formatNumber){
  const nums = values.map(Number), min=Math.min(...nums), max=Math.max(...nums), step=(max-min||1)/n, counts=Array(n).fill(0), members=Array.from({length:n},()=>[]);
  nums.forEach((x,i)=>{ const b=Math.min(n-1, Math.floor((x-min)/step)); counts[b]++; members[b].push(i); });
  return {labels:counts.map((_,i)=>`${formatter(min+i*step)} تا ${formatter(min+(i+1)*step)}`), centers:counts.map((_,i)=>min+(i+.5)*step), counts, members, min, max, step};
}
function classificationSummary(v){
  const members=[[],[]];
  (v.is_correct || v.actual.map((a,i)=>Number(a)===Number(v.predicted[i]))).forEach((ok,i)=>members[ok?0:1].push(i));
  return {labels:['درست','غلط'], centers:[0,1], counts:members.map(m=>m.length), members, min:0, max:1, step:1};
}
function findBin(error){ return Math.min(vizState.bins.counts.length-1, Math.max(0, Math.floor((Number(error)-vizState.bins.min)/vizState.bins.step))); }
function findClassBin(p){ return classOutcome(p) ? 0 : 1; }
function resetPanels(){
  setPanel('pointPanel','برای دیدن واقعی، پیش‌بینی، خطا و تفسیر، یک نقطه را انتخاب کنید.');
  setPanel('binPanel', isRegression() ? 'یک ستون خطا را انتخاب کنید تا نمونه‌های آن بازه نمایش داده شود.' : 'ستون درست یا غلط را انتخاب کنید تا نمونه‌ها نمایش داده شوند.');
  setPanel('featurePanel','یک ویژگی را انتخاب کنید تا معنی اهمیت و محدودیت آن را ببینید.');
}

function renderResult(data){
  lastPrediction = data;
  const meta = data.model_metadata || {};
  const reliability = data.analysis?.reliability || 'low';
  const confidence = Number(data.confidence || 0);
  const resultIsRegression = meta.task_type === 'regression';
  const title = resultIsRegression ? 'قیمت پیش‌بینی‌شده' : 'کلاس پیش‌بینی‌شده';
  const mainValue = resultIsRegression ? formatMoney(data.prediction) : escapeHtml(data.predicted_class ?? data.prediction);
  const rangeMeta = data.prediction_range || null;
  const range = rangeMeta ? `${formatMoney(rangeMeta.lower)} — ${formatMoney(rangeMeta.upper)}` : null;
  const probs = data.class_probabilities ? Object.entries(data.class_probabilities).map(([klass, prob]) => `
    <div class="probability-row"><span>کلاس ${escapeHtml(klass)}</span><div class="probability-track"><i style="width:${Math.max(0, Math.min(100, Number(prob)*100))}%"></i></div><strong>${percent(prob)}</strong></div>`).join('') : '';
  const confidenceTitle = resultIsRegression ? 'شاخص اطمینان تقریبی (RMSE-based Confidence)' : 'اعتماد مدل';
  const confidenceTip = resultIsRegression
    ? (data.confidence_explanation || 'این عدد احتمال درست بودن نیست؛ از نسبت RMSE به میانگین قیمت ساخته شده است.')
    : 'در طبقه‌بندی، اعتماد همان احتمال کلاس انتخاب‌شده است؛ احتمال‌های نزدیک یعنی مدل مرددتر است.';
  const rangeHelp = rangeMeta ? 'این بازه تضمینی نیست؛ خطای معمول مدل روی داده آزمون را نشان می‌دهد.' : '';
  const rangeBasis = rangeMeta?.basis || '±1 RMSE';
  $('resultCard').className = `result-card reliability-${reliability}`;
  $('resultCard').innerHTML = `
    <div class="result-topline"><span>${title}</span><span class="badge">قابلیت اتکا: ${reliabilityFa[reliability] || reliability}</span></div>
    <div class="prediction-value">${mainValue}</div>
    ${range ? `<div class="range-line explainer" title="${escapeHtml(rangeHelp)}"><b>بازه تقریبی پیش‌بینی (${escapeHtml(rangeBasis)})</b><span>${range}</span><small>${escapeHtml(rangeHelp)}</small></div>` : ''}
    <div class="confidence-block explainer" title="${escapeHtml(confidenceTip)}"><div><b>${escapeHtml(confidenceTitle)}</b><span>${percent(confidence)}</span></div><div class="progress"><i style="width:${Math.max(0, Math.min(100, confidence * 100))}%"></i></div><small>${escapeHtml(confidenceTip)}</small></div>
    <div class="info-panel"><div><small>مدل</small><b>${escapeHtml(modelLabel(meta.model_name || '-'))}</b></div><div><small>دیتاست</small><b>${escapeHtml(datasetLabel(meta.dataset_used || '-', meta.dataset_type))}</b></div><div><small>نوع مسئله</small><b>${escapeHtml(faTask[meta.task_type] || meta.task_type || '-')}</b></div></div>
    <div class="analysis"><b>تحلیل</b><p>${escapeHtml(data.analysis?.explanation || '')}</p><p id="featureContext" class="muted">با انتخاب یک ویژگی از نمودار اهمیت، ارتباط کلی آن با رفتار مدل اینجا نمایش داده می‌شود.</p></div>
    ${probs ? `<div class="probabilities"><b>احتمال کلاس‌ها</b>${probs}</div>` : ''}`;
}

$('load').onclick = loadAll;
$('predict').onclick = async()=>{
  const body = {task:$('task').value,dataset:$('dataset').value,model:$('model').value,input_mode:activeMode(),features:{}};
  if(activeMode()==='advanced'){
    document.querySelectorAll('#form input').forEach(i=>body.features[i.name]=Number(i.value||0));
    document.querySelectorAll('#form select[data-onehot-group]').forEach(sel=>{
      currentFeatures.filter(f=>f.oneHotGroup===sel.dataset.onehotGroup).forEach(f=>body.features[f.name]=f.rawName===sel.value?1:0);
    });
  }
  if(activeMode()==='preset') body.preset_id = $('preset').value;
  if(activeMode()==='dataset') body.sample_id = $('sample').value;
  $('loading').hidden = false; $('predict').disabled = true;
  try{
    const r = await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data = await r.json();
    if(!r.ok) throw new Error(JSON.stringify(data));
    renderResult(data);
    $('result').textContent = JSON.stringify(data, null, 2);
    $('technicalDetails').hidden = false;
  }catch(e){
    $('resultCard').className = 'result-card error-state';
    $('resultCard').textContent = `خطا در پیش‌بینی: ${e.message}`;
  }finally{
    $('loading').hidden = true; $('predict').disabled = false;
  }
};
loadOptions().catch(e=>alert(e.message));

const comparisonMockData = {
  regression: {
    primaryMetric: 'RMSE',
    metricDirection: {rmse:'lower', mae:'lower', r2:'higher', normalizedRmse:'lower'},
    rows: [
      {id:'reg-a-rf', datasetId:'A', datasetLabelFa:'دیتاست A — پایه', datasetLabelEn:'Dataset A / Baseline Housing', datasetRawName:'baseline_dataset', modelLabelFa:'جنگل تصادفی', modelLabelEn:'Random Forest', modelRawName:'random_forest', rmse:27450, mae:18220, r2:0.89, normalizedRmse:0.118, rank:1, interpretation:'بهترین تعادل خطا و توضیح‌پذیری؛ روی داده پایه پایدارترین رفتار را دارد.'},
      {id:'reg-b-xgb', datasetId:'B', datasetLabelFa:'دیتاست B — ویژگی‌سازی‌شده', datasetLabelEn:'Dataset B / Enhanced Features', datasetRawName:'enhanced_dataset', modelLabelFa:'ایکس‌جی‌بوست', modelLabelEn:'XGBoost', modelRawName:'xgboost', rmse:28680, mae:19040, r2:0.875, normalizedRmse:0.123, rank:2, interpretation:'با ویژگی‌های بیشتر بهتر از مدل خطی عمل می‌کند اما کمی واریانس خطا دارد.'},
      {id:'reg-b-rf', datasetId:'B', datasetLabelFa:'دیتاست B — ویژگی‌سازی‌شده', datasetLabelEn:'Dataset B / Enhanced Features', datasetRawName:'enhanced_dataset', modelLabelFa:'جنگل تصادفی', modelLabelEn:'Random Forest', modelRawName:'random_forest', rmse:30120, mae:20110, r2:0.862, normalizedRmse:0.129, rank:3, interpretation:'رفتار مقاوم دارد اما نسبت به دیتاست پایه اندکی خطای نرمال‌شده بالاتر است.'},
      {id:'reg-a-linear', datasetId:'A', datasetLabelFa:'دیتاست A — پایه', datasetLabelEn:'Dataset A / Baseline Housing', datasetRawName:'baseline_dataset', modelLabelFa:'رگرسیون خطی', modelLabelEn:'Linear Regression', modelRawName:'linear_regression', rmse:39200, mae:26500, r2:0.751, normalizedRmse:0.169, rank:4, interpretation:'خط مبنا قابل فهم است ولی الگوهای غیرخطی قیمت را کامل نمی‌گیرد.'}
    ]
  },
  classification: {
    primaryMetric: 'Weighted F1',
    metricDirection: {accuracy:'higher', weightedF1:'higher', macroF1:'higher'},
    rows: [
      {id:'cls-c-xgb', datasetId:'C', datasetLabelFa:'دیتاست C — ویژگی‌سازی طبقه‌بندی', datasetLabelEn:'Dataset C / Classification Features', datasetRawName:'enhanced_dataset', modelLabelFa:'ایکس‌جی‌بوست', modelLabelEn:'XGBoost', modelRawName:'xgboost', accuracy:0.884, weightedF1:0.879, macroF1:0.842, rank:1, interpretation:'بهترین عملکرد کلی؛ کلاس‌های پرتعداد و کم‌تعداد را نسبتاً متوازن مدیریت می‌کند.'},
      {id:'cls-c-rf', datasetId:'C', datasetLabelFa:'دیتاست C — ویژگی‌سازی طبقه‌بندی', datasetLabelEn:'Dataset C / Classification Features', datasetRawName:'enhanced_dataset', modelLabelFa:'جنگل تصادفی', modelLabelEn:'Random Forest', modelRawName:'random_forest', accuracy:0.861, weightedF1:0.854, macroF1:0.811, rank:2, interpretation:'دقت خوب دارد اما برای کلاس‌های کوچک‌تر کمی افت Macro F1 دیده می‌شود.'},
      {id:'cls-a-log', datasetId:'A', datasetLabelFa:'دیتاست A — پایه', datasetLabelEn:'Dataset A / Baseline Housing', datasetRawName:'baseline_dataset', modelLabelFa:'رگرسیون لجستیک', modelLabelEn:'Logistic Regression', modelRawName:'logistic_regression', accuracy:0.812, weightedF1:0.801, macroF1:0.754, rank:3, interpretation:'مدل ساده و قابل توضیح است؛ برای مرزبندی‌های غیرخطی محدودیت دارد.'},
      {id:'cls-b-log', datasetId:'B', datasetLabelFa:'دیتاست B — ویژگی‌سازی‌شده', datasetLabelEn:'Dataset B / Enhanced Features', datasetRawName:'enhanced_dataset', modelLabelFa:'رگرسیون لجستیک', modelLabelEn:'Logistic Regression', modelRawName:'logistic_regression', accuracy:0.793, weightedF1:0.782, macroF1:0.731, rank:4, interpretation:'افزایش ویژگی‌ها برای مدل خطی الزاماً سودمند نیست و احتمال نویز را بالا می‌برد.'}
    ]
  }
};
let comparisonState = {task:'regression', selectedId:null};
function comparisonRows(){ return comparisonMockData[comparisonState.task].rows; }
function comparisonLabel(row){ return `${row.datasetLabelFa} (${row.datasetLabelEn}) / ${row.modelLabelFa} (${row.modelLabelEn})`; }
function comparisonMetricValue(row, key){ return key === 'normalizedRmse' ? row.normalizedRmse : row[key]; }
function formatMetricValue(value, kind){ return ['accuracy','weightedF1','macroF1','r2','normalizedRmse'].includes(kind) ? percent(value) : formatMoney(value); }
function bestComparisonRow(){ return comparisonRows().find(r=>r.rank===1) || comparisonRows()[0]; }
function metricClass(row, key){ const rows=comparisonRows(), dir=comparisonMockData[comparisonState.task].metricDirection[key]; const vals=rows.map(r=>comparisonMetricValue(r,key)); const best=dir==='lower'?Math.min(...vals):Math.max(...vals); return comparisonMetricValue(row,key)===best?' best-metric':''; }
function renderComparison(){
  const task=comparisonState.task, cfg=comparisonMockData[task], rows=cfg.rows, best=bestComparisonRow();
  if(!comparisonState.selectedId) comparisonState.selectedId=best.id;
  document.querySelectorAll('.comparison-tab').forEach(btn=>{ const active=btn.dataset.comparisonTask===task; btn.classList.toggle('active',active); btn.setAttribute('aria-selected', String(active)); });
  $('comparisonSummary').innerHTML = [
    ['Best model', `${best.modelLabelFa} (${best.modelLabelEn})`, best.modelRawName],
    ['Best dataset/model pair', comparisonLabel(best), `${best.datasetRawName} / ${best.modelRawName}`],
    ['Primary metric', cfg.primaryMetric, task==='regression'?'lower is better for RMSE':'higher is better for Weighted F1'],
    ['Key takeaway', best.interpretation, 'Mock data only — ready for future API shape']
  ].map(([t,v,s])=>`<article class="summary-card"><span>${escapeHtml(t)}</span><strong>${escapeHtml(v)}</strong><small>${escapeHtml(s)}</small></article>`).join('');
  const reg=task==='regression';
  const cols=reg?['Dataset','Model','RMSE','MAE','R²','Normalized RMSE','Rank']:['Dataset','Model','Accuracy','Weighted F1','Macro F1','Rank'];
  $('comparisonTable').innerHTML = `<thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr class="${r.rank===1?'best-row ':''}${r.id===comparisonState.selectedId?'selected-row':''}" data-comparison-id="${r.id}"><td><b>${escapeHtml(r.datasetLabelFa)}</b><small>${escapeHtml(r.datasetLabelEn)} · raw: ${escapeHtml(r.datasetRawName)} · id: ${escapeHtml(r.datasetId)}</small></td><td><b>${escapeHtml(r.modelLabelFa)}</b><small>${escapeHtml(r.modelLabelEn)} · raw: ${escapeHtml(r.modelRawName)}</small></td>${reg?`<td class="number${metricClass(r,'rmse')}">${formatMoney(r.rmse)}</td><td class="number${metricClass(r,'mae')}">${formatMoney(r.mae)}</td><td class="number${metricClass(r,'r2')}">${percent(r.r2)}</td><td class="number${metricClass(r,'normalizedRmse')}">${percent(r.normalizedRmse)}</td>`:`<td class="number${metricClass(r,'accuracy')}">${percent(r.accuracy)}</td><td class="number${metricClass(r,'weightedF1')}">${percent(r.weightedF1)}</td><td class="number${metricClass(r,'macroF1')}">${percent(r.macroF1)}</td>`}<td><span class="rank-pill">#${formatNumber(r.rank)}</span></td></tr>`).join('')}</tbody>`;
  document.querySelectorAll('#comparisonTable tbody tr').forEach(tr=>tr.onclick=()=>selectComparisonRow(tr.dataset.comparisonId));
  renderComparisonCharts(); renderComparisonInsights(); renderComparisonDetail();
}
function selectComparisonRow(id){ comparisonState.selectedId=id; renderComparison(); }
function renderComparisonCharts(){
  const reg=comparisonState.task==='regression', rows=comparisonRows();
  destroy('comparisonOne'); destroy('comparisonTwo');
  $('comparisonChartOneTitle').textContent=reg?'RMSE by model/dataset':'Accuracy by model/dataset';
  $('comparisonChartOneHelp').textContent=reg?'RMSE: lower is better. MAE: lower is better.':'Accuracy/F1: higher is better.';
  $('comparisonChartTwoTitle').textContent=reg?'R² by model/dataset':'Weighted F1 by model/dataset';
  $('comparisonChartTwoHelp').textContent=reg?'R²: higher is better.':'Accuracy/F1: higher is better.';
  const labels=rows.map(comparisonLabel), colors=rows.map(r=>r.id===comparisonState.selectedId?'#7c3aed':r.rank===1?'#22c55e':'#2563eb');
  const make = (canvas, key, name) => new Chart($(canvas), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: name,
        data: rows.map(r => comparisonMetricValue(r, key)),
        backgroundColor: colors,
        borderColor: rows.map(r => r.rank === 1 ? '#166534' : 'transparent'),
        borderWidth: 2
      }]
    },
    options: {
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {legend: {display: false}, tooltip: {callbacks: {label: c => `${name}: ${formatMetricValue(c.raw, key)}`}}},
      onClick: (evt, els) => { if(els[0]) selectComparisonRow(rows[els[0].index].id); },
      scales: {
        x: {beginAtZero: true, ticks: {callback: v => formatMetricValue(v, key)}},
        y: {ticks: {autoSkip: false}}
      }
    }
  });
  charts.comparisonOne=make('comparisonChartOne', reg?'rmse':'accuracy', reg?'RMSE':'Accuracy');
  charts.comparisonTwo=make('comparisonChartTwo', reg?'r2':'weightedF1', reg?'R²':'Weighted F1');
}
function renderComparisonInsights(){
  const reg=comparisonState.task==='regression';
  $('comparisonInsights').innerHTML = [
    ['Overall takeaway', reg?'در داده mock، مدل‌های درختی خطای قیمت را کمتر از مدل خطی نگه می‌دارند.':'در داده mock، XGBoost بهترین Weighted F1 را دارد و تعادل کلاس‌ها بهتر حفظ شده است.'],
    ['Dataset effect', reg?'تغییر دیتاست همیشه بهبود ایجاد نمی‌کند؛ Normalized RMSE کمک می‌کند اثر مقیاس قیمت کنترل شود.':'ویژگی‌سازی طبقه‌بندی برای مدل‌های غیرخطی مفیدتر از مدل لجستیک ساده است.'],
    ['Model behavior', reg?'Random Forest پایدار است؛ XGBoost حساس‌تر ولی رقابتی است؛ Linear Regression خط مبنای قابل توضیح می‌دهد.':'مدل‌های غیرخطی مرزهای تصمیم پیچیده‌تر را بهتر می‌گیرند اما باید با Macro F1 کنترل شوند.'],
    ['Metric caution', reg?'RMSE به خطاهای بزرگ حساس است؛ MAE و R² را همزمان بخوانید.':'Accuracy در کلاس‌های نامتوازن کافی نیست؛ Weighted F1 و Macro F1 را کنار آن ببینید.']
  ].map(([h,p])=>`<article><h3>${h}</h3><p>${p}</p></article>`).join('');
}
function renderComparisonDetail(){
  const row=comparisonRows().find(r=>r.id===comparisonState.selectedId) || bestComparisonRow(), best=bestComparisonRow(), reg=comparisonState.task==='regression';
  const delta=reg?row.rmse-best.rmse:best.weightedF1-row.weightedF1;
  $('comparisonDetailPanel').innerHTML = `<h3>جزئیات انتخاب‌شده</h3><p><b>${escapeHtml(comparisonLabel(row))}</b></p><div class="fact-grid"><span>Dataset raw</span><strong>${escapeHtml(row.datasetRawName)}</strong><span>Model raw</span><strong>${escapeHtml(row.modelRawName)}</strong><span>Rank</span><strong>#${formatNumber(row.rank)}</strong>${reg?`<span>RMSE</span><strong>${formatMoney(row.rmse)}</strong><span>MAE</span><strong>${formatMoney(row.mae)}</strong><span>R²</span><strong>${percent(row.r2)}</strong><span>Normalized RMSE</span><strong>${percent(row.normalizedRmse)}</strong>`:`<span>Accuracy</span><strong>${percent(row.accuracy)}</strong><span>Weighted F1</span><strong>${percent(row.weightedF1)}</strong><span>Macro F1</span><strong>${percent(row.macroF1)}</strong>`}</div><p>${escapeHtml(row.interpretation)}</p><p class="warn">مقایسه با بهترین: ${reg?`RMSE این انتخاب ${formatMoney(delta)} از بهترین ${delta===0?'برابر/بهتر نیست؛ خودش بهترین است':'بیشتر'} است.`:`Weighted F1 این انتخاب ${percent(delta)} ${delta===0?'با بهترین برابر است':'کمتر از بهترین'} است.`}</p>`;
}
document.querySelectorAll('.comparison-tab').forEach(btn=>btn.onclick=()=>{comparisonState={task:btn.dataset.comparisonTask, selectedId:null}; renderComparison();});
renderComparison();
