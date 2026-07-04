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
