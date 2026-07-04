$('load').onclick = loadAll;
$('predict').onclick = async()=>{
  const body = {task:$('task').value,dataset:$('dataset').value,model:$('model').value,input_mode:activeMode(),features:{}};
  if(activeMode()==='advanced'){
    document.querySelectorAll('#form input').forEach(i=>body.features[i.name]=Number(i.value||0));
    document.querySelectorAll('#form select[data-onehot-group]').forEach(sel=>{
      if(sel.value) body.features[sel.dataset.onehotGroup] = sel.value;
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
