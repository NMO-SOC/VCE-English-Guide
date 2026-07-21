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
        out.innerHTML=res.map(function(r){
          return '<a href="'+r.u+'">'+esc(r.t)+'<small>'+esc(r.p)+(r.s?' \u2014 '+esc(r.s):'')+'</small></a>';
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
    d.textContent=Math.floor(diff/86400000);
    h.textContent=pad(Math.floor(diff/3600000)%24);
    m.textContent=pad(Math.floor(diff/60000)%60);
    s.textContent=pad(Math.floor(diff/1000)%60);
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
