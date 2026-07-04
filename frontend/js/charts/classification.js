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
    $('classwiseSummary').innerHTML = ''; $('confidentMistakes').innerHTML = ''; $('simplexFallback').textContent = ''; destroy('decisionBoundary');
    return;
  }
  drawClasswisePerformance();
  drawConfidenceDistribution();
  drawProbabilitySimplex();
  renderConfidentMistakes();
  setupDecisionFeatureSelectors();
  loadDecisionSurface();
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

function decisionFeatureName(feature){ return feature?.rawName || feature?.name || feature?.raw_feature || feature; }
function isOneHotFeature(feature){ return feature?.inputKind === 'oneHotOption' || String(decisionFeatureName(feature)).includes('_'); }
function selectDefaultDecisionFeatures(){
  const names = currentFeatures.map(decisionFeatureName);
  if(names.includes('GrLivArea') && names.includes('OverallQual')) return ['GrLivArea', 'OverallQual'];
  const numeric = currentFeatures.filter(f=>f.type === 'number' && !isOneHotFeature(f)).map(decisionFeatureName);
  const fallback = numeric.length >= 2 ? numeric : names;
  return [fallback[0], fallback[1] || fallback[0]].filter(Boolean);
}
function setupDecisionFeatureSelectors(){
  const xSel = $('decisionXFeature'), ySel = $('decisionYFeature');
  if(!xSel || !ySel) return;
  const options = currentFeatures.map(f=>`<option value="${escapeHtml(decisionFeatureName(f))}">${escapeHtml(humanizeFeatureName(f))}</option>`).join('');
  const previous = [xSel.value, ySel.value];
  xSel.innerHTML = options; ySel.innerHTML = options;
  const defaults = selectDefaultDecisionFeatures();
  xSel.value = currentFeatures.some(f=>decisionFeatureName(f)===previous[0]) ? previous[0] : defaults[0];
  ySel.value = currentFeatures.some(f=>decisionFeatureName(f)===previous[1]) ? previous[1] : defaults[1];
  xSel.onchange = loadDecisionSurface;
  ySel.onchange = loadDecisionSurface;
}
async function loadDecisionSurface(){
  if(isRegression()) return;
  const x = $('decisionXFeature')?.value, y = $('decisionYFeature')?.value;
  if(!x || !y) return;
  const loading = $('decisionBoundaryLoading'), error = $('decisionBoundaryError'), canvas = $('decisionBoundary');
  decisionSurfaceState = {data:null, loading:true, error:null, selectedPoint:null};
  loading.hidden = false; error.hidden = true; canvas.hidden = true; destroy('decisionBoundary');
  try{
    const data = await api(`/api/decision-surface?${params()}&x_feature=${encodeURIComponent(x)}&y_feature=${encodeURIComponent(y)}`);
    decisionSurfaceState = {data, loading:false, error:null, selectedPoint:null};
    loading.hidden = true; canvas.hidden = false;
    drawDecisionBoundary();
  }catch(e){
    decisionSurfaceState = {data:null, loading:false, error:e.message, selectedPoint:null};
    loading.hidden = true; error.hidden = false; canvas.hidden = true;
    error.textContent = `مرز تصمیم در دسترس نیست: ${e.message}`;
  }
}
function decisionClassLabel(value){ return decisionSurfaceState.data?.class_labels?.[String(value)] || classLabelFor(value); }
function decisionTooltip(point){ return [`واقعی: ${decisionClassLabel(point.actual)}`, `پیش‌بینی: ${decisionClassLabel(point.predicted)}`, `وضعیت: ${point.is_correct ? 'درست' : 'غلط'}`, `${decisionSurfaceState.data.x_feature}: ${formatNumber(point.x)}`, `${decisionSurfaceState.data.y_feature}: ${formatNumber(point.y)}`]; }
function drawDecisionBoundary(){
  const data = decisionSurfaceState.data; if(!data) return;
  const classOrder = data.classes.map(String);
  const backgroundPlugin = {id:'decisionRegionBackground', beforeDatasetsDraw(chart){
    const {ctx, chartArea, scales:{x,y}} = chart; if(!chartArea) return;
    const w = Math.abs(x.getPixelForValue(data.x_range[1]) - x.getPixelForValue(data.x_range[0])) / data.grid_size;
    const h = Math.abs(y.getPixelForValue(data.y_range[1]) - y.getPixelForValue(data.y_range[0])) / data.grid_size;
    ctx.save();
    data.grid.forEach(cell=>{ ctx.fillStyle = `${classColor(cell.predicted_class, classOrder)}33`; ctx.fillRect(x.getPixelForValue(cell.x)-w/2, y.getPixelForValue(cell.y)-h/2, w+1, h+1); });
    ctx.restore();
  }};
  charts.decisionBoundary = new Chart($('decisionBoundary'), {type:'scatter', data:{datasets:[{label:'نمونه‌های واقعی', data:data.points, pointRadius:c=>c.raw===decisionSurfaceState.selectedPoint?7:4, pointHoverRadius:7, pointHitRadius:10, backgroundColor:c=>classColor(c.raw.actual, classOrder), borderColor:c=>c.raw.is_correct?'#334155':'#f97316', borderWidth:c=>c.raw.is_correct?1.4:3}]}, options:{parsing:false, maintainAspectRatio:false, animation:false, plugins:{legend:{display:true}, tooltip:{callbacks:{label:c=>decisionTooltip(c.raw)}}}, onClick:(evt)=>{ const hit=charts.decisionBoundary.getElementsAtEventForMode(evt,'nearest',{intersect:true},true)[0]; if(hit) selectDecisionPoint(hit.index); }, scales:{x:{min:data.x_range[0], max:data.x_range[1], title:{display:true,text:data.x_feature}}, y:{min:data.y_range[0], max:data.y_range[1], title:{display:true,text:data.y_feature}}}}, plugins:[backgroundPlugin]});
}
function selectDecisionPoint(index){
  const p = decisionSurfaceState.data?.points?.[index]; if(!p) return;
  decisionSurfaceState.selectedPoint = p;
  const message = p.is_correct ? 'این نمونه در ناحیه‌ای قرار گرفته که مدل کلاس واقعی را انتخاب می‌کند.' : 'این نمونه روی ناحیه‌ای قرار گرفته که تصمیم مدل با کلاس واقعی تفاوت دارد.';
  setPanel('decisionBoundaryPanel', `<b>نمونه مرز تصمیم</b><div class="fact-grid"><span>${escapeHtml(decisionSurfaceState.data.x_feature)}</span><strong>${formatNumber(p.x)}</strong><span>${escapeHtml(decisionSurfaceState.data.y_feature)}</span><strong>${formatNumber(p.y)}</strong><span>واقعی</span><strong>${escapeHtml(decisionClassLabel(p.actual))}</strong><span>پیش‌بینی</span><strong>${escapeHtml(decisionClassLabel(p.predicted))}</strong><span>وضعیت</span><strong>${p.is_correct?'درست':'غلط'}</strong></div><p class="${p.is_correct?'':'warn'}">${message}</p>`);
  setPanel('pointPanel', `<b>نقطه انتخاب‌شده از مرز تصمیم</b><p>${message}</p>`);
  charts.decisionBoundary?.update();
}
