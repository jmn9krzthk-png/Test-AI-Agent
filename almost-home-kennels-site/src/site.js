/* Almost Home Kennels – shared site script. Each block runs only if its markup is on the page. */
(function(){
  'use strict';
  var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
  var IMG=(document.body.getAttribute('data-img')||'img/');
  var store={get:function(k,d){try{var v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(_){return d}},set:function(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}}};
  var money=function(n){return '$'+n.toLocaleString('en-US')};
  var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
  var today=new Date();today.setHours(12,0,0,0);
  var iso=function(d){var z=new Date(d.getTime()-d.getTimezoneOffset()*6e4);return z.toISOString().slice(0,10)};
  var addDays=function(d,n){var x=new Date(d);x.setDate(x.getDate()+n);return x};
  var nice=function(d,o){return d.toLocaleDateString('en-US',o||{weekday:'short',month:'short',day:'numeric'})};
  var PORTAL='https://almosthomekennelsmo.propetware.com';
  var RATE={adult:43,pup:47,day:36};

  /* ---------- mobile menu ---------- */
  var mt=$('#menuToggle');
  if(mt){mt.addEventListener('click',function(){var o=mt.getAttribute('aria-expanded')!=='true';mt.setAttribute('aria-expanded',o);document.body.classList.toggle('menu-open',o)});
    $$('#siteNav a').forEach(function(a){a.addEventListener('click',function(){mt.setAttribute('aria-expanded','false');document.body.classList.remove('menu-open')})});}

  /* ---------- services tabs ---------- */
  var SVC=[
    {k:'Boarding',title:'Overnight boarding',img:'svc-boarding.jpg',alt:'A doodle relaxing on a daybed with a plaid blanket',price:['$43','/ night'],desc:'Thoughtful care, supervision and attention for a comfortable overnight stay.',list:['Supervised outdoor play through the day','A clean, comfortable space in our temperature-controlled buildings','Your dog\u2019s own food on their usual schedule','Medication management arranged in advance'],note:'Puppies 8 months & under: $47 / night. Pick up by 12 PM on your last day for no extra charge.',href:'boarding'},
    {k:'Daycare',title:'Daycare',img:'svc-daycare.jpg',alt:'A team member at a picnic table in the shaded play yard with several dogs',price:['$36','/ day'],desc:'A full day of supervised group play, fresh air and rest breaks. Your dog comes home happy and tired.',list:['Group play matched to your dog\u2019s style','Rest breaks worked into the day','Familiar faces who know your dog'],note:'Daycare is open to dogs who have completed the new-client trial day.',href:'daycare'},
    {k:'Baths & nails',title:'Baths & nail care',img:'svc-bath.jpg',alt:'A black Lab standing happily in the bathing tub',price:['Add-on',''],desc:'Send them home fresh. Add a bath, nail trim or nail grind to any daycare or boarding reservation.',list:['Baths','Nail trims','Nail grinding'],note:'We don\u2019t offer full-service haircuts or breed-specific grooming. Please schedule add-ons in advance.',href:'baths'},
    {k:'Enrichment',title:'Enrichment & one-on-one care',img:'svc-enrich.jpg',alt:'A spotted dog solving a treat puzzle toy',price:['Add-on',''],desc:'Extra individual attention and mental stimulation that lets dogs use their natural instincts.',list:['Snuffle mats and food puzzles','Lick mats and stuffed toys','One-on-one time with our team','Photo updates sent to you (add-on)'],note:'Add enrichment when booking or ask our team which options suit your dog.',href:'enrichment'},
    {k:'Trial day',title:'New-client trial day',img:'svc-trial.jpg',alt:'A papillon sitting in a colorful ball pit',price:['$36','/ dog'],desc:'Every new dog starts with a full day of daycare so we can get to know them.',list:['Drop off 8\u20139 AM, pick up 3\u20135 PM','Monday, Wednesday, Thursday & Friday','By appointment only'],note:'Some dogs may need extra daycare days or an overnight before full approval. We\u2019ll tell you what we recommend.',href:'newclients'}
  ];
  var tabs=$('#svcTabs');
  if(tabs){
    var links=JSON.parse(tabs.getAttribute('data-links')||'{}');
    SVC.forEach(function(s,i){var b=document.createElement('button');b.type='button';b.className='chip';b.setAttribute('role','tab');b.id='tab'+i;b.textContent=s.k;b.setAttribute('aria-selected',i===0);b.setAttribute('aria-controls','svcPanel');b.onclick=function(){showSvc(i)};tabs.appendChild(b)});
    var showSvc=function(i){
      var s=SVC[i];
      $$('#svcTabs .chip').forEach(function(b,j){b.setAttribute('aria-selected',j===i)});
      var img=$('#svcImg');img.style.opacity=0;
      setTimeout(function(){img.src=IMG+s.img;img.alt=s.alt;img.style.opacity=1},150);
      $('#svcTitle').textContent=s.title;
      $('#svcPrice').innerHTML='<b>'+esc(s.price[0])+'</b><span>'+esc(s.price[1])+'</span>';
      $('#svcDesc').textContent=s.desc;
      $('#svcList').innerHTML=s.list.map(function(t){return '<li>'+esc(t)+'</li>'}).join('');
      $('#svcNote').textContent=s.note;
      var more=$('#svcMore');if(more&&links[s.href]){more.href=links[s.href];more.textContent='More about '+s.title.toLowerCase()+' \u2192'}
      $('#svcPanel').setAttribute('aria-labelledby','tab'+i);
    };
    tabs.addEventListener('keydown',function(e){var bs=$$('#svcTabs .chip');var i=bs.indexOf(document.activeElement);if(i<0)return;var n=e.key==='ArrowRight'?i+1:e.key==='ArrowLeft'?i-1:null;if(n===null)return;n=(n+bs.length)%bs.length;bs[n].focus();showSvc(n)});
    showSvc(0);
  }

  /* ---------- stay estimator ---------- */
  if($('#estimate-tool')){
    var din=addDays(today,14),dout=addDays(din,4);
    $('#e-in').value=iso(din);$('#e-out').value=iso(dout);$('#e-in').min=iso(today);$('#e-out').min=iso(today);
    var est={adults:1,pups:0,daycare:0};
    $$('#estimate-tool .stepper').forEach(function(st){
      var key=st.getAttribute('data-key'),out=st.querySelector('output');
      $$('button',st).forEach(function(b){b.addEventListener('click',function(){
        var max=key==='daycare'?14:6;
        est[key]=Math.max(0,Math.min(max,est[key]+ +b.getAttribute('data-d')));
        if(est.adults+est.pups===0)est[key]=1;
        out.textContent=est[key];calc();
      })});
    });
    $$('#addons .chip').forEach(function(c){c.addEventListener('click',function(){c.setAttribute('aria-pressed',c.getAttribute('aria-pressed')!=='true');calc()})});
    ['#e-in','#e-out'].forEach(function(s){$(s).addEventListener('change',calc)});
    var calc=function(){
      $$('#estimate-tool .stepper').forEach(function(st){var k=st.getAttribute('data-key'),bs=$$('button',st);bs[0].disabled=est[k]===0||(k!=='daycare'&&est.adults+est.pups===1&&est[k]===1);bs[1].disabled=est[k]>=(k==='daycare'?14:6)});
      var a=new Date($('#e-in').value+'T12:00'),b=new Date($('#e-out').value+'T12:00');
      var nights=Math.round((b-a)/864e5);if(!isFinite(nights)||nights<0)nights=0;
      var lines=[],total=0,pl=function(n,w){return n+' '+w+(n===1?'':'s')};
      if(est.adults){var t=nights*est.adults*RATE.adult;total+=t;lines.push([est.adults+' adult \u00d7 '+pl(nights,'night')+' \u00d7 $43',t])}
      if(est.pups){var t2=nights*est.pups*RATE.pup;total+=t2;lines.push([est.pups+' puppy \u00d7 '+pl(nights,'night')+' \u00d7 $47',t2])}
      var dogs=est.adults+est.pups;
      if(est.daycare){var t3=est.daycare*dogs*RATE.day;total+=t3;lines.push([pl(est.daycare,'daycare day')+' \u00d7 '+pl(dogs,'dog')+' \u00d7 $36',t3])}
      var ad=$$('#addons .chip[aria-pressed="true"]').map(function(c){return c.textContent});
      var h=lines.map(function(l){return '<div><span>'+esc(l[0])+'</span><b>'+money(l[1])+'</b></div>'}).join('');
      if(ad.length)h+='<div><span>Add-ons: '+esc(ad.join(', '))+'</span><b>quoted</b></div>';
      $('#eLines').innerHTML=h;
      $('#eTotal').textContent=money(total)+(ad.length?' +':'');
      $('#eNote').textContent=nights===0?'Choose a pick-up date after your drop-off date.':'Pick up by 12 PM on your last day for no extra charge. Major holidays may need a $50 nonrefundable deposit.';
    };
    calc();
  }

  /* ---------- gallery + lightbox ---------- */
  var G=[
    ['g-0353-2.jpg','play','Leaping for a spray of water in the play yard'],
    ['g-6597.jpg','play','An Aussie posing on a tree stump with friends behind'],
    ['g-6316.jpg','play','A schnauzer and a poodle saying hello'],
    ['g-d6374.jpg','people','A big hug and kiss from a golden friend'],
    ['g-6486.jpg','rest','A husky stretched out for a nap'],
    ['g-0361.jpg','enrich','Standing proud in the ball pit'],
    ['g-6455.jpg','play','A dachshund grinning in the sunshine'],
    ['g-6466.jpg','rest','A beagle with a chew toy on a cozy bed'],
    ['g-d6305.jpg','people','Cuddles with a black Lab and a yellow Lab'],
    ['g-6322.jpg','play','A puppy with a stuffed toy, ready to play'],
    ['g-6544.jpg','rest','Sunny-window nap on the daybed'],
    ['g-1159.jpg','play','Lounging on the patio after a run'],
    ['g-6562.jpg','people','A dachshund getting a gentle head rub'],
    ['svc-enrich.jpg','enrich','Working out a treat puzzle'],
    ['g-6422.jpg','rest','A bully mix sound asleep on a soft bed'],
    ['g-d6359.jpg','people','Two of our team with their doodle and Lab pals'],
    ['g-6546.jpg','play','All smiles on top of the table'],
    ['g-6468.jpg','rest','Belly-up and totally relaxed'],
    ['g-6611.jpg','enrich','A little white pup coming to say hi'],
    ['g-1167.jpg','people','Getting some one-on-one time in the yard'],
    ['g-6550.jpg','rest','A hound napping by the couch'],
    ['g-6333.jpg','rest','A papillon perched on a pink blanket'],
    ['g-0627.jpg','rest','A black Lab tucked in on the sofa'],
    ['g-6669.jpg','enrich','Selfie with a Pomeranian mix'],
    ['g-d6306.jpg','people','Lots of love between a handler and her dogs'],
    ['g-6427.jpg','rest','A poodle mix on a raised cot'],
    ['g-6423.jpg','rest','Curled up in a dog bed under the table'],
    ['g-6315.jpg','rest','A yellow Lab in a sea of blankets']
  ];
  var gal=$('#gal');
  if(gal){
    var only=gal.getAttribute('data-only'),limit=+(gal.getAttribute('data-limit')||0);
    var items=G.map(function(g,i){return {f:g[0],c:g[1],a:g[2],i:i}}).filter(function(g){return !only||only.split(',').indexOf(g.c)>-1});
    if(limit)items=items.slice(0,limit);
    items.forEach(function(g){var b=document.createElement('button');b.type='button';b.setAttribute('data-c',g.c);b.setAttribute('data-i',g.i);b.setAttribute('aria-label','Open photo: '+g.a);
      b.innerHTML='<img loading="lazy" decoding="async" src="'+IMG+'t-'+g.f+'" alt="'+esc(g.a)+'">';b.onclick=function(){openLb(g.i)};gal.appendChild(b)});
    $$('#galFilters .chip').forEach(function(c){c.addEventListener('click',function(){var f=c.getAttribute('data-f');$$('#galFilters .chip').forEach(function(x){x.setAttribute('aria-pressed',x===c)});$$('#gal button').forEach(function(b){b.hidden=!(f==='all'||b.getAttribute('data-c')===f)})})});
    var lb=$('#lb'),cur=0,lastFocus=null;
    var visible=function(){return $$('#gal button').filter(function(b){return !b.hidden}).map(function(b){return +b.getAttribute('data-i')})};
    var showLb=function(){var g=G[cur];$('#lbImg').src=IMG+g[0];$('#lbImg').alt=g[2];var v=visible();$('#lbCap').textContent=g[2]+'  \u00b7  '+(v.indexOf(cur)+1)+' / '+v.length};
    var openLb=function(i){cur=i;lastFocus=document.activeElement;showLb();lb.hidden=false;document.body.style.overflow='hidden';$('.close',lb).focus()};
    var step=function(d){var v=visible();cur=v[(v.indexOf(cur)+d+v.length)%v.length];showLb()};
    var closeLb=function(){lb.hidden=true;document.body.style.overflow='';if(lastFocus)lastFocus.focus()};
    $('.prev',lb).onclick=function(){step(-1)};$('.next',lb).onclick=function(){step(1)};$('.close',lb).onclick=closeLb;
    lb.addEventListener('click',function(e){if(e.target===lb)closeLb()});
    document.addEventListener('keydown',function(e){if(lb.hidden)return;if(e.key==='Escape')closeLb();if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1)});
    var sx=null;lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX},{passive:true});lb.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>50)step(dx<0?1:-1);sx=null});
  }

  /* ---------- fit check ---------- */
  if($('#fit')){
    var fit=function(){
      var n=$$('#fit .switch:checked').length,tot=$$('#fit .switch').length;
      $('#fitBar').style.width=(n/tot*100)+'%';
      var m=$('#fitMsg');m.classList.toggle('ok',n===tot);
      m.textContent=n===tot?'Sounds like a great fit! Create your portal account and we\u2019ll set up your tour and trial day.':n===0?'0 of '+tot+' checked. Keep going!':n+' of '+tot+' checked. Each one is required before a trial day. Questions? Give us a call.';
    };
    $$('#fit .switch').forEach(function(s){s.addEventListener('change',fit)});fit();
  }

  /* ---------- trial day picker ---------- */
  var days=$('#days');
  if(days){
    var DN=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],OPEN=[1,3,4,5];
    for(var k=1;k<=14;k++)(function(d){
      var b=document.createElement('button');b.type='button';b.className='day';
      var open=OPEN.indexOf(d.getDay())>-1;b.disabled=!open;b.setAttribute('aria-pressed','false');
      b.innerHTML='<small>'+DN[d.getDay()]+'</small><b>'+d.getDate()+'</b><small>'+d.toLocaleString('en-US',{month:'short'})+'</small>';
      b.setAttribute('aria-label',nice(d,{weekday:'long',month:'long',day:'numeric'})+(open?'':' (no trial days)'));
      b.onclick=function(){$$('#days .day').forEach(function(x){x.setAttribute('aria-pressed',x===b)});var m=$('#dayMsg');m.classList.add('ok');m.textContent=nice(d,{weekday:'long',month:'long',day:'numeric'})+': drop off 8\u20139 AM, pick up 3\u20135 PM. Request this date in the client portal and we\u2019ll confirm.'};
      days.appendChild(b);
    })(addDays(today,k));
  }

  /* ---------- packing checklist ---------- */
  var boxes=$$('#pack input');
  if(boxes.length){
    var saved=store.get('ahk-pack',{});
    var pack=function(){var s={},n=0;boxes.forEach(function(b){s[b.id]=b.checked;n+=b.checked?1:0});store.set('ahk-pack',s);$('#packCount').textContent=n===boxes.length?'All packed, see you soon!':n+' of '+boxes.length+' packed';$('#packBar').style.width=(n/boxes.length*100)+'%'};
    boxes.forEach(function(b){b.checked=!!saved[b.id];b.addEventListener('change',pack)});
    $('#packReset').onclick=function(){boxes.forEach(function(b){b.checked=false});pack()};pack();
  }

  /* ---------- FAQ search (works on server-rendered <details>) ---------- */
  var fq=$('#faqQ');
  if(fq){
    var list=$$('#faqList details');
    list.forEach(function(d){d._q=d.querySelector('summary').textContent;d._a=d.querySelector('p').textContent});
    var fcat='All';
    var hi=function(t,q){t=esc(t);if(!q)return t;return t.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')};
    var render=function(){
      var q=fq.value.trim(),ql=q.toLowerCase(),shown=0;
      list.forEach(function(d){var ok=(fcat==='All'||d.getAttribute('data-cat')===fcat)&&(!ql||(d._q+' '+d._a).toLowerCase().indexOf(ql)>-1);d.hidden=!ok;if(ok)shown++;
        d.querySelector('summary').innerHTML=hi(d._q,q);d.querySelector('p').innerHTML=hi(d._a,q);if(ql&&ok)d.open=true});
      $('#faqEmpty').hidden=shown>0;
    };
    $$('#faqCats .chip').forEach(function(b){b.addEventListener('click',function(){fcat=b.getAttribute('data-cat');$$('#faqCats .chip').forEach(function(x){x.setAttribute('aria-pressed',x===b)});render()})});
    fq.addEventListener('input',render);
  }

  /* ---------- copy buttons ---------- */
  $$('[data-copy]').forEach(function(btn){btn.addEventListener('click',function(){
    var el=document.getElementById(btn.getAttribute('data-copy'));
    var ok=function(){btn.textContent='Copied';setTimeout(function(){btn.textContent='Copy'},1500)};
    var fb=function(){var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);btn.textContent='Selected'};
    try{navigator.clipboard.writeText(el.textContent.trim()).then(ok,fb)}catch(_){fb()}
  })});


  /* ---------- new client registration (open access, preview) ---------- */
  var RF=$('#regForm');
  if(RF){
    var rstep=1,rsteps=$$('.reg-step',RF),trial=null,rfiles=[];
    var rerr=function(m){var e=$('#regErr');e.hidden=!m;e.textContent=m||''};
    var ageMonths=function(){var v=$('#r-bday').value;if(!v)return null;var b=new Date(v+'T12:00');return (today.getFullYear()-b.getFullYear())*12+(today.getMonth()-b.getMonth())-(today.getDate()<b.getDate()?1:0)};
    var ageNote=function(){var m=ageMonths(),sx=($('input[name="r-sex"]:checked',RF)||{}).value||'',n=$('#regAge');
      if(m===null){n.hidden=true;return ''}
      var msg='';if(m<4)msg='Dogs need to be at least 4 months old and up to date on puppy vaccines. You can still register now and we’ll schedule the trial day once your pup is ready.';
      else if(m>8&&/intact/.test(sx))msg='Dogs over 8 months need to be spayed or neutered before they can attend.';
      n.hidden=!msg;n.textContent=msg;return msg};
    var rvalid=function(n){
      var fs=rsteps[n-1],ok=true,first=null;
      $$('input[required],select[required]',fs).forEach(function(i){
        var bad=i.type==='radio'?!$('input[name="'+i.name+'"]:checked',fs):i.type==='checkbox'?!i.checked:!i.value.trim()||(i.type==='email'&&!/^\S+@\S+\.\S+$/.test(i.value));
        var tgt=(i.type==='radio'||i.type==='checkbox')?i.closest('.chips,.chipbox'):i;if(tgt)tgt.classList.toggle('invalid',bad);
        if(bad){ok=false;first=first||i}});
      if(!ok){rerr('Please fill in the highlighted fields.');first.focus();return false}
      if(n===4&&!trial){rerr('Pick a trial day to continue.');return false}
      rerr('');return true};
    var rshow=function(n){rstep=n;rsteps.forEach(function(f,i){f.hidden=i!==n-1});
      $$('.reg-steps li',RF).forEach(function(l,i){l.classList.toggle('on',i<n)});
      $('#regBack').hidden=n===1;$('#regNext').hidden=n===4;$('#regSubmit').hidden=n!==4;rerr('');
      RF.scrollIntoView({behavior:'smooth',block:'start'})};
    $('#regNext').onclick=function(){if(rvalid(rstep))rshow(rstep+1)};
    $('#regBack').onclick=function(){rshow(rstep-1)};
    $('#r-bday').addEventListener('change',ageNote);
    $$('input[name="r-sex"]',RF).forEach(function(i){i.addEventListener('change',ageNote)});
    RF.addEventListener('input',function(e){var t=e.target;if(t.classList)t.classList.remove('invalid');var c=t.closest&&t.closest('.chips,.chipbox');if(c)c.classList.remove('invalid')});
    var rfi=$('#r-file'),rdz=rfi.closest('.drop');
    var addFiles=function(fl){Array.prototype.forEach.call(fl,function(x){rfiles.push(x.name)});$('#regFiles').innerHTML=rfiles.map(function(n){return '<li><span>'+esc(n)+'</span><span class="badge good">Attached</span></li>'}).join('')};
    rfi.addEventListener('change',function(){addFiles(rfi.files)});
    ['dragover','dragenter'].forEach(function(ev){rdz.addEventListener(ev,function(e){e.preventDefault();rdz.classList.add('over')})});
    ['dragleave','drop'].forEach(function(ev){rdz.addEventListener(ev,function(){rdz.classList.remove('over')})});
    rdz.addEventListener('drop',function(e){e.preventDefault();addFiles(e.dataTransfer.files)});
    var rd=$('#regDays'),DN2=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    for(var k2=2;k2<=21;k2++)(function(d){if([1,3,4,5].indexOf(d.getDay())<0)return;
      var b=document.createElement('button');b.type='button';b.className='day';b.setAttribute('aria-pressed','false');
      b.innerHTML='<small>'+DN2[d.getDay()]+'</small><b>'+d.getDate()+'</b><small>'+d.toLocaleString('en-US',{month:'short'})+'</small>';
      b.setAttribute('aria-label',nice(d,{weekday:'long',month:'long',day:'numeric'}));
      b.onclick=function(){trial=d;$$('.day',rd).forEach(function(x){x.setAttribute('aria-pressed',x===b)});rerr('')};rd.appendChild(b)})(addDays(today,k2));
    RF.addEventListener('submit',function(e){e.preventDefault();if(!rvalid(4))return;
      var v=function(id){return $('#'+id).value.trim()};
      var vax=$$('.rvax',RF).filter(function(i){return i.checked}).map(function(i){return i.parentNode.textContent.trim()});
      var rows=[['Owner',v('r-first')+' '+v('r-last')],['Contact',v('r-email')+' · '+v('r-phone')],['Dog',v('r-dname')+', '+v('r-breed')],
        ['Vaccines marked current',vax.length?vax.join(', '):'None yet'],['Records attached',rfiles.length?rfiles.length+' file'+(rfiles.length===1?'':'s'):'None yet'],
        ['Requested trial day',nice(trial,{weekday:'long',month:'long',day:'numeric'})+', drop off 8–9 AM']];
      var check=document.body.getAttribute('data-img')==='/img/'?'/checklists-and-scheduling/':'checklists-and-scheduling.html';
      RF.hidden=true;var d=$('#regDone');d.hidden=false;
      d.innerHTML='<span class="eyebrow">Registration received</span><h2>Thanks, '+esc(v('r-first'))+'! We can’t wait to meet '+esc(v('r-dname'))+'.</h2>'+
        '<p class="lede">Our team will call or text you to confirm the trial day and answer any questions.</p><dl>'+rows.map(function(r){return '<dt>'+esc(r[0])+'</dt><dd>'+esc(r[1])+'</dd>'}).join('')+'</dl>'+
        ((vax.length<3||!rfiles.length)?'<p class="fit-msg">Before the trial day, please send proof of all three vaccines (Rabies, DHPP and Bordetella).</p>':'')+
        '<p class="small">Preview site: this form isn’t connected yet, so nothing was sent.</p>'+
        '<div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-green" href="'+check+'">See the packing checklist</a><button type="button" class="btn btn-line" id="regAgain">Register another dog</button></div>';
      $('#regAgain').onclick=function(){RF.reset();rfiles=[];trial=null;$('#regFiles').innerHTML='';$$('.day',rd).forEach(function(x){x.setAttribute('aria-pressed','false')});d.hidden=true;RF.hidden=false;rshow(1)};
      d.scrollIntoView({behavior:'smooth',block:'start'})});
  }

  /* ---------- client portal (front-end demo, sample data) ---------- */
  var P=$('#portal');
  if(P){
    var KEY='ahk-portal-demo';
    var seed=function(){return {
      owner:'Jamie',
      dogs:[
        {id:'d1',name:'Biscuit',breed:'Beagle mix',age:'4 yrs',photo:'t-g-6466.jpg',food:'1 cup twice a day',meds:'Allergy pill with breakfast',vax:{Rabies:iso(addDays(today,300)),DHPP:iso(addDays(today,120)),Bordetella:iso(addDays(today,21))}},
        {id:'d2',name:'Juniper',breed:'Australian Shepherd',age:'2 yrs',photo:'t-g-6597.jpg',food:'1.5 cups twice a day',meds:'None',vax:{Rabies:iso(addDays(today,500)),DHPP:iso(addDays(today,-6)),Bordetella:iso(addDays(today,200))}}
      ],
      res:[
        {id:'r1',dogs:['d1','d2'],type:'Boarding',from:iso(addDays(today,12)),to:iso(addDays(today,16)),addons:['Bath'],status:'Confirmed'},
        {id:'r2',dogs:['d2'],type:'Daycare',from:iso(addDays(today,3)),to:iso(addDays(today,3)),addons:[],status:'Requested'},
        {id:'r3',dogs:['d1'],type:'Boarding',from:iso(addDays(today,-40)),to:iso(addDays(today,-37)),addons:['Nail trim'],status:'Completed'}
      ],
      uploads:[]
    }};
    var S=store.get(KEY,null)||seed();
    var save=function(){store.set(KEY,S)};
    var D=function(s){return new Date(s+'T12:00')};
    var dogBy=function(id){for(var i=0;i<S.dogs.length;i++)if(S.dogs[i].id===id)return S.dogs[i]};
    var nightsOf=function(r){return Math.max(0,Math.round((D(r.to)-D(r.from))/864e5))};
    var costOf=function(r){var n=r.dogs.length;return r.type==='Boarding'?nightsOf(r)*RATE.adult*n:(Math.max(1,nightsOf(r)+1))*RATE.day*n};
    var vstat=function(exp){var d=Math.round((D(exp)-today)/864e5);return d<0?['bad','Expired']:d<=30?['warn','Due in '+d+' day'+(d===1?'':'s')]:['good','Current']};
    var badge=function(st){var m={Confirmed:'good',Requested:'warn',Completed:'muted',Cancelled:'bad'};return '<span class="badge '+(m[st]||'muted')+'">'+esc(st)+'</span>'};
    var toast=function(msg){var t=$('#ptoast');t.textContent=msg;t.hidden=false;clearTimeout(t._t);t._t=setTimeout(function(){t.hidden=true},3200)};

    var views={
      overview:function(){
        var up=S.res.filter(function(r){return D(r.to)>=today&&r.status!=='Cancelled'}).sort(function(a,b){return D(a.from)-D(b.from)});
        var next=up[0];var alerts=[];
        S.dogs.forEach(function(d){Object.keys(d.vax).forEach(function(v){var s=vstat(d.vax[v]);if(s[0]!=='good')alerts.push('<li><span class="badge '+s[0]+'">'+s[1]+'</span> '+esc(d.name)+'\u2019s '+v+'</li>')})});
        var h='<div class="p-grid">';
        h+='<div class="p-card p-next">'+(next?('<span class="eyebrow">Next visit</span><h3>'+esc(next.type)+' \u00b7 '+next.dogs.map(function(i){return esc(dogBy(i).name)}).join(' & ')+'</h3><p class="p-big">'+Math.max(0,Math.round((D(next.from)-today)/864e5))+' <small>days to go</small></p><p>'+nice(D(next.from))+(next.to!==next.from?' \u2013 '+nice(D(next.to)):'')+' '+badge(next.status)+'</p>'):'<h3>No upcoming visits</h3><p>Request a stay to get on the calendar.</p>')+'<button class="btn btn-coral" data-go="book" type="button">Request a stay</button></div>';
        h+='<div class="p-card"><span class="eyebrow">Needs attention</span>'+(alerts.length?'<ul class="p-alerts">'+alerts.join('')+'</ul><button class="btn btn-line" type="button" data-go="vaccines">Upload records</button>':'<p>Everything is up to date. Nice work!</p>')+'</div>';
        h+='<div class="p-card"><span class="eyebrow">Your pack</span><div class="p-pack">'+S.dogs.map(function(d){return '<button type="button" class="p-dog" data-go="dogs"><img src="'+IMG+d.photo+'" alt=""><b>'+esc(d.name)+'</b><small>'+esc(d.breed)+'</small></button>'}).join('')+'</div></div>';
        h+='</div>';return h;
      },
      reservations:function(){
        var rows=S.res.slice().sort(function(a,b){return D(b.from)-D(a.from)});
        return '<div class="p-head"><h3>Reservations</h3><button class="btn btn-coral" type="button" data-go="book">Request a stay</button></div><div class="p-table" role="table" aria-label="Reservations">'+
          rows.map(function(r){var canCancel=(r.status==='Requested'||r.status==='Confirmed')&&D(r.from)>today;
            var late=canCancel&&r.type==='Boarding'&&(D(r.from)-today)/36e5<48;
            return '<div class="p-row" role="row"><div><b>'+esc(r.type)+'</b><small>'+r.dogs.map(function(i){return esc(dogBy(i).name)}).join(', ')+(r.addons.length?' \u00b7 '+esc(r.addons.join(', ')):'')+'</small></div><div>'+nice(D(r.from))+(r.to!==r.from?' \u2013 '+nice(D(r.to)):'')+'</div><div class="num">'+money(costOf(r))+'</div><div>'+badge(r.status)+'</div><div>'+(canCancel?'<button type="button" class="linkbtn" data-cancel="'+r.id+'" '+(late?'data-late="1"':'')+'>Cancel</button>':'')+'</div></div>'}).join('')+'</div><p class="small">Estimates use standard rates. Add-ons are priced by our team when they confirm your reservation.</p>';
      },
      book:function(){
        var dIn=iso(addDays(today,7)),dOut=iso(addDays(today,10));
        return '<form id="pBook" class="p-card p-form" novalidate><h3>Request a stay</h3>'+
          '<fieldset><legend>Which dogs?</legend><div class="chips">'+S.dogs.map(function(d,i){return '<label class="chipbox" for="pb-'+d.id+'"><input type="checkbox" id="pb-'+d.id+'" value="'+d.id+'" '+(i===0?'checked':'')+'>'+esc(d.name)+'</label>'}).join('')+'</div></fieldset>'+
          '<fieldset><legend>Service</legend><div class="chips"><label class="chipbox" for="pb-board"><input type="radio" name="ptype" id="pb-board" value="Boarding" checked>Boarding</label><label class="chipbox" for="pb-day"><input type="radio" name="ptype" id="pb-day" value="Daycare">Daycare</label></div></fieldset>'+
          '<div class="row2"><div class="field"><label for="pb-in">Drop-off</label><input type="date" id="pb-in" value="'+dIn+'" min="'+iso(addDays(today,1))+'"></div><div class="field"><label for="pb-out">Pick-up</label><input type="date" id="pb-out" value="'+dOut+'" min="'+iso(addDays(today,1))+'"></div></div>'+
          '<fieldset><legend>Add-ons</legend><div class="chips">'+['Bath','Nail trim','Nail grind','Enrichment','Photo updates'].map(function(a,i){return '<label class="chipbox" for="pa-'+i+'"><input type="checkbox" id="pa-'+i+'" value="'+a+'">'+a+'</label>'}).join('')+'</div></fieldset>'+
          '<div class="field"><label for="pb-notes">Notes for our team</label><textarea id="pb-notes" rows="3" placeholder="Feeding changes, new meds, anything we should know"></textarea></div>'+
          '<p class="p-est" id="pbEst" aria-live="polite"></p><button class="btn btn-green" type="submit">Send request</button><p class="small">Requests aren\u2019t booked until our team confirms them.</p></form>';
      },
      dogs:function(){
        return '<div class="p-head"><h3>My dogs</h3></div><div class="p-dogs">'+S.dogs.map(function(d){
          return '<article class="p-card p-profile"><img src="'+IMG+d.photo+'" alt="'+esc(d.name)+'"><div><h3>'+esc(d.name)+'</h3><p class="small">'+esc(d.breed)+' \u00b7 '+esc(d.age)+'</p><dl><div><dt>Food</dt><dd>'+esc(d.food)+'</dd></div><div><dt>Medications</dt><dd>'+esc(d.meds)+'</dd></div></dl><ul class="p-vax">'+Object.keys(d.vax).map(function(v){var s=vstat(d.vax[v]);return '<li><span>'+v+'</span><span class="badge '+s[0]+'">'+s[1]+'</span><small>exp. '+nice(D(d.vax[v]),{month:'short',day:'numeric',year:'numeric'})+'</small></li>'}).join('')+'</ul></div></article>'}).join('')+'</div>';
      },
      vaccines:function(){
        return '<div class="p-card p-form"><h3>Upload vaccine records</h3><p class="small">Rabies, DHPP (Distemper/Parvo) and Bordetella must be current before every visit. Photos or PDFs from your vet work.</p>'+
          '<div class="field"><label for="pv-dog">Dog</label><select id="pv-dog">'+S.dogs.map(function(d){return '<option value="'+d.id+'">'+esc(d.name)+'</option>'}).join('')+'</select></div>'+
          '<label class="drop" for="pv-file"><input type="file" id="pv-file" accept="image/*,.pdf" multiple><b>Choose files</b><span>or drop them here</span></label>'+
          '<ul class="p-uploads">'+S.uploads.map(function(u){return '<li><span>'+esc(u.name)+'</span><small>'+esc(dogBy(u.dog)?dogBy(u.dog).name:'')+'</small><span class="badge warn">Pending review</span></li>'}).join('')+'</ul></div>';
      }
    };
    var current='overview';
    var render=function(v){current=v||current;$$('#ptabs .chip').forEach(function(b){b.setAttribute('aria-selected',b.getAttribute('data-v')===current)});$('#pview').innerHTML=views[current]();wire()};
    var estBook=function(){var f=$('#pBook');if(!f)return;var dogs=$$('input[type=checkbox][id^="pb-d"]:checked',f).length;var type=$('input[name=ptype]:checked',f).value;var r={dogs:new Array(dogs),type:type,from:$('#pb-in',f).value,to:$('#pb-out',f).value};
      var bad=!dogs||!r.from||!r.to||D(r.to)<D(r.from)||(type==='Boarding'&&r.to===r.from);
      $('#pbEst').textContent=bad?'Pick at least one dog and valid dates.':'Estimated '+money(costOf(r))+(type==='Boarding'?' for '+nightsOf(r)+' night'+(nightsOf(r)===1?'':'s'):'')+' before add-ons.';return !bad};
    var wire=function(){
      $$('[data-go]',P).forEach(function(b){b.addEventListener('click',function(){render(b.getAttribute('data-go'))})});
      $$('[data-cancel]',P).forEach(function(b){b.addEventListener('click',function(){
        if(b.getAttribute('data-armed')!=='1'){b.setAttribute('data-armed','1');b.textContent=b.getAttribute('data-late')?'Within 48 hrs, may be charged 1 night. Confirm?':'Confirm cancel?';return}
        S.res.forEach(function(r){if(r.id===b.getAttribute('data-cancel'))r.status='Cancelled'});save();render();toast('Reservation cancelled.');
      })});
      var f=$('#pBook');
      if(f){f.addEventListener('input',estBook);f.addEventListener('change',estBook);estBook();
        f.addEventListener('submit',function(e){e.preventDefault();if(!estBook())return;
          S.res.push({id:'r'+Date.now(),dogs:$$('input[type=checkbox][id^="pb-d"]:checked',f).map(function(i){return i.value}),type:$('input[name=ptype]:checked',f).value,from:$('#pb-in',f).value,to:$('#pb-out',f).value,addons:$$('input[id^="pa-"]:checked',f).map(function(i){return i.value}),status:'Requested'});
          save();render('reservations');toast('Request sent. Our team will confirm it soon.')})}
      var fi=$('#pv-file');
      if(fi){var add=function(files){Array.prototype.forEach.call(files,function(x){S.uploads.push({name:x.name,dog:$('#pv-dog').value})});save();render('vaccines');toast('Uploaded. We\u2019ll review it before your next visit.')};
        fi.addEventListener('change',function(){add(fi.files)});
        var dz=$('.drop',P);['dragover','dragenter'].forEach(function(ev){dz.addEventListener(ev,function(e){e.preventDefault();dz.classList.add('over')})});
        ['dragleave','drop'].forEach(function(ev){dz.addEventListener(ev,function(){dz.classList.remove('over')})});
        dz.addEventListener('drop',function(e){e.preventDefault();add(e.dataTransfer.files)})}
    };
    $$('#ptabs .chip').forEach(function(b){b.addEventListener('click',function(){render(b.getAttribute('data-v'))})});
    $('#pReset').addEventListener('click',function(){S=seed();save();render('overview');toast('Sample data reset.')});
    render('overview');
    $('#pGreeting').textContent='Hi, '+S.owner+'!';
  }
})();
