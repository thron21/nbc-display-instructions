/* All parts: a panel from the top of the screen listing every piece in the booklet, grouped by colour,
   with how many of each are already ticked. Filters: whole build or the section in view, and "still needed". */
(function(){
var el=function(t,c,h){var e=document.createElement(t); if(c) e.className=c; if(h!=null) e.innerHTML=h; return e;};
var ORDER=['White','Light Bluish Grey','Dark Bluish Grey','Black','Dark Red','Reddish Brown','Tan','Lime'];
var tab=el('button','ap-tab','All parts'); tab.type='button'; tab.setAttribute('aria-expanded','false');
var back=el('div','ap-back');
var pane=el('div','ap'); pane.setAttribute('role','dialog'); pane.setAttribute('aria-label','All parts'); pane.setAttribute('aria-hidden','true');
pane.innerHTML='<div class="ap-h"><div><p class="ap-e">Pick list</p><h2 class="ap-t">All parts</h2><p class="ap-s"></p></div><button class="ap-x" type="button" aria-label="Close">×</button></div>'+
  '<div class="ap-f"><div class="ap-seg" role="group" aria-label="Which pieces"><button type="button" data-m="all" class="on">Whole build</button><button type="button" data-m="sec">This section</button></div>'+
  '<label class="ap-need"><input type="checkbox"> Still needed only</label></div><div class="ap-l"></div>';
document.body.appendChild(tab); document.body.appendChild(back); document.body.appendChild(pane);
var list=pane.querySelector('.ap-l'), sub=pane.querySelector('.ap-s'), need=pane.querySelector('.ap-need input'), segs=[].slice.call(pane.querySelectorAll('.ap-seg button'));
var mode='all', open=false, secs=[].slice.call(document.querySelectorAll('section.sec'));
function secInView(){
  var best=secs[0]; for(var i=0;i<secs.length;i++){ var r=secs[i].getBoundingClientRect(); if(r.top<window.innerHeight*0.4) best=secs[i]; }
  var cur=document.querySelector('article.step.cur, article.step.active'); if(cur) best=cur.closest('section.sec')||best;
  return best;
}
function render(){
  var scope=mode==='sec'?secInView():document, rows=[].slice.call(scope.querySelectorAll('ul.ticks li')), g={}, tot=0, on=0;
  rows.forEach(function(li){
    var pid=(li.querySelector('.pid')||{}).textContent||'', pn=li.querySelector('.pn'), name=pn?pn.firstChild.textContent.trim():'', pc=li.querySelector('.pc');
    var col=pc?pc.textContent.trim():'', sw=pc&&pc.querySelector('.sw')?pc.querySelector('.sw').style.background:'', pp=li.querySelector('.pp'), img=pp?pp.style.backgroundImage.replace(/"/g,"'"):'';
    var cb=li.querySelector('input'), k=col+'|'+pid;
    if(!g[k]) g[k]={col:col,sw:sw,pid:pid,name:name,img:img,n:0,on:0};
    g[k].n++; tot++; if(cb&&cb.checked){ g[k].on++; on++; }
  });
  var cols={}; Object.keys(g).forEach(function(k){ var x=g[k]; (cols[x.col]=cols[x.col]||[]).push(x); });
  var names=Object.keys(cols).sort(function(a,b){ var ia=ORDER.indexOf(a), ib=ORDER.indexOf(b); return (ia<0?50:ia)-(ib<0?50:ib)||a.localeCompare(b); });
  var html='';
  names.forEach(function(c){
    var items=cols[c].sort(function(a,b){return b.n-a.n||a.name.localeCompare(b.name);}), cn=0, co=0;
    items.forEach(function(x){cn+=x.n; co+=x.on;});
    var shown=need.checked?items.filter(function(x){return x.on<x.n;}):items; if(!shown.length) return;
    var label=c==='Lime'?'Lime · any colour (hidden fillers)':c;
    html+='<section class="ap-g"><h3><span class="ap-sw" style="background:'+(items[0].sw||'#ccc')+'"></span>'+label+'<span class="ap-gc">'+co+' of '+cn+' placed</span></h3><ul>';
    shown.forEach(function(x){
      var left=x.n-x.on, note=(x.pid==='3958'&&c==='Tan')?' · marker only, not a part to buy':'';
      html+='<li class="'+(left?'':'done')+'"><span class="ap-q">'+(need.checked?left:x.n)+'×</span><span class="pp" style="background-image:'+x.img+'"></span>'+
        '<span class="ap-i"><span class="ap-p">'+x.name+'</span><span class="ap-k">'+x.pid+note+'</span></span><span class="ap-d">'+(left?x.on+' of '+x.n:'all placed')+'</span></li>';
    });
    html+='</ul></section>';
  });
  list.innerHTML=html||'<p class="ap-empty">Everything here is placed.</p>';
  var where=mode==='sec'?(secInView().querySelector('h2')||{}).textContent:'Whole build';
  sub.textContent=where+' · '+tot+' pieces · '+(tot-on)+' still needed';
}
function setOpen(v){
  open=v; if(v) render();
  pane.classList.toggle('on',v); back.classList.toggle('on',v);
  pane.setAttribute('aria-hidden',v?'false':'true'); tab.setAttribute('aria-expanded',v?'true':'false');
  document.documentElement.classList.toggle('ap-lock',v);
}
tab.addEventListener('click',function(){ setOpen(!open); });
back.addEventListener('click',function(){ setOpen(false); });
pane.querySelector('.ap-x').addEventListener('click',function(){ setOpen(false); });
document.addEventListener('keydown',function(e){ if(open&&e.key==='Escape') setOpen(false); });
segs.forEach(function(b){ b.addEventListener('click',function(){ mode=b.dataset.m; segs.forEach(function(x){x.classList.toggle('on',x===b);}); render(); }); });
need.addEventListener('change',render);
document.addEventListener('change',function(e){ if(open&&e.target&&e.target.matches&&e.target.matches('ul.ticks input')) render(); });
window.MOCKITALLPARTS={open:function(){setOpen(true);},close:function(){setOpen(false);}};
})();
