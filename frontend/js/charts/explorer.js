async function drawCharts(){
  const v = await api('/api/visualization?'+params());
  destroy('scatter'); destroy('errors'); destroy('importance'); destroy('classwisePerformance'); destroy('confidenceDistribution'); destroy('simplex'); destroy('decisionBoundary');
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
function normalizeClassLabelList(value){
  if(Array.isArray(value)) return value.map(String);
  if(value && typeof value === 'object') return Object.keys(value).map(String);
  return [];
}
function normalizeDisplayLabels(displayLabels, labels){
  if(Array.isArray(displayLabels)) return displayLabels.map(String);
  if(displayLabels && typeof displayLabels === 'object') return labels.map(label=>String(displayLabels[String(label)] ?? label));
  return labels.map(String);
}
function buildConfusionMatrix(){
  const cm = vizState.raw.confusion_matrix || {};
  const fallbackLabels = Array.from(new Set([...(vizState.raw.actual_class || vizState.raw.actual || []), ...(vizState.raw.predicted_class || vizState.raw.predicted || [])])).map(String);
  const labels = normalizeClassLabelList(cm.labels).length
    ? normalizeClassLabelList(cm.labels)
    : normalizeClassLabelList(vizState.raw.class_labels).length
      ? normalizeClassLabelList(vizState.raw.class_labels)
      : fallbackLabels;
  const displayLabels = normalizeDisplayLabels(cm.display_labels || vizState.raw.class_labels, labels);
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

