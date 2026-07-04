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
