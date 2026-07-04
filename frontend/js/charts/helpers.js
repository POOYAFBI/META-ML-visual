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
