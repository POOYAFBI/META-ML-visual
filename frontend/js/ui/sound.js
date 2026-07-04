(function(){
  const preferenceKey = 'mlPlaygroundSoundEnabled';
  const getEnabled = () => localStorage.getItem(preferenceKey) !== 'false';
  let ctx;
  function tone(kind='tap'){
    if(!getEnabled() || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    try{
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const now = ctx.currentTime;
      const frequency = kind === 'success' ? 740 : kind === 'select' ? 560 : 420;
      osc.type = 'sine';
      osc.frequency.setValueAtTime(frequency, now);
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.018, now + 0.006);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.055);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now); osc.stop(now + 0.07);
    }catch(_e){}
  }
  window.mlPlaygroundSound = { enable(){localStorage.setItem(preferenceKey,'true');}, disable(){localStorage.setItem(preferenceKey,'false');}, tone };
  document.addEventListener('pointerup', event => {
    const target = event.target.closest('button, select, input[type="checkbox"], input[type="radio"], summary, .cm-cell');
    if(!target || target.disabled) return;
    tone(target.tagName === 'SELECT' ? 'select' : 'tap');
  }, {passive:true});
})();
