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
        var res=[];
        for(var i=0;i<data.length&&res.length<40;i++){
          var t=data[i].t.toLowerCase(),p=data[i].p.toLowerCase();
          if(t.indexOf(q)>-1||p.indexOf(q)>-1)res.push(data[i]);
        }
        if(!res.length){out.innerHTML='<div class="nores">No matches for &ldquo;'+esc(box.value)+'&rdquo;</div>';out.classList.add('show');return;}
        out.innerHTML=res.map(function(r){
          return '<a href="'+r.u+'">'+esc(r.t)+'<small>'+esc(r.p)+'</small></a>';
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
