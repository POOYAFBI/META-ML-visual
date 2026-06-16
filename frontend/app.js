const $ = id => document.getElementById(id);
let charts = {}, currentFeatures = [], currentPresets = [], currentSamples = [], vizState = null, lastPrediction = null;
const faModel = {linear_regression:'Linear / Logistic', logistic_regression:'Logistic', random_forest:'RandomForest', xgboost:'XGBoost'};
const faTask = {regression:'رگرسیون', classification:'طبقه‌بندی'};
const faDataset = {baseline_dataset:'دیتاست پایه', enhanced_dataset:'دیتاست مهندسی‌شده'};
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
function valueText(value){ return isRegression() ? formatMoney(value) : `کلاس ${formatNumber(value)}`; }
function percent(value){ return `${Math.round(Number(value || 0) * 100).toLocaleString('fa-IR')}٪`; }
function escapeHtml(value){ return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function direction(error){ if(Number(error) > 0) return 'بیش‌برآورد'; if(Number(error) < 0) return 'کم‌برآورد'; return 'دقیق'; }
function severity(error, maxAbs){ const ratio = maxAbs ? Math.abs(error) / maxAbs : 0; if(ratio >= .66) return 'high'; if(ratio >= .33) return 'medium'; return 'low'; }
function pointColor(level, selected){ return selected ? '#7c3aed' : 'rgba(37, 99, 235, 0.42)'; }
function pointBorderColor(level, selected){ if(selected) return '#4c1d95'; return {low:'rgba(34, 197, 94, 0.55)', medium:'rgba(249, 115, 22, 0.55)', high:'rgba(239, 68, 68, 0.65)'}[level] || 'rgba(37, 99, 235, 0.55)'; }
function setPanel(id, html){ $(id).innerHTML = html; }

async function loadOptions(){
  const data = await api('/api/options');
  function fill(){
    const task = $('task').value, cfg = data.tasks[task];
    $('dataset').innerHTML = cfg.datasets.map(d=>`<option value="${d.id}">${d.name}</option>`).join('');
    $('model').innerHTML = cfg.models.map(m=>`<option value="${m}">${faModel[m]||m}</option>`).join('');
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
  $('form').innerHTML = currentFeatures.map(f=>`<label>${escapeHtml(f.name)}<input name="${escapeHtml(f.name)}" type="number" step="any" value="0"></label>`).join('');

  currentPresets = (await api(`/api/presets?task=${$('task').value}&dataset=${$('dataset').value}`)).presets;
  $('preset').innerHTML = currentPresets.map(p=>`<option value="${escapeHtml(p.id)}">${escapeHtml(p.label)}</option>`).join('');
  $('presetHelp').textContent = currentPresets[0]?.description || 'برای این انتخاب پریستی وجود ندارد.';
  $('preset').onchange = () => $('presetHelp').textContent = currentPresets.find(p=>p.id===$('preset').value)?.description || '';

  currentSamples = (await api('/api/samples?'+params()+'&limit=10')).samples;
  $('sample').innerHTML = currentSamples.map(s=>`<option value="${escapeHtml(s.id)}">${escapeHtml(s.label)} — هدف واقعی: ${Number(s.target).toLocaleString('fa-IR')}</option>`).join('');
  $('sampleHelp').textContent = 'این حالت یک ردیف واقعی را به بردار کامل ویژگی تبدیل می‌کند.';

  const metrics = await api('/api/metrics?'+params());
  renderMetrics(metrics.metrics);
  switchMode(); await drawCharts();
}

function renderMetrics(metrics){
  $('metrics').innerHTML = Object.entries(metrics).map(([k,v])=>`<button class="metric-chip" data-metric="${k}"><b>${k}</b><span>${Number(v).toFixed(4)}</span></button>`).join('');
  document.querySelectorAll('.metric-chip').forEach(btn=>btn.onclick=()=>explainMetric(btn.dataset.metric, metrics[btn.dataset.metric]));
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
  const points = v.actual.map((a,i)=>({x:a,y:v.predicted[i], actual:a, predicted:v.predicted[i], error:v.errors[i], index:i, severity:severity(v.errors[i], maxAbsError)})).slice(0,400);
  const bins = histogram(v.errors, 20);
  vizState = {raw:v, points, bins, maxAbsError, selectedPoint:null, selectedBin:null, selectedFeature:null};
  $('taskLesson').textContent = isRegression() ? 'رگرسیون یعنی فاصله عدد پیش‌بینی‌شده با مقدار واقعی را می‌آموزیم.' : 'طبقه‌بندی یعنی درستی کلاس و احتمال انتخاب‌شده را بررسی می‌کنیم.';
  $('scatterHelp').textContent = isRegression() ? 'هر نقطه یک پیش‌بینی عددی است؛ فاصله بیشتر یعنی خطای بیشتر.' : 'هر نقطه یک مقایسه کلاس واقعی و کلاس پیش‌بینی‌شده است؛ درست/غلط بودن مهم‌تر از فاصله عددی است.';
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
  const ctx = $('scatter');
  const bounds = scatterBounds(vizState.points);
  charts.scatter = new Chart(ctx, {
    type:'scatter',
    data:{datasets:[
      {label:'خط مرجع: پیش‌بینی ایده‌آل', data:referenceLine(bounds), type:'line', borderColor:'rgba(15, 23, 42, 0.35)', borderDash:[6,6], borderWidth:2, pointRadius:0, pointHitRadius:0, fill:false, order:0},
      {label:isRegression()?'واقعی در برابر پیش‌بینی':'کلاس واقعی در برابر کلاس پیش‌بینی', data:vizState.points, order:1, pointRadius:p=>p.raw.index===vizState.selectedPoint?7:4, pointHoverRadius:7, pointHitRadius:10, backgroundColor:p=>pointColor(p.raw.severity, p.raw.index===vizState.selectedPoint), borderColor:p=>pointBorderColor(p.raw.severity, p.raw.index===vizState.selectedPoint), borderWidth:p=>p.raw.index===vizState.selectedPoint?3:1.25}
    ]},
    options:{
      parsing:false,
      maintainAspectRatio:true,
      aspectRatio:1.08,
      animation:false,
      interaction:{mode:'nearest', intersect:true},
      plugins:{legend:{display:true, labels:{filter:item=>item.text !== 'خط مرجع: پیش‌بینی ایده‌آل'}}, tooltip:{filter:item=>item.datasetIndex === 1, callbacks:{label:c=>tooltipForPoint(c.raw)}}},
      onClick:(evt)=>{ const hit=charts.scatter.getElementsAtEventForMode(evt,'nearest',{intersect:true},true).find(item=>item.datasetIndex===1); if(hit) selectPoint(hit.index); },
      scales:{
        x:{min:bounds.min, max:bounds.max, grace:0, title:{display:true,text:isRegression()?'Actual / مقدار واقعی':'کلاس واقعی'}, grid:{color:'rgba(148, 163, 184, 0.22)'}},
        y:{min:bounds.min, max:bounds.max, grace:0, title:{display:true,text:isRegression()?'Predicted / مقدار پیش‌بینی':'کلاس پیش‌بینی'}, grid:{color:'rgba(148, 163, 184, 0.22)'}}
      }
    }
  });
}
function tooltipForPoint(p){
  if(isRegression()) return `${direction(p.error)} | خطا: ${formatSigned(p.error)} | ${severityFa[p.severity]}`;
  return Number(p.actual) === Number(p.predicted) ? `درست | کلاس ${formatNumber(p.actual)}` : `غلط | واقعی ${formatNumber(p.actual)}، پیش‌بینی ${formatNumber(p.predicted)}`;
}
function selectPoint(index){
  const p = vizState.points[index];
  vizState.selectedPoint = p.index;
  const binIndex = findBin(p.error);
  setPanel('pointPanel', `<b>${isRegression()?'جزئیات پیش‌بینی':'جزئیات طبقه‌بندی'}</b><div class="fact-grid"><span>واقعی</span><strong>${valueText(p.actual)}</strong><span>پیش‌بینی</span><strong>${valueText(p.predicted)}</strong><span>خطا</span><strong>${formatSigned(p.error)}</strong><span>برداشت</span><strong>${isRegression()?direction(p.error):(Number(p.actual)===Number(p.predicted)?'درست':'غلط')}</strong></div><p>${isRegression()?`این نمونه ${severityFa[p.severity]} خطا دارد و به بازه خطای انتخاب‌شده وصل شد.`:'در طبقه‌بندی، درست بودن کلاس از فاصله عددی مهم‌تر است.'}</p>`);
  selectBin(binIndex, false);
  charts.scatter.update();
}

function drawErrors(){
  charts.errors = new Chart($('errors'), {
    type:'bar',
    data:{labels:vizState.bins.labels, datasets:[{label:'توزیع خطا', data:vizState.bins.counts, backgroundColor:(c)=>binColor(c.dataIndex), borderColor:(c)=>c.dataIndex===vizState.selectedBin?'#7c3aed':'transparent', borderWidth:2}]},
    options:{plugins:{tooltip:{callbacks:{label:c=>`${c.raw} پیش‌بینی در بازه ${vizState.bins.labels[c.dataIndex]}`}}}, onClick:(evt)=>{ const hit=charts.errors.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectBin(hit.index, true); }, scales:{x:{title:{display:true,text:'بازه خطا'}}, y:{title:{display:true,text:'تعداد'}}}}
  });
}
function binColor(i){ if(i===vizState.selectedBin) return '#7c3aed'; const mid=vizState.bins.centers[i]; if(Math.abs(mid) < vizState.bins.step) return '#22c55e'; return mid < 0 ? '#38bdf8' : '#f97316'; }
function selectBin(index, renderScatterLink){
  vizState.selectedBin = index;
  const examples = vizState.bins.members[index].slice(0,6).map(i=>({i, actual:vizState.raw.actual[i], predicted:vizState.raw.predicted[i], error:vizState.raw.errors[i]}));
  const center = vizState.bins.centers[index];
  const label = Math.abs(center) < vizState.bins.step ? 'نزدیک به دقیق' : center < 0 ? 'کم‌برآورد' : 'بیش‌برآورد';
  setPanel('binPanel', `<b>بازه ${escapeHtml(vizState.bins.labels[index])} — ${label}</b><div class="mini-list">${examples.map(e=>`<button onclick="selectPointByRawIndex(${e.i})"><span>#${e.i}</span><span>${valueText(e.actual)} → ${valueText(e.predicted)}</span><b>${formatSigned(e.error)}</b></button>`).join('') || '<p>نمونه‌ای در این بازه نیست.</p>'}</div>`);
  charts.errors?.update();
  if(renderScatterLink) charts.scatter?.update();
}
function selectPointByRawIndex(rawIndex){ const i = vizState.points.findIndex(p=>p.index===rawIndex); if(i >= 0) selectPoint(i); }

function drawImportance(){
  const items = vizState.raw.feature_importance || [];
  charts.importance = new Chart($('importance'), {
    type:'bar',
    data:{labels:items.map(x=>x.feature), datasets:[{label:'اهمیت ویژگی', data:items.map(x=>x.importance), backgroundColor:(c)=>c.dataIndex===vizState.selectedFeature?'#7c3aed':'#14b8a6'}]},
    options:{indexAxis:'y', plugins:{tooltip:{callbacks:{label:c=>`اهمیت: ${formatNumber(c.raw)} — برای توضیح کلیک کنید`}}}, onClick:(evt)=>{ const hit=charts.importance.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectFeature(hit.index); }}
  });
}
function selectFeature(index){
  vizState.selectedFeature = index;
  const f = vizState.raw.feature_importance[index];
  const model = $('model').value;
  const modelText = model.includes('linear') || model.includes('logistic') ? 'در مدل خطی/لجستیک، این عدد از اندازه ضریب می‌آید.' : 'در مدل درختی، این عدد نشان می‌دهد ویژگی چقدر در تقسیم‌ها و تصمیم‌های مدل استفاده شده است.';
  setPanel('featurePanel', `<b>${escapeHtml(f.feature)}</b><div class="fact-grid"><span>رتبه</span><strong>${formatNumber(index+1)}</strong><span>اهمیت</span><strong>${formatNumber(f.importance)}</strong></div><p>${modelText}</p><p class="warn">هشدار آموزشی: اهمیت کلی ویژگی به معنی علت قطعی یا توضیح یک پیش‌بینی خاص نیست.</p>`);
  const context = $('featureContext');
  if(context) context.textContent = `ویژگی انتخاب‌شده: ${f.feature}. این یک نشانه کلی از رفتار مدل است، نه دلیل قطعی همین پیش‌بینی.`;
  charts.importance.update();
}

function histogram(values, n){
  const nums = values.map(Number), min=Math.min(...nums), max=Math.max(...nums), step=(max-min||1)/n, counts=Array(n).fill(0), members=Array.from({length:n},()=>[]);
  nums.forEach((x,i)=>{ const b=Math.min(n-1, Math.floor((x-min)/step)); counts[b]++; members[b].push(i); });
  return {labels:counts.map((_,i)=>`${(min+i*step).toFixed(1)} تا ${(min+(i+1)*step).toFixed(1)}`), centers:counts.map((_,i)=>min+(i+.5)*step), counts, members, min, max, step};
}
function findBin(error){ return Math.min(vizState.bins.counts.length-1, Math.max(0, Math.floor((Number(error)-vizState.bins.min)/vizState.bins.step))); }
function resetPanels(){
  setPanel('pointPanel','برای دیدن واقعی، پیش‌بینی، خطا و تفسیر، یک نقطه را انتخاب کنید.');
  setPanel('binPanel','یک ستون خطا را انتخاب کنید تا نمونه‌های آن بازه نمایش داده شود.');
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
  const range = data.prediction_range ? `${formatMoney(data.prediction_range.lower)} — ${formatMoney(data.prediction_range.upper)}` : null;
  const probs = data.class_probabilities ? Object.entries(data.class_probabilities).map(([klass, prob]) => `
    <div class="probability-row"><span>کلاس ${escapeHtml(klass)}</span><div class="probability-track"><i style="width:${Math.max(0, Math.min(100, Number(prob)*100))}%"></i></div><strong>${percent(prob)}</strong></div>`).join('') : '';
  const confidenceTip = resultIsRegression ? 'در رگرسیون، اعتماد از RMSE نسبت به میانگین هدف ساخته شده و یعنی پیش‌بینی یک تخمین همراه با خطاست.' : 'در طبقه‌بندی، اعتماد همان احتمال کلاس انتخاب‌شده است؛ احتمال‌های نزدیک یعنی مدل مرددتر است.';
  $('resultCard').className = `result-card reliability-${reliability}`;
  $('resultCard').innerHTML = `
    <div class="result-topline"><span>${title}</span><span class="badge">قابلیت اتکا: ${reliabilityFa[reliability] || reliability}</span></div>
    <div class="prediction-value">${mainValue}</div>
    ${range ? `<div class="range-line" title="این بازه از خطای RMSE ساخته شده و یعنی خروجی عددی دقیق و قطعی نیست.">بازه پیش‌بینی: ${range}</div>` : ''}
    <div class="confidence-block explainer" title="${escapeHtml(confidenceTip)}"><div><b>اعتماد مدل</b><span>${percent(confidence)}</span></div><div class="progress"><i style="width:${Math.max(0, Math.min(100, confidence * 100))}%"></i></div><small>${escapeHtml(confidenceTip)}</small></div>
    <div class="info-panel"><div><small>مدل</small><b>${escapeHtml(faModel[meta.model_name] || meta.model_name || '-')}</b></div><div><small>دیتاست</small><b>${escapeHtml(faDataset[meta.dataset_used] || meta.dataset_used || '-')}</b></div><div><small>نوع مسئله</small><b>${escapeHtml(faTask[meta.task_type] || meta.task_type || '-')}</b></div></div>
    <div class="analysis"><b>تحلیل</b><p>${escapeHtml(data.analysis?.explanation || '')}</p><p id="featureContext" class="muted">با انتخاب یک ویژگی از نمودار اهمیت، ارتباط کلی آن با رفتار مدل اینجا نمایش داده می‌شود.</p></div>
    ${probs ? `<div class="probabilities"><b>احتمال کلاس‌ها</b>${probs}</div>` : ''}`;
}

$('load').onclick = loadAll;
$('predict').onclick = async()=>{
  const body = {task:$('task').value,dataset:$('dataset').value,model:$('model').value,input_mode:activeMode(),features:{}};
  if(activeMode()==='advanced') document.querySelectorAll('#form input').forEach(i=>body.features[i.name]=Number(i.value||0));
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
