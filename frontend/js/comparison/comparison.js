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
