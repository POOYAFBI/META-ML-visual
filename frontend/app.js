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

async function api(path, options){ const r = await fetch(path, options); if(!r.ok) throw new Error(await r.text()); return r.json(); }
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
  destroy('scatter'); destroy('errors'); destroy('importance'); destroy('classwisePerformance'); destroy('confidenceDistribution'); destroy('simplex');
  const maxAbsError = Math.max(...v.errors.map(e=>Math.abs(Number(e))), 1);
  const points = isRegression()
    ? v.actual.map((a,i)=>({x:a,y:v.predicted[i], actual:a, predicted:v.predicted[i], error:v.errors[i], index:i, severity:severity(v.errors[i], maxAbsError)})).slice(0,400)
    : v.actual.map((a,i)=>{ const ok = v.is_correct?.[i] ?? Number(a) === Number(v.predicted[i]); return {x:ok ? 'درست' : 'غلط', y:ok ? 1 : 0, actual:v.actual_class?.[i] ?? a, predicted:v.predicted_class?.[i] ?? v.predicted[i], error:v.errors[i], index:i, is_correct:ok, severity:ok ? 'low' : 'high'}; }).slice(0,400);
  const bins = isRegression() ? histogram(v.errors, 20, formatMoney) : classificationSummary(v);
  vizState = {raw:v, points, bins, maxAbsError, selectedPoint:null, selectedBin:null, selectedFeature:null, selectedConfusionCell:null, selectedClass:null, selectedConfidenceBin:null, selectedMistake:null, selectedSimplexPoint:null};
  $('taskLesson').textContent = isRegression() ? 'رگرسیون یعنی فاصله عدد پیش‌بینی‌شده با مقدار واقعی را می‌آموزیم.' : 'طبقه‌بندی یعنی درستی کلاس و احتمال انتخاب‌شده را بررسی می‌کنیم.';
  $('scatterTitle').textContent = isRegression() ? 'قیمت واقعی در برابر قیمت پیش‌بینی‌شده' : 'ماتریس خطای طبقه‌بندی (Confusion Matrix)';
  $('errorTitle').textContent = isRegression() ? 'توزیع خطای پیش‌بینی (Prediction Error Distribution)' : 'تعداد پیش‌بینی‌های درست و غلط';
  $('errorHelp').textContent = isRegression() ? v.error_definition ? `تعریف خطا: ${v.error_definition}؛ واحد: ${v.error_unit || 'نامشخص'}.` : 'عدد منفی یعنی کم‌برآورد؛ عدد مثبت یعنی بیش‌برآورد.' : 'این نمودار به جای خطای عددی، تعداد پاسخ‌های درست و غلط طبقه‌بندی را نشان می‌دهد.';
  $('scatterHelp').textContent = isRegression() ? v.ideal_line_description || 'هر نقطه یک خانه است. هرچه به خط ایده‌آل نزدیک‌تر باشد، پیش‌بینی دقیق‌تر است.' : 'خانه‌های روی قطر اصلی پیش‌بینی درست هستند؛ خانه‌های بیرون قطر نشان می‌دهند مدل کدام کلاس‌ها را با هم اشتباه گرفته است.';
  resetPanels();
  drawScatter(); drawErrors(); drawImportance(); drawClassificationLayer();
}

function scatterBounds(points){
  const xs = points.map(p=>Number(p.x)), ys = points.map(p=>Number(p.y));
  const min = Math.min(...xs, ...ys), max = Math.max(...xs, ...ys);
  const pad = Math.max((max - min) * 0.06, isRegression() ? 1000 : 0.5);
  return {min:min - pad, max:max + pad};
}
function referenceLine(bounds){ return [{x:bounds.min, y:bounds.min}, {x:bounds.max, y:bounds.max}]; }

function drawScatter(){
  const scatter = $('scatter');
  const matrix = $('confusionMatrix');
  if(!isRegression()){
    scatter.hidden = true;
    matrix.hidden = false;
    return drawConfusionMatrix();
  }
  scatter.hidden = false;
  matrix.hidden = true;
  matrix.innerHTML = '';
  const ctx = scatter;
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
function buildConfusionMatrix(){
  const cm = vizState.raw.confusion_matrix || {};
  const rawLabels = cm.labels || vizState.raw.class_labels || Array.from(new Set([...(vizState.raw.actual_class || vizState.raw.actual || []), ...(vizState.raw.predicted_class || vizState.raw.predicted || [])]));
  const labels = rawLabels.map(String);
  const displayLabels = (cm.display_labels || rawLabels).map(String);
  const matrix = cm.matrix ? cm.matrix.map(row=>row.map(Number)) : labels.map(()=>labels.map(()=>0));
  const members = labels.map(()=>labels.map(()=>[]));
  const actual = vizState.raw.actual_class || vizState.raw.actual || [];
  const predicted = vizState.raw.predicted_class || vizState.raw.predicted || [];
  const labelIndex = new Map(labels.map((label, i)=>[String(label), i]));
  actual.forEach((a, i)=>{
    const r = labelIndex.get(String(a));
    const c = labelIndex.get(String(predicted[i]));
    if(r !== undefined && c !== undefined){
      members[r][c].push(i);
      if(!cm.matrix) matrix[r][c]++;
    }
  });
  return {labels, displayLabels, matrix, members};
}
function drawConfusionMatrix(){
  const target = $('confusionMatrix');
  const data = buildConfusionMatrix();
  vizState.confusion = data;
  const maxCount = Math.max(...data.matrix.flat(), 1);
  const cols = data.labels.length + 1;
  const cells = [];
  cells.push('<div class="cm-corner"><span>واقعی ↓</span><b>پیش‌بینی →</b></div>');
  data.displayLabels.forEach(label=>cells.push(`<div class="cm-axis cm-predicted">${escapeHtml(label)}</div>`));
  data.matrix.forEach((row, r)=>{
    const rowTotal = row.reduce((sum, n)=>sum + Number(n), 0);
    cells.push(`<div class="cm-axis cm-actual">${escapeHtml(data.displayLabels[r])}</div>`);
    row.forEach((count, c)=>{
      const pct = rowTotal ? count / rowTotal : 0;
      const intensity = Math.max(0.08, count / maxCount);
      const correct = r === c;
      const selected = vizState.selectedConfusionCell?.row === r && vizState.selectedConfusionCell?.col === c;
      const label = `واقعی ${data.displayLabels[r]}، پیش‌بینی ${data.displayLabels[c]}، تعداد ${count}، ${correct ? 'درست' : 'خطا'}`;
      cells.push(`<button type="button" class="cm-cell ${correct ? 'cm-correct' : 'cm-error'} ${selected ? 'selected' : ''}" style="--intensity:${intensity}" aria-label="${escapeHtml(label)}" onclick="selectConfusionCell(${r},${c})"><strong>${formatNumber(count)}</strong><span>${percent(pct)}</span></button>`);
    });
  });
  target.innerHTML = `<div class="cm-wrap" style="grid-template-columns: minmax(88px, 1fr) repeat(${cols - 1}, minmax(82px, 1fr));">${cells.join('')}</div><div class="cm-legend"><span><i class="legend-correct"></i>قطر اصلی: درست</span><span><i class="legend-error"></i>بیرون قطر: خطا</span><span>رنگ پررنگ‌تر = تعداد بیشتر</span></div>`;
}
function selectConfusionCell(row, col){
  vizState.selectedConfusionCell = {row, col};
  const data = vizState.confusion || buildConfusionMatrix();
  const count = data.matrix[row][col];
  const correct = row === col;
  const examples = data.members[row][col].slice(0, 6);
  setPanel('pointPanel', `<b>${correct ? 'خانه درست در ماتریس خطا' : 'خانه خطا در ماتریس خطا'}</b><div class="fact-grid"><span>کلاس واقعی</span><strong>${escapeHtml(data.displayLabels[row])}</strong><span>کلاس پیش‌بینی</span><strong>${escapeHtml(data.displayLabels[col])}</strong><span>تعداد</span><strong>${formatNumber(count)}</strong><span>برداشت</span><strong>${correct ? 'درست' : 'خطا'}</strong></div>${correct ? '' : '<p class="warn">این نوع خطا نشان می‌دهد مدل این دو کلاس را با هم اشتباه می‌گیرد.</p>'}<div class="mini-list">${examples.map(i=>`<button onclick="selectPointByRawIndex(${i})"><span>#${i}</span><span>${escapeHtml(data.displayLabels[row])} → ${escapeHtml(data.displayLabels[col])}</span><b>${correct ? 'درست' : 'خطا'}</b></button>`).join('') || '<p>نمونه‌ای برای این خانه وجود ندارد.</p>'}</div>`);
  drawConfusionMatrix();
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
  charts.scatter?.update();
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


const classPalette = ['#2563eb', '#14b8a6', '#7c3aed', '#f59e0b', '#ec4899', '#0ea5e9'];
function classColor(classId, order=[]){
  const index = order.map(String).indexOf(String(classId));
  return classPalette[(index >= 0 ? index : Math.abs(String(classId).split('').reduce((sum,ch)=>sum+ch.charCodeAt(0),0))) % classPalette.length];
}
function classOrderForProbabilities(raw){
  const probabilities = raw?.class_probabilities || [];
  const first = probabilities.find(p=>p && Object.keys(p).length);
  const labels = raw?.confusion_matrix?.labels;
  if(Array.isArray(labels)) return labels.map(String);
  return first ? Object.keys(first).map(String).sort((a,b)=>Number(a)-Number(b) || a.localeCompare(b)) : [];
}
function simplexPoint(probabilityDict, classOrder){
  if(!probabilityDict || classOrder.length !== 3) return null;
  const p0 = Number(probabilityDict[classOrder[0]]), p1 = Number(probabilityDict[classOrder[1]]), p2 = Number(probabilityDict[classOrder[2]]);
  if(![p0,p1,p2].every(Number.isFinite)) return null;
  const total = p0 + p1 + p2 || 1;
  return {x:(p1 + p2 * 0.5) / total, y:(p2 * 0.866) / total, probabilities:[p0/total, p1/total, p2/total]};
}
function simplexTooltip(point){
  return [
    `واقعی: ${classLabelFor(point.actual)}`,
    `پیش‌بینی: ${classLabelFor(point.predicted)}`,
    ...point.classOrder.map((id,i)=>`${classLabelFor(id)}: ${percent(point.probabilities[i])}`),
    point.is_correct ? 'وضعیت: درست' : 'وضعیت: غلط'
  ];
}
function drawProbabilitySimplex(){
  const canvas = $('probabilitySimplex'), fallback = $('simplexFallback'), panel = $('simplexPanel');
  const probabilities = vizState.raw.class_probabilities || [];
  if(!probabilities.length){ canvas.hidden = true; fallback.hidden = false; panel.hidden = true; fallback.textContent = 'این مدل احتمال کلاس‌ها را ارائه نمی‌کند، بنابراین مثلث احتمال در دسترس نیست.'; return; }
  const classOrder = classOrderForProbabilities(vizState.raw);
  if(classOrder.length !== 3){ canvas.hidden = true; fallback.hidden = false; panel.hidden = true; fallback.textContent = 'این نمودار فقط برای طبقه‌بندی سه‌کلاسه فعال است.'; return; }
  canvas.hidden = false; fallback.hidden = true; panel.hidden = false;
  const points = probabilities.map((probabilityDict, i)=>{
    const point = simplexPoint(probabilityDict, classOrder);
    if(!point) return null;
    const actual = vizState.raw.actual_class?.[i] ?? vizState.raw.actual?.[i];
    const predicted = vizState.raw.predicted_class?.[i] ?? vizState.raw.predicted?.[i];
    const ok = vizState.raw.is_correct?.[i] ?? String(actual) === String(predicted);
    const confidence = Math.max(...point.probabilities);
    return {...point, index:i, actual, predicted, is_correct:ok, confidence, classOrder};
  }).filter(Boolean).slice(0,400);
  vizState.simplexPoints = points;
  const labelPlugin = {id:'simplexCornerLabels', afterDatasetsDraw(chart){
    const {ctx, scales:{x,y}} = chart; ctx.save(); ctx.font = '700 12px Tahoma, Arial'; ctx.fillStyle = '#0f172a'; ctx.textAlign = 'center';
    [[0,0,classOrder[0],8],[1,0,classOrder[1],8],[0.5,0.866,classOrder[2],-10]].forEach(([vx,vy,id,dy])=>ctx.fillText(classLabelFor(id), x.getPixelForValue(vx), y.getPixelForValue(vy)+dy)); ctx.restore();
  }};
  charts.simplex = new Chart(canvas, {type:'scatter', data:{datasets:[
    {label:'مرز مثلث احتمال', type:'line', data:[{x:0,y:0},{x:1,y:0},{x:0.5,y:0.866},{x:0,y:0}], borderColor:'rgba(15,23,42,.5)', borderWidth:2, pointRadius:0, fill:false, order:0},
    {label:'نقطه‌ها: رنگ = کلاس پیش‌بینی‌شده، دورخط نارنجی/قرمز = خطا', data:points, order:1, pointRadius:c=>c.raw.index===vizState.selectedSimplexPoint?8:(!c.raw.is_correct && c.raw.confidence >= .75 ? 7:4.5), pointHoverRadius:8, pointHitRadius:10, backgroundColor:c=>classColor(c.raw.predicted, classOrder), borderColor:c=>c.raw.is_correct?'#334155':'#f97316', borderWidth:c=>c.raw.is_correct?1.5:(c.raw.confidence >= .75 ? 4:3)}
  ]}, options:{parsing:false, maintainAspectRatio:false, animation:false, interaction:{mode:'nearest', intersect:true}, plugins:{legend:{display:true}, tooltip:{filter:item=>item.datasetIndex===1, callbacks:{label:c=>simplexTooltip(c.raw)}}}, onClick:(evt)=>{ const hit=charts.simplex.getElementsAtEventForMode(evt,'nearest',{intersect:true},true).find(item=>item.datasetIndex===1); if(hit) selectSimplexPoint(hit.index); }, scales:{x:{min:-.08,max:1.08,title:{display:true,text:'ترکیب احتمال کلاس‌ها'}, grid:{color:'rgba(148,163,184,.18)'}}, y:{min:-.08,max:.96,grid:{color:'rgba(148,163,184,.18)'}}}}, plugins:[labelPlugin]});
}
function selectSimplexPoint(index){
  const p = vizState.simplexPoints?.[index]; if(!p) return;
  vizState.selectedSimplexPoint = p.index;
  const probs = p.classOrder.map((id,i)=>`<span>${escapeHtml(classLabelFor(id))}</span><strong>${percent(p.probabilities[i])}</strong>`).join('');
  const message = p.is_correct ? 'این نقطه نشان می‌دهد مدل بیشترین احتمال را به کلاس درست داده است.' : 'این نقطه یک خطای هندسی مهم است؛ اگر نزدیک گوشه باشد یعنی مدل با اطمینان بالا اشتباه کرده است.';
  setPanel('simplexPanel', `<b>نمونه #${formatNumber(p.index)}</b><div class="fact-grid"><span>واقعی</span><strong>${escapeHtml(classLabelFor(p.actual))}</strong><span>پیش‌بینی</span><strong>${escapeHtml(classLabelFor(p.predicted))}</strong><span>اطمینان</span><strong>${percent(p.confidence)}</strong><span>وضعیت</span><strong>${p.is_correct?'درست':'غلط'}</strong>${probs}</div><p class="${p.is_correct?'':'warn'}">${message}</p>`);
  setPanel('pointPanel', `<b>جزئیات نقطه مثلث احتمال #${formatNumber(p.index)}</b><div class="fact-grid"><span>واقعی</span><strong>${escapeHtml(classLabelFor(p.actual))}</strong><span>پیش‌بینی</span><strong>${escapeHtml(classLabelFor(p.predicted))}</strong><span>برداشت</span><strong>${p.is_correct?'درست':'غلط'}</strong></div><p>${message}</p>`);
  charts.simplex?.update();
}

function classLabelFor(value){
  const key = String(value);
  return vizState?.raw?.class_labels?.[key] || `کلاس ${key}`;
}
function classwiseItems(){
  const entries = Object.entries(vizState?.raw?.classwise_metrics || {});
  return entries.map(([id, item])=>({id, label:item.label || classLabelFor(id), precision:Number(item.precision || 0), recall:Number(item.recall || 0), f1:Number(item.f1 || 0), support:Number(item.support || 0)}));
}
function weakestMetric(item){
  const metrics = [{name:'Precision', value:item.precision, text:'مدل وقتی این کلاس را پیش‌بینی می‌کند بیشتر خطا می‌کند.'}, {name:'Recall', value:item.recall, text:'مدل بخشی از نمونه‌های واقعی این کلاس را از دست می‌دهد.'}, {name:'F1', value:item.f1, text:'تعادل Precision و Recall برای این کلاس ضعیف‌تر است.'}];
  return metrics.sort((a,b)=>a.value-b.value)[0];
}
function drawClassificationLayer(){
  const layer = $('classificationAnalysisLayer');
  layer.hidden = isRegression();
  if(isRegression()){
    $('classwiseSummary').innerHTML = ''; $('confidentMistakes').innerHTML = ''; $('simplexFallback').textContent = '';
    return;
  }
  drawClasswisePerformance();
  drawConfidenceDistribution();
  drawProbabilitySimplex();
  renderConfidentMistakes();
}
function drawClasswisePerformance(){
  const items = classwiseItems();
  if(!items.length){ setPanel('classwisePanel','داده عملکرد کلاس‌ها در دسترس نیست.'); return; }
  const best = [...items].sort((a,b)=>b.f1-a.f1)[0];
  const weakest = [...items].sort((a,b)=>a.f1-b.f1)[0];
  const lowestRecall = [...items].sort((a,b)=>a.recall-b.recall)[0];
  $('classwiseSummary').innerHTML = [
    ['بهترین F1', best], ['ضعیف‌ترین F1', weakest], ['کمترین Recall', lowestRecall]
  ].map(([title,item])=>`<div><span>${escapeHtml(title)}</span><strong>${escapeHtml(item.label)}</strong><small>${title.includes('Recall') ? percent(item.recall) : percent(item.f1)}</small></div>`).join('');
  charts.classwisePerformance = new Chart($('classwisePerformance'), {
    type:'bar',
    data:{labels:items.map(i=>i.label), datasets:[
      {label:'Precision', data:items.map(i=>i.precision), backgroundColor:items.map(i=>i.id===weakest.id?'#fb923c':'#2563eb')},
      {label:'Recall', data:items.map(i=>i.recall), backgroundColor:items.map(i=>i.id===weakest.id?'#fdba74':'#14b8a6')},
      {label:'F1', data:items.map(i=>i.f1), backgroundColor:items.map(i=>i.id===weakest.id?'#ef4444':'#7c3aed')}
    ]},
    options:{maintainAspectRatio:false, plugins:{tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${percent(c.raw)} | support: ${formatNumber(items[c.dataIndex].support)}`}}}, onClick:(evt)=>{ const hit=charts.classwisePerformance.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectClassPerformance(items[hit.index].id); }, scales:{y:{beginAtZero:true, max:1, ticks:{callback:v=>percent(v)}, title:{display:true,text:'درصد'}}, x:{title:{display:true,text:'کلاس'}}}}
  });
}
function selectClassPerformance(classId){
  vizState.selectedClass = classId;
  const item = classwiseItems().find(x=>x.id===String(classId));
  if(!item) return;
  const weak = weakestMetric(item);
  setPanel('classwisePanel', `<b>${escapeHtml(item.label)}</b><div class="fact-grid"><span>Precision</span><strong>${percent(item.precision)}</strong><span>Recall</span><strong>${percent(item.recall)}</strong><span>F1</span><strong>${percent(item.f1)}</strong><span>Support</span><strong>${formatNumber(item.support)}</strong></div><p class="warn">ضعیف‌ترین معیار: ${escapeHtml(weak.name)} (${percent(weak.value)}). ${escapeHtml(weak.text)}</p>`);
}
function confidenceBins(confidences, isCorrect, binCount = 10){
  const bins = Array.from({length:binCount},(_,i)=>({label:`${(i/binCount).toFixed(1)}–${((i+1)/binCount).toFixed(1)}`, correct:0, incorrect:0, members:[]}));
  confidences.forEach((value,i)=>{ const n=Number(value); if(!Number.isFinite(n)) return; const b=Math.min(binCount-1, Math.max(0, Math.floor(n*binCount))); bins[b][isCorrect?.[i] ? 'correct' : 'incorrect']++; bins[b].members.push(i); });
  return bins;
}
function drawConfidenceDistribution(){
  const confidences = vizState.raw.prediction_confidence || [];
  const canvas = $('confidenceDistribution'), fallback = $('confidenceFallback'), panel = $('confidencePanel');
  if(!confidences.length){ canvas.hidden = true; fallback.hidden = false; panel.hidden = true; fallback.textContent = 'این مدل احتمال کلاس‌ها را ارائه نمی‌کند، بنابراین نمودار اطمینان در دسترس نیست.'; return; }
  canvas.hidden = false; fallback.hidden = true; panel.hidden = false;
  vizState.confidenceBins = confidenceBins(confidences, vizState.raw.is_correct || []);
  charts.confidenceDistribution = new Chart(canvas, {type:'bar', data:{labels:vizState.confidenceBins.map(b=>b.label), datasets:[{label:'درست', data:vizState.confidenceBins.map(b=>b.correct), backgroundColor:'#14b8a6'},{label:'غلط', data:vizState.confidenceBins.map(b=>b.incorrect), backgroundColor:'#f97316'}]}, options:{maintainAspectRatio:false, plugins:{tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${formatNumber(c.raw)} نمونه`}}}, onClick:(evt)=>{ const hit=charts.confidenceDistribution.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectConfidenceBin(hit.index); }, scales:{x:{stacked:false,title:{display:true,text:'بازه اطمینان'}}, y:{beginAtZero:true,title:{display:true,text:'تعداد نمونه'}}}}});
}
function selectConfidenceBin(binIndex){
  vizState.selectedConfidenceBin = binIndex;
  const bin = vizState.confidenceBins?.[binIndex]; if(!bin) return;
  const total = bin.correct + bin.incorrect, rate = total ? bin.incorrect / total : 0;
  const examples = bin.members.slice(0,6).map(i=>`<button onclick="selectPointByRawIndex(${i})"><span>#${i}</span><span>${escapeHtml(classLabelFor(vizState.raw.actual_class?.[i] ?? vizState.raw.actual[i]))} → ${escapeHtml(classLabelFor(vizState.raw.predicted_class?.[i] ?? vizState.raw.predicted[i]))}</span><b>${vizState.raw.is_correct?.[i] ? 'درست' : 'غلط'}</b></button>`).join('');
  setPanel('confidencePanel', `<b>بازه اطمینان ${escapeHtml(bin.label)}</b><div class="fact-grid"><span>درست</span><strong>${formatNumber(bin.correct)}</strong><span>غلط</span><strong>${formatNumber(bin.incorrect)}</strong><span>نرخ خطا</span><strong>${percent(rate)}</strong></div><div class="mini-list">${examples || '<p>نمونه‌ای در این بازه نیست.</p>'}</div>`);
}
function probabilityBars(probabilities){
  if(!probabilities) return '<p class="muted">این مدل احتمال کلاس‌ها را ارائه نمی‌کند.</p>';
  return `<div class="prob-mini">${Object.entries(probabilities).map(([klass,prob])=>`<div><span>${escapeHtml(classLabelFor(klass))}</span><i style="width:${Math.max(0, Math.min(100, Number(prob)*100))}%"></i><b>${percent(prob)}</b></div>`).join('')}</div>`;
}
function renderConfidentMistakes(){
  const mistakes = vizState.raw.confident_mistakes || [];
  if(!mistakes.length){ $('confidentMistakes').innerHTML = '<div class="insight-panel">اشتباه پر اطمینانی برای این مدل پیدا نشد.</div>'; return; }
  $('confidentMistakes').innerHTML = mistakes.slice(0,10).map((m,i)=>`<button class="mistake-card ${vizState.selectedMistake===i?'selected':''}" onclick="selectConfidentMistake(${i})"><span class="mistake-index">#${formatNumber(m.index)}</span><strong>${escapeHtml(m.actual_label || classLabelFor(m.actual))} → ${escapeHtml(m.predicted_label || classLabelFor(m.predicted))}</strong><em>${percent(m.confidence)}</em>${probabilityBars(m.probabilities)}</button>`).join('');
}
function selectConfidentMistake(index){
  vizState.selectedMistake = index;
  const m = (vizState.raw.confident_mistakes || [])[index]; if(!m) return;
  setPanel('pointPanel', `<b>اشتباه پر اطمینان #${formatNumber(m.index)}</b><div class="fact-grid"><span>واقعی</span><strong>${escapeHtml(m.actual_label || classLabelFor(m.actual))}</strong><span>پیش‌بینی</span><strong>${escapeHtml(m.predicted_label || classLabelFor(m.predicted))}</strong><span>اطمینان</span><strong>${percent(m.confidence)}</strong></div><p class="warn">مدل با اعتماد بالا کلاس اشتباه را انتخاب کرده است.</p>`);
  const data = vizState.confusion || buildConfusionMatrix();
  const row = data.labels.findIndex(x=>String(x)===String(m.actual)); const col = data.labels.findIndex(x=>String(x)===String(m.predicted));
  if(row >= 0 && col >= 0){ vizState.selectedConfusionCell = {row,col}; drawConfusionMatrix(); }
  renderConfidentMistakes();
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
  setPanel('pointPanel', isRegression() ? 'برای دیدن واقعی، پیش‌بینی، خطا و تفسیر، یک نقطه را انتخاب کنید.' : 'یک خانه از ماتریس خطا را انتخاب کنید تا جزئیات کلاس واقعی، کلاس پیش‌بینی‌شده و نمونه‌ها نمایش داده شود.');
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

let comparisonRequestId = 0;
let comparisonAbortController = null;

function validateComparisonData(data, task){
  if(!data || typeof data !== 'object') throw new Error('Comparison API returned an empty response.');
  if(data.task !== task) throw new Error(`Comparison API returned ${data.task || 'unknown'} data for ${task}.`);
  if(!Array.isArray(data.rows) || !data.rows.length) throw new Error('Comparison API returned no comparison rows.');
  if(!Array.isArray(data.summary_cards)) throw new Error('Comparison API returned invalid summary cards.');
  if(!data.metric_definitions || typeof data.metric_definitions !== 'object') throw new Error('Comparison API returned invalid metric definitions.');
  if(!Array.isArray(data.chart_config) || data.chart_config.length < 2) throw new Error('Comparison API returned invalid chart configuration.');
  return data;
}

async function loadComparisonData(task, signal){
  const data = await api(`/api/comparison?task=${encodeURIComponent(task)}`, {signal});
  return validateComparisonData(data, task);
}
let comparisonState = {task:'regression', selectedRow:null, data:null, loading:false, error:null};
function comparisonData(){ return comparisonState.data; }
function comparisonRows(){ return comparisonData()?.rows || []; }
function comparisonLabel(row){ return `${row.dataset_label_fa} (${row.dataset_label_en}) / ${row.model_label_fa} (${row.model_label_en})`; }
function comparisonMetricValue(row, key){ return row[key]; }
function formatMetricValue(value, kind){ return ['accuracy','weighted_f1','macro_f1','r2','normalized_rmse'].includes(kind) ? percent(value) : formatMoney(value); }
function bestComparisonRow(){ const cfg=comparisonData(); return comparisonRows().find(r=>r.id===cfg?.best?.row_id) || comparisonRows().find(r=>r.rank===1) || comparisonRows()[0]; }
function resetComparisonSelection(){ const best=bestComparisonRow(); comparisonState.selectedRow = best?.id || null; }
function metricClass(row, key){ const rows=comparisonRows(), dir=comparisonData().metric_definitions[key]?.direction; const vals=rows.map(r=>comparisonMetricValue(r,key)); const best=dir==='lower'?Math.min(...vals):Math.max(...vals); return comparisonMetricValue(row,key)===best?' best-metric':''; }
function renderComparison(){
  const cfg=comparisonData();
  if(!cfg){ renderComparisonStatus(comparisonState.error || 'داده‌ای برای مقایسه در دسترس نیست.'); return; }
  const rows=cfg.rows, best=bestComparisonRow();
  if(!comparisonState.selectedRow || !rows.some(r=>r.id===comparisonState.selectedRow)) resetComparisonSelection();
  document.querySelectorAll('.comparison-tab').forEach(btn=>{ const active=btn.dataset.comparisonTask===cfg.task; btn.classList.toggle('active',active); btn.setAttribute('aria-selected', String(active)); btn.disabled=false; });
  $('comparisonSummary').innerHTML = cfg.summary_cards.map(card=>`<article class="summary-card"><span>${escapeHtml(card.title)}</span><strong>${escapeHtml(card.value)}</strong><small>${escapeHtml(card.detail)}</small></article>`).join('');
  const reg=cfg.task==='regression';
  const cols=reg?['Dataset','Model','RMSE','MAE','R²','Normalized RMSE','Rank']:['Dataset','Model','Accuracy','Weighted F1','Macro F1','Rank'];
  $('comparisonTable').innerHTML = `<thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr class="${r.id===cfg.best.row_id?'best-row ':''}${r.id===comparisonState.selectedRow?'selected-row':''}" data-comparison-id="${r.id}"><td><b>${escapeHtml(r.dataset_label_fa)}</b><small>${escapeHtml(r.dataset_label_en)} · raw: ${escapeHtml(r.dataset_raw_name)} · id: ${escapeHtml(r.dataset_id)}</small></td><td><b>${escapeHtml(r.model_label_fa)}</b><small>${escapeHtml(r.model_label_en)} · raw: ${escapeHtml(r.model_raw_name)}</small></td>${reg?`<td class="number${metricClass(r,'rmse')}">${formatMoney(r.rmse)}</td><td class="number${metricClass(r,'mae')}">${formatMoney(r.mae)}</td><td class="number${metricClass(r,'r2')}">${percent(r.r2)}</td><td class="number${metricClass(r,'normalized_rmse')}">${percent(r.normalized_rmse)}</td>`:`<td class="number${metricClass(r,'accuracy')}">${percent(r.accuracy)}</td><td class="number${metricClass(r,'weighted_f1')}">${percent(r.weighted_f1)}</td><td class="number${metricClass(r,'macro_f1')}">${percent(r.macro_f1)}</td>`}<td><span class="rank-pill">#${formatNumber(r.rank)}</span></td></tr>`).join('')}</tbody>`;
  document.querySelectorAll('#comparisonTable tbody tr').forEach(tr=>tr.onclick=()=>selectComparisonRow(tr.dataset.comparisonId));
  renderComparisonCharts(); renderComparisonInsights(); renderComparisonDetail();
}
function selectComparisonRow(id){ comparisonState.selectedRow=id; renderComparison(); }
function renderComparisonCharts(){
  const cfg=comparisonData(), rows=cfg.rows;
  destroy('comparisonOne'); destroy('comparisonTwo');
  const [firstChart, secondChart] = cfg.chart_config;
  $('comparisonChartOneTitle').textContent=firstChart.title;
  $('comparisonChartOneHelp').textContent=cfg.metric_definitions[firstChart.metric].helper_text;
  $('comparisonChartTwoTitle').textContent=secondChart.title;
  $('comparisonChartTwoHelp').textContent=cfg.metric_definitions[secondChart.metric].helper_text;
  const labels=rows.map(comparisonLabel), colors=rows.map(r=>r.id===comparisonState.selectedRow?'#7c3aed':r.id===cfg.best.row_id?'#22c55e':'#2563eb');
  const make = (canvas, chart) => new Chart($(canvas), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: cfg.metric_definitions[chart.metric].label,
        data: rows.map(r => comparisonMetricValue(r, chart.metric)),
        backgroundColor: colors,
        borderColor: rows.map(r => r.id === cfg.best.row_id ? '#166534' : 'transparent'),
        borderWidth: 2
      }]
    },
    options: {
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {legend: {display: false}, tooltip: {callbacks: {label: c => `${cfg.metric_definitions[chart.metric].label}: ${formatMetricValue(c.raw, chart.metric)}`}}},
      onClick: (evt, els) => { if(els[0]) selectComparisonRow(rows[els[0].index].id); },
      scales: {
        x: {beginAtZero: true, ticks: {callback: v => formatMetricValue(v, chart.metric)}},
        y: {ticks: {autoSkip: false}}
      }
    }
  });
  charts.comparisonOne=make('comparisonChartOne', firstChart);
  charts.comparisonTwo=make('comparisonChartTwo', secondChart);
}
function renderComparisonInsights(){
  const insights=comparisonData().insights;
  $('comparisonInsights').innerHTML = [
    ['Overall takeaway', insights.overall_takeaway],
    ['Dataset effect', insights.dataset_effect],
    ['Model behavior', insights.model_behavior],
    ['Metric caution', insights.metric_caution]
  ].map(([h,p])=>`<article><h3>${escapeHtml(h)}</h3><p>${escapeHtml(p)}</p></article>`).join('');
}
function renderComparisonDetail(){
  const cfg=comparisonData(), row=comparisonRows().find(r=>r.id===comparisonState.selectedRow) || bestComparisonRow(), best=bestComparisonRow(), reg=cfg.task==='regression';
  const delta=reg?row.rmse-best.rmse:best.weighted_f1-row.weighted_f1;
  $('comparisonDetailPanel').innerHTML = `<h3>جزئیات انتخاب‌شده</h3><p><b>${escapeHtml(comparisonLabel(row))}</b></p><div class="fact-grid"><span>Dataset raw</span><strong>${escapeHtml(row.dataset_raw_name)}</strong><span>Model raw</span><strong>${escapeHtml(row.model_raw_name)}</strong><span>Rank</span><strong>#${formatNumber(row.rank)}</strong>${reg?`<span>RMSE</span><strong>${formatMoney(row.rmse)}</strong><span>MAE</span><strong>${formatMoney(row.mae)}</strong><span>R²</span><strong>${percent(row.r2)}</strong><span>Normalized RMSE</span><strong>${percent(row.normalized_rmse)}</strong>`:`<span>Accuracy</span><strong>${percent(row.accuracy)}</strong><span>Weighted F1</span><strong>${percent(row.weighted_f1)}</strong><span>Macro F1</span><strong>${percent(row.macro_f1)}</strong>`}</div><p>${escapeHtml(row.interpretation)}</p><p class="warn">مقایسه با بهترین: ${reg?`RMSE این انتخاب ${formatMoney(delta)} از بهترین ${delta===0?'برابر/بهتر نیست؛ خودش بهترین است':'بیشتر'} است.`:`Weighted F1 این انتخاب ${percent(delta)} ${delta===0?'با بهترین برابر است':'کمتر از بهترین'} است.`}</p>`;
}
function renderComparisonStatus(message, isLoading=false){
  destroy('comparisonOne'); destroy('comparisonTwo');
  document.querySelectorAll('.comparison-tab').forEach(btn=>{ const active=btn.dataset.comparisonTask===comparisonState.task; btn.classList.toggle('active',active); btn.setAttribute('aria-selected', String(active)); btn.disabled=false; });
  $('comparisonSummary').innerHTML = `<article class="summary-card"><span>${isLoading?'Loading':'Error'}</span><strong>${escapeHtml(message)}</strong><small>${isLoading?'Preparing comparison data':'Please try switching tasks again'}</small></article>`;
  $('comparisonTable').innerHTML = '';
  $('comparisonDetailPanel').innerHTML = isLoading ? 'در حال بارگذاری داده‌های مقایسه...' : `<p class="warn">${escapeHtml(message)}</p>`;
  $('comparisonChartOneTitle').textContent = isLoading ? 'Loading...' : 'Comparison unavailable';
  $('comparisonChartOneHelp').textContent = '';
  $('comparisonChartTwoTitle').textContent = '';
  $('comparisonChartTwoHelp').textContent = '';
  $('comparisonInsights').innerHTML = '';
}
async function reloadComparison(task=comparisonState.task){
  const requestId = ++comparisonRequestId;
  if(comparisonAbortController) comparisonAbortController.abort();
  comparisonAbortController = new AbortController();
  comparisonState = {task, selectedRow:null, data:null, loading:true, error:null};
  renderComparisonStatus('در حال بارگذاری داده‌های مقایسه...', true);
  try{
    const data = await loadComparisonData(task, comparisonAbortController.signal);
    if(requestId !== comparisonRequestId) return;
    comparisonState = {task, selectedRow:null, data, loading:false, error:null};
    resetComparisonSelection();
    renderComparison();
  }catch(e){
    if(e.name === 'AbortError' || requestId !== comparisonRequestId) return;
    comparisonState = {task, selectedRow:null, data:null, loading:false, error:e.message};
    renderComparisonStatus(`خطا در بارگذاری مقایسه: ${e.message}`);
  }
}
document.querySelectorAll('.comparison-tab').forEach(btn=>btn.onclick=()=>reloadComparison(btn.dataset.comparisonTask));
reloadComparison();
