function renderFeatureValidation(data){
  const v = data.feature_validation || {};
  const ok = !!v.ok;
  return `<div class="validation-panel ${ok ? 'valid' : 'invalid'}"><b>Feature validation</b><span>${ok ? '✅ معتبر' : '❌ نامعتبر'}</span><small>${formatNumber(v.actual_features || 0)} / ${formatNumber(v.expected_features || 0)} features · NaN: ${formatNumber(v.nan_count || 0)}</small></div>`;
}
function renderFeaturePreview(data){
  const rows = (data.feature_preview || []).slice(0, 12).map(x=>`<tr><td>${escapeHtml(x.feature)}</td><td>${formatNumber(x.value)}</td><td>${escapeHtml(x.source)}</td></tr>`).join('');
  const builder = data.feature_builder || {};
  return `<details class="feature-preview"><summary>Feature preview — بردار ارسال‌شده به مدل</summary><p class="muted">Defaults from training means: ${formatNumber(builder.defaults_used_count || 0)} · engineered: ${(builder.engineered_features || []).map(escapeHtml).join(', ') || '-'}</p><table><thead><tr><th>Feature</th><th>Value</th><th>Source</th></tr></thead><tbody>${rows}</tbody></table></details>`;
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
    <div class="raw-output"><small>Raw model output</small><code>${escapeHtml(data.raw_model_output ?? data.prediction)}</code></div>
    ${range ? `<div class="range-line explainer" title="${escapeHtml(rangeHelp)}"><b>بازه تقریبی پیش‌بینی (${escapeHtml(rangeBasis)})</b><span>${range}</span><small>${escapeHtml(rangeHelp)}</small></div>` : ''}
    <div class="confidence-block explainer" title="${escapeHtml(confidenceTip)}"><div><b>${escapeHtml(confidenceTitle)}</b><span>${percent(confidence)}</span></div><div class="progress"><i style="width:${Math.max(0, Math.min(100, confidence * 100))}%"></i></div><small>${escapeHtml(confidenceTip)}</small></div>
    <div class="info-panel"><div><small>مدل</small><b>${escapeHtml(modelLabel(meta.model_name || '-'))}</b></div><div><small>دیتاست</small><b>${escapeHtml(datasetLabel(meta.dataset_used || '-', meta.dataset_type))}</b></div><div><small>نوع مسئله</small><b>${escapeHtml(faTask[meta.task_type] || meta.task_type || '-')}</b></div></div>
    <div class="analysis"><b>تحلیل</b><p>${escapeHtml(data.analysis?.explanation || '')}</p><p id="featureContext" class="muted">با انتخاب یک ویژگی از نمودار اهمیت، ارتباط کلی آن با رفتار مدل اینجا نمایش داده می‌شود.</p></div>
    ${renderFeatureValidation(data)}
    ${renderFeaturePreview(data)}
    ${probs ? `<div class="probabilities"><b>احتمال کلاس‌ها</b>${probs}</div>` : ''}`;
}

