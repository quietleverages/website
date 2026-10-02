
(function(){
  var doc=document, body=doc.body;
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]});}
  // filter pills (storefront)
  var pills=doc.querySelectorAll('.pill');
  if(pills.length){
    var cards=doc.querySelectorAll('.cards .card'), empty=doc.getElementById('empty');
    pills.forEach(function(p){p.addEventListener('click',function(){
      var f=p.getAttribute('data-f'), shown=0;
      pills.forEach(function(q){q.setAttribute('aria-pressed',q===p?'true':'false')});
      cards.forEach(function(c){var ok=f==='all'||c.getAttribute('data-pillar')===f;c.hidden=!ok;if(ok)shown++});
      if(empty)empty.hidden=shown>0;
    })});
  }
  // sticky buy bar: show once the hero CTA has scrolled away
  var st=doc.getElementById('sticky'), hc=doc.getElementById('herocta');
  if(st&&hc&&'IntersectionObserver' in window){
    new IntersectionObserver(function(es){es.forEach(function(e){st.classList.toggle('on',!e.isIntersecting&&e.boundingClientRect.top<0)})}).observe(hc);
  }
  // reviews: render only real entries from reviews.json
  var wrap=doc.getElementById('reviews-wrap'), list=doc.getElementById('reviews');
  if(wrap&&list&&window.fetch){
    var main=doc.querySelector('main'), slug=main&&main.getAttribute('data-slug');
    fetch('reviews.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():null}).then(function(j){
      if(!j||!j.items)return;
      var items=j.items.filter(function(i){return i&&i.text&&i.rating&&(!slug||i.slug===slug)});
      if(!slug)items=items.slice(0,3);
      if(!items.length)return;
      list.innerHTML=items.map(function(i){
        var s=new Array(Math.max(1,Math.min(5,Math.round(i.rating)))+1).join('★');
        return '<figure class="review" style="margin:0"><div class="stars" aria-label="'+esc(i.rating)+' out of 5">'+s+'</div><q>'+esc(i.text)+'</q><figcaption class="who">'+esc(i.name||'Reader')+(i.source?' · '+esc(i.source):'')+'</figcaption></figure>';
      }).join('');
      wrap.hidden=false;
      var r=doc.getElementById('rating');
      if(r&&slug){
        var avg=items.reduce(function(a,i){return a+Number(i.rating)},0)/items.length;
        r.innerHTML='<span class="stars" aria-hidden="true">★★★★★</span><span><b>'+avg.toFixed(1)+'</b> from '+items.length+' reader review'+(items.length>1?'s':'')+'</span>';
        r.hidden=false;
      }
    }).catch(function(){});
  }
})();
(function(){
  var doc=document, reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Gumroad overlay checkout: route styled buy buttons into Gumroad's overlay; plain link if its script is missing
  var hidden=doc.getElementById('gr-open');
  doc.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[data-buy]');
    if(!a||!hidden||!window.__gr)return;
    e.preventDefault(); hidden.click();
  });
  // header shadow + progress bar
  var bar=doc.querySelector('.bar'), prog=doc.getElementById('progress'), tick=false;
  function onScroll(){
    if(tick)return; tick=true;
    requestAnimationFrame(function(){
      var y=window.scrollY||0, h=doc.documentElement.scrollHeight-window.innerHeight;
      if(bar)bar.classList.toggle('scrolled',y>8);
      if(prog&&h>0)prog.style.transform='scaleX('+Math.min(1,y/h)+')';
      tick=false;
    });
  }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
  if(reduce)return;
  // scroll reveals with stagger
  var sel='.sechead,.benefit,.proofcard,.steps li,.forwho > div,.card,.gallery figure,.facts > div,.uvp > div,.method > div,.compare > div,.review,details,.offer,.flag,.related,.final > *,.statstrip > div,.proofnote,.bignum,.problem > div';
  var els=[].slice.call(doc.querySelectorAll(sel));
  els.forEach(function(el){
    var sibs=el.parentElement?[].slice.call(el.parentElement.children).filter(function(c){return c.matches(sel)}):[el];
    el.style.setProperty('--d',Math.min(sibs.indexOf(el),6)*60+'ms');
    el.classList.add('rv');
  });
  function count(el){
    var m=/^([^0-9]*)([0-9][0-9,]*(?:\.[0-9]+)?)(.*)$/.exec(el.textContent.trim());
    if(!m)return;
    var target=parseFloat(m[2].replace(/,/g,'')), dec=(m[2].split('.')[1]||'').length, comma=m[2].indexOf(',')>-1;
    if(!isFinite(target)||target>20000)return;
    var t0=null, dur=900;
    function fmt(v){var t=v.toFixed(dec);return comma?Number(t).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec}):t}
    el.textContent=m[1]+fmt(0)+m[3];
    function step(ts){
      if(t0===null)t0=ts;
      var p=Math.min(1,(ts-t0)/dur), e=1-Math.pow(1-p,3);
      el.textContent=m[1]+fmt(target*e)+m[3];
      if(p<1)requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function reveal(el){
    el.classList.add('in');
    el.querySelectorAll('.n,.bignum').forEach(count);
    if(el.matches('.n,.bignum'))count(el);
  }
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){if(e.isIntersecting){reveal(e.target);io.unobserve(e.target)}});
    },{rootMargin:'0px 0px -8% 0px',threshold:.08});
    els.forEach(function(el){io.observe(el)});
    setTimeout(function(){els.forEach(function(el){el.classList.add('in')})},3500); // safety net
  } else { els.forEach(function(el){el.classList.add('in')}); }
  // pointer tilt on the cover image (desktop, fine pointers only)
  var cover=doc.querySelector('.hero .cover');
  if(cover&&matchMedia('(hover:hover) and (pointer:fine)').matches){
    cover.addEventListener('mousemove',function(e){
      var r=cover.getBoundingClientRect(), x=(e.clientX-r.left)/r.width-.5, y=(e.clientY-r.top)/r.height-.5;
      cover.classList.remove('tilt-reset'); cover.classList.add('tilt');
      cover.style.transform='perspective(900px) rotateY('+(x*7).toFixed(2)+'deg) rotateX('+(-y*7).toFixed(2)+'deg)';
    });
    cover.addEventListener('mouseleave',function(){
      cover.classList.remove('tilt'); cover.classList.add('tilt-reset'); cover.style.transform='';
    });
  }
  // re-animate cards when the shop filter changes
  doc.querySelectorAll('.pill').forEach(function(p){p.addEventListener('click',function(){
    doc.querySelectorAll('.cards .card:not([hidden])').forEach(function(c,i){c.classList.remove('pop');void c.offsetWidth;c.style.animationDelay=(i*35)+'ms';c.classList.add('pop')});
  })});
})();


(function(){
  function init(){
  var dlg=document.getElementById('getfree'); if(!dlg||!dlg.showModal)return;
  var form=document.getElementById('gf-form'), frame=document.getElementById('gf-frame');
  var body=document.getElementById('gf-body'), done=document.getElementById('gf-done');
  var err=document.getElementById('gf-err'), btn=document.getElementById('gf-btn'), sent=false;
  function open(){body.hidden=false;done.hidden=true;sent=false;btn.disabled=false;btn.textContent='Send it to me';err.hidden=true;dlg.showModal();var f=form.querySelector('input');f&&f.focus()}
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[data-free]'); if(!a)return;
    e.preventDefault(); open();
  });
  dlg.addEventListener('click',function(e){if(e.target===dlg)dlg.close()});
  document.getElementById('gf-ok').addEventListener('click',function(){dlg.close()});
  function fail(msg,el){err.textContent=msg;err.hidden=false;if(el){el.setAttribute('aria-invalid','true');el.focus()}}
  form.addEventListener('submit',function(e){
    var f=form.elements, ok=true; err.hidden=true;
    [].forEach.call(form.querySelectorAll('input'),function(i){i.removeAttribute('aria-invalid')});
    var fn=f['fields[first_name]'], ln=f['fields[last_name]'], em=f['email_address'];
    if(!fn.value.trim()){e.preventDefault();return fail('Please add your first name.',fn)}
    if(!ln.value.trim()){e.preventDefault();return fail('Please add your last name.',ln)}
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em.value.trim())){e.preventDefault();return fail('That email does not look right.',em)}
    em.value=em.value.trim(); sent=true; btn.disabled=true; btn.textContent='Sending…';
    setTimeout(function(){ if(sent&&body.hidden===false) finish() },6000);
  });
  frame.addEventListener('load',function(){ if(sent) finish() });
  function finish(){
    if(done.hidden===false)return;
    document.getElementById('gf-addr').textContent=form.elements['email_address'].value;
    body.hidden=true; done.hidden=false;
  }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
})();
