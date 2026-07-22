(function(){
  var toggle=document.getElementById('menu-toggle'),sb=document.getElementById('sidebar');
  if(toggle&&sb){toggle.addEventListener('click',function(){sb.classList.toggle('open');});
    document.querySelector('.content').addEventListener('click',function(){sb.classList.remove('open');});}

  var box=document.getElementById('search'),out=document.getElementById('search-results'),idx=null;
  if(box){
    function load(){if(idx)return Promise.resolve(idx);
      return fetch('assets/search.json').then(function(r){return r.json();}).then(function(d){idx=d;return d;});}
    function esc(s){return s.replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
    function run(){
      var q=box.value.trim().toLowerCase();
      if(q.length<2){out.classList.remove('show');out.innerHTML='';return;}
      load().then(function(data){
        var res=[],seen={};
        for(var i=0;i<data.length&&res.length<40;i++){
          var t=data[i].t.toLowerCase(),p=data[i].p.toLowerCase(),b=(data[i].b||'').toLowerCase();
          var hit=t.indexOf(q)>-1||p.indexOf(q)>-1?1:(b.indexOf(q)>-1?2:0);
          if(hit&&!seen[data[i].u]){seen[data[i].u]=1;
            var r={t:data[i].t,p:data[i].p,u:data[i].u,s:''};
            if(hit===2){var k=b.indexOf(q);r.s=(k>40?'\u2026':'')+((data[i].b||'').substring(Math.max(0,k-40),k+60))+'\u2026';}
            res.push(r);}
        }
        if(!res.length){out.innerHTML='<div class="nores">No matches for &ldquo;'+esc(box.value)+'&rdquo;</div>';out.classList.add('show');return;}
        function hl(s){var e=esc(s),i=e.toLowerCase().indexOf(q);if(i<0)return e;
          return e.substring(0,i)+'<b>'+e.substring(i,i+q.length)+'</b>'+e.substring(i+q.length);}
        out.innerHTML=res.map(function(r){
          return '<a href="'+r.u+'">'+hl(r.t)+'<small>'+esc(r.p)+(r.s?' \u2014 '+hl(r.s):'')+'</small></a>';
        }).join('');
        out.classList.add('show');
      });
    }
    box.addEventListener('input',run);
    box.addEventListener('focus',run);
    document.addEventListener('click',function(e){
      if(!out.contains(e.target)&&e.target!==box)out.classList.remove('show');});
  }
})();
(function(){
  var el=document.getElementById('countdown');
  if(!el)return;
  var target=new Date(el.getAttribute('data-target')).getTime();
  var d=document.getElementById('cd-d'),h=document.getElementById('cd-h'),
      m=document.getElementById('cd-m'),s=document.getElementById('cd-s');
  function pad(n){return n<10?'0'+n:''+n;}
  function tick(){
    var diff=target-Date.now();
    if(diff<=0){
      el.classList.add('cd-done');
      el.querySelector('.eb-label').textContent='The English exam is here. Good luck!';
      el.querySelector('.eb-time').style.display='none';
      clearInterval(iv);return;
    }
    var days=Math.floor(diff/86400000);
    d.textContent=days;
    h.textContent=pad(Math.floor(diff/3600000)%24);
    m.textContent=pad(Math.floor(diff/60000)%60);
    s.textContent=pad(Math.floor(diff/1000)%60);
    var u=days<=7?'cd-final':days<=30?'cd-near':days<=100?'cd-mid':'';
    ['cd-mid','cd-near','cd-final'].forEach(function(c){el.classList.remove(c);});
    if(u)el.classList.add(u);
  }
  var iv=setInterval(tick,1000);tick();
})();
(function(){
  var foot=document.querySelector('.side-foot');
  if(foot){
    var b=document.createElement('button');b.className='theme-toggle';b.id='theme-toggle';
    b.textContent=document.documentElement.getAttribute('data-theme')==='dark'?'Light mode':'Dark mode';
    b.addEventListener('click',function(){
      var d=document.documentElement.getAttribute('data-theme')==='dark';
      document.documentElement.setAttribute('data-theme',d?'':'dark');
      try{localStorage.setItem('siteTheme',d?'light':'dark');}catch(e){}
      b.textContent=d?'Dark mode':'Light mode';
    });
    foot.insertBefore(b,foot.firstChild);
  }
  var t=document.createElement('button');t.id='to-top';t.setAttribute('aria-label','Back to top');t.innerHTML='&#8593;';
  t.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
  document.body.appendChild(t);
  window.addEventListener('scroll',function(){t.classList.toggle('show',window.scrollY>600);},{passive:true});
})();

(function(){
  var bar=document.createElement('div');bar.id='progress-bar';document.body.appendChild(bar);
  function upd(){var h=document.documentElement.scrollHeight-window.innerHeight;
    bar.style.width=(h>200?Math.min(100,window.scrollY/h*100):0)+'%';}
  window.addEventListener('scroll',upd,{passive:true});upd();


  document.addEventListener('click',function(e){
    var img=e.target.closest&&e.target.closest('img.content-img');
    if(!img)return;
    var ov=document.createElement('div');ov.className='lb-overlay';
    var big=document.createElement('img');big.src=img.src;big.alt=img.alt||'';
    ov.appendChild(big);ov.addEventListener('click',function(){ov.remove();});
    document.addEventListener('keydown',function esc2(ev){if(ev.key==='Escape'){ov.remove();document.removeEventListener('keydown',esc2);}});
    document.body.appendChild(ov);
  });

  var sb=document.getElementById('sidebar');
  var act=sb&&(sb.querySelector('.subnav li.active')||sb.querySelector('.toc li.active'));
  if(sb&&act){var r=act.getBoundingClientRect(),rs=sb.getBoundingClientRect();
    if(r.top>rs.bottom-80||r.top<rs.top)sb.scrollTop+=r.top-rs.top-sb.clientHeight/2;}

  try{
    var here=location.pathname.split('/').pop()||'index.html';
    if(here!=='index.html'&&here!=='404.html'){
      var tt=(document.title||'').split(' · ')[0];
      localStorage.setItem('lastPage',JSON.stringify({u:here,t:tt}));
    }else if(here==='index.html'){
      var lp=JSON.parse(localStorage.getItem('lastPage')||'null');
      var hero=document.querySelector('.hero');
      if(lp&&lp.u&&hero){
        var a=document.createElement('a');a.className='resume-chip';a.href=lp.u;
        a.innerHTML='<span class="rc-label">Resume</span> '+lp.t.replace(/[<>&]/g,'')+' →';
        hero.parentNode.insertBefore(a,hero.nextSibling);
      }
    }
  }catch(e){}
})();
(function(){
  document.addEventListener('click',function(e){
    var mk=e.target.closest&&e.target.closest('mark.anno');
    document.querySelectorAll('mark.anno.open').forEach(function(m){if(m!==mk)m.classList.remove('open');});
    if(mk){
      mk.classList.toggle('open');
      if(mk.classList.contains('open')){
        var r=mk.getBoundingClientRect();
        mk.classList.toggle('tip-up',r.bottom>window.innerHeight-260);
      }
      e.stopPropagation();
    }
    var lg=e.target.closest&&e.target.closest('.lg[data-cat]');
    if(lg){
      var cat=lg.dataset.cat,was=lg.classList.contains('active');
      document.querySelectorAll('.lg').forEach(function(b){b.classList.remove('active');});
      document.querySelectorAll('mark.anno').forEach(function(m){m.classList.remove('anno-match');});
      if(was){document.body.classList.remove('anno-filtered');}
      else{
        lg.classList.add('active');
        document.body.classList.add('anno-filtered');
        document.querySelectorAll('mark.anno-'+cat).forEach(function(m){m.classList.add('anno-match');});
      }
    }
  });
})();
