import json, os

sounds = {
  "dieren": json.load(open("sounds_dieren.json")),
  "erf": json.load(open("sounds_erf.json")),
  "wild": json.load(open("sounds_wild.json")),
  "voertuigen": json.load(open("sounds_voertuigen.json")),
  "huis": json.load(open("sounds_huis.json")),
  "mensen": json.load(open("sounds_mensen.json")),
}
SOUNDS_JS = json.dumps(sounds, separators=(",",":"))
SCENE_DIEREN = open("scene_dieren.svg").read()
SCENE_ERF    = open("scene_erf.svg").read()
SCENE_WILD   = open("scene_wild.svg").read()
SCENE_HUIS   = open("scene_huis.svg").read()
SCENE_MENSEN = open("scene_mensen.svg").read()
SCENE_VOERT  = open("scene_voertuigen.svg").read()

HTML = r'''<title>Geluidenspel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&display=swap">
<style>
  :root{
    --sky:#8FD3F4; --grass:#A8E063; --sun:#FFD23F; --pink:#FF6B9D;
    --ink:#3D2C4E; --card:#FFFFFF; --good:#5FCB6B;
    font-family:"Baloo 2","Trebuchet MS",system-ui,sans-serif;
  }
  html,body{height:100%;margin:0;}
  body{min-height:100%;background:linear-gradient(180deg,var(--sky) 0%,#B6E3F7 42%,var(--grass) 100%);
    color:var(--ink);-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;
    touch-action:manipulation;overflow-x:hidden;}
  .wrap{position:relative;z-index:2;box-sizing:border-box;padding:14px;
    padding-block:calc(env(safe-area-inset-top,0px) + 12px) calc(env(safe-area-inset-bottom,0px) + 16px);
    max-width:1000px;margin:0 auto;}
  h1{text-align:center;font-weight:800;font-size:clamp(1.5rem,6vw,2.3rem);margin:0 0 4px;color:#fff;
    text-shadow:0 3px 0 rgba(61,44,78,.25);text-wrap:balance;}
  .subtitle{text-align:center;margin:2px 0 14px;font-weight:600;font-size:clamp(1rem,3.8vw,1.25rem);
    color:#fff;opacity:.98;text-shadow:0 2px 0 rgba(61,44,78,.2);}

  /* ---- HOME ---- */
  .theme-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;max-width:560px;margin:18px auto 0;}
  @media (max-width:460px){ .theme-grid{gap:12px;} }
  .theme-card{appearance:none;border:none;cursor:pointer;font-family:inherit;color:var(--ink);
    border-radius:28px;padding:26px 12px 20px;display:flex;flex-direction:column;align-items:center;gap:6px;
    box-shadow:0 10px 0 rgba(61,44,78,.16),0 14px 26px rgba(61,44,78,.16);transition:transform .09s ease;}
  .theme-card:active{transform:translateY(5px);box-shadow:0 5px 0 rgba(61,44,78,.16);}
  .theme-card .tEmoji{font-size:clamp(3.4rem,16vw,5rem);line-height:1;filter:drop-shadow(0 4px 3px rgba(61,44,78,.18));}
  .theme-card .tName{font-weight:800;font-size:clamp(1.1rem,4.6vw,1.5rem);}
  .theme-card.soon{cursor:default;opacity:.6;}
  .theme-card.soon:active{transform:none;}

  /* ---- topbar in theme ---- */
  .topbar{display:flex;align-items:center;gap:10px;justify-content:center;margin:0 0 8px;}
  .homebtn{appearance:none;border:none;cursor:pointer;font-family:inherit;font-weight:800;
    background:rgba(255,255,255,.65);border-radius:999px;padding:8px 16px;color:var(--ink);
    font-size:clamp(1rem,3.6vw,1.15rem);box-shadow:0 4px 0 rgba(61,44,78,.14);transition:transform .08s ease;}
  .homebtn:active{transform:translateY(3px);}

  .tabs{display:flex;gap:8px;justify-content:center;margin:0 0 8px;flex-wrap:wrap;}
  .tabs.small{margin-bottom:14px;}
  .tab{appearance:none;border:none;cursor:pointer;font-family:inherit;font-weight:800;
    font-size:clamp(.95rem,3.4vw,1.1rem);color:var(--ink);background:rgba(255,255,255,.55);
    border-radius:999px;padding:9px 18px;box-shadow:0 4px 0 rgba(61,44,78,.14);transition:transform .08s ease;}
  .tabs.small .tab{font-size:clamp(.85rem,3vw,1rem);padding:7px 15px;}
  .tab.active{background:#fff;box-shadow:0 6px 0 var(--pink);}
  .tab:active{transform:translateY(3px);}

  .grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;}
  @media (max-width:820px){ .grid{grid-template-columns:repeat(4,1fr);} }
  @media (max-width:620px){ .grid{grid-template-columns:repeat(2,1fr);gap:12px;} }
  .animal{appearance:none;border:none;cursor:pointer;font-family:inherit;background:var(--card);
    border-radius:26px;padding:14px 6px 12px;display:flex;flex-direction:column;align-items:center;gap:2px;
    box-shadow:0 8px 0 rgba(61,44,78,.16),0 12px 22px rgba(61,44,78,.14);transition:transform .08s ease;outline:none;}
  .animal:focus-visible{box-shadow:0 0 0 4px var(--pink),0 8px 0 rgba(61,44,78,.16);}
  .animal:active{transform:translateY(4px);box-shadow:0 4px 0 rgba(61,44,78,.16);}
  .emoji{font-size:clamp(3rem,14vw,4.4rem);line-height:1;filter:drop-shadow(0 4px 3px rgba(61,44,78,.18));}
  .name{font-weight:800;font-size:clamp(1rem,4vw,1.3rem);color:var(--ink);}
  .pop{animation:pop .6s ease;}
  @keyframes pop{0%{transform:scale(1) rotate(0)}25%{transform:scale(1.18) rotate(-7deg)}
    50%{transform:scale(1.12) rotate(7deg)}75%{transform:scale(1.14) rotate(-4deg)}100%{transform:scale(1) rotate(0)}}
  .shake{animation:shake .5s ease;}
  @keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-9px) rotate(-4deg)}
    40%{transform:translateX(9px) rotate(4deg)}60%{transform:translateX(-7px) rotate(-3deg)}80%{transform:translateX(7px) rotate(3deg)}}
  .right{box-shadow:0 0 0 5px var(--good),0 8px 0 rgba(61,44,78,.16) !important;}
  .choices{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;width:100%;}
  .choices .animal{flex:1 1 0;min-width:120px;max-width:210px;}

  .replay{appearance:none;border:none;cursor:pointer;font-family:inherit;display:none;
    width:clamp(96px,24vw,120px);height:clamp(96px,24vw,120px);border-radius:50%;
    background:radial-gradient(circle at 35% 32%,#fff,#FFE9F0);
    box-shadow:0 9px 0 var(--pink),0 14px 22px rgba(61,44,78,.22);
    font-size:clamp(2.8rem,11vw,3.6rem);line-height:1;color:var(--pink);
    align-items:center;justify-content:center;margin:0 auto 14px;transition:transform .08s ease;}
  .replay.show{display:flex;}
  .replay:active{transform:translateY(6px);box-shadow:0 3px 0 var(--pink);}
  .replay.playing{animation:pulse 1s ease infinite;}
  @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
  .stars{min-height:1.9rem;text-align:center;font-size:1.5rem;margin:12px 0 0;letter-spacing:2px;}

  #sceneWrap{width:100%;}
  #sceneWrap svg{width:100%;height:auto;display:block;border-radius:22px;box-shadow:0 10px 26px rgba(61,44,78,.22);}
  .animal-node{cursor:pointer;transform-box:fill-box;transform-origin:center;}
  .animal-node .hit{fill:transparent;}
  .animal-node:focus{outline:none;}
  .a-bounce{animation:abounce .6s ease;}
  @keyframes abounce{0%{transform:scale(1)}30%{transform:scale(1.17)}60%{transform:scale(.97)}100%{transform:scale(1)}}
  .a-shake{animation:ashake .5s ease;}
  @keyframes ashake{0%,100%{transform:translateX(0)}25%{transform:translateX(-6px) rotate(-4deg)}75%{transform:translateX(6px) rotate(4deg)}}
  .a-glow{filter:drop-shadow(0 0 10px #FFD23F) drop-shadow(0 0 18px #FFD23F);}

  #fx{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:5;}
  .flash{position:fixed;z-index:6;pointer-events:none;transform:translate(-50%,-50%);font-weight:800;
    font-size:clamp(1.8rem,9vw,3.4rem);color:#fff;text-shadow:0 3px 0 var(--pink),0 6px 12px rgba(61,44,78,.35);
    animation:rise 1.2s ease-out forwards;white-space:nowrap;text-align:center;}
  @keyframes rise{0%{opacity:0;transform:translate(-50%,-50%) scale(.6)}
    18%{opacity:1;transform:translate(-50%,-62%) scale(1.12)}100%{opacity:0;transform:translate(-50%,-155%) scale(1)}}
  .credit{margin:18px auto 0;text-align:center;font-size:.72rem;color:rgba(61,44,78,.55);font-weight:600;}
  [hidden]{display:none !important;}
  @media (prefers-reduced-motion:reduce){
    .pop,.shake,.a-bounce,.a-shake,.replay.playing{animation:none}.flash{animation-duration:.9s}
  }
</style>

<canvas id="fx" aria-hidden="true"></canvas>

<main class="wrap">
  <!-- HOME -->
  <section id="home">
    <h1>🔊 Geluidenspel</h1>
    <p class="subtitle">Kies een thema</p>
    <div class="theme-grid" id="themeGrid"></div>
  </section>

  <!-- THEME -->
  <section id="themeView" hidden>
    <div class="topbar">
      <button id="homeBtn" class="homebtn" type="button">🏠 Terug</button>
      <h1 id="themeTitle" style="margin:0;font-size:clamp(1.2rem,4.6vw,1.7rem)">Thema</h1>
    </div>
    <div class="tabs" id="modeTabs">
      <button id="tabPlay" class="tab active" type="button">🎨 Vrij spelen</button>
      <button id="tabQuiz" class="tab" type="button">❓ Quiz</button>
    </div>
    <div class="tabs small" id="viewTabs">
      <button id="tabTiles" class="tab active" type="button">🔲 Tegels</button>
      <button id="tabScene" class="tab" type="button">🌳 Tekening</button>
    </div>
    <p class="subtitle" id="subtitle">Tik op een plaatje!</p>
    <button id="replay" class="replay" type="button" aria-label="Nog eens luisteren">🔊</button>
    <section id="board">
      <div id="tilesFree" class="grid"></div>
      <div id="tilesQuiz" class="choices" hidden></div>
      <div id="sceneWrap" hidden></div>
    </section>
    <p class="stars" id="stars" aria-live="polite"></p>
  </section>

  <p class="credit">Echte opnames · ESC-50 (CC BY-NC) · tekeningen: illustratie</p>
</main>

<!-- scenes (hidden templates) -->
<div id="scene-dieren" hidden>__SCENE_DIEREN__</div>
<div id="scene-erf" hidden>__SCENE_ERF__</div>
<div id="scene-wild" hidden>__SCENE_WILD__</div>
<div id="scene-huis" hidden>__SCENE_HUIS__</div>
<div id="scene-mensen" hidden>__SCENE_MENSEN__</div>
<div id="scene-voertuigen" hidden>__SCENE_VOERTUIGEN__</div>

<script>
var SOUNDS = __SOUNDS__;
(function(){
  "use strict";
  var THEMES = {
    dieren: { title:"Boerderij", emoji:"🐮", sceneTab:"🌳 Boerderij", sceneName:"boerderij",
      items:[
        {emoji:"🐄",name:"Koe",key:"koe"},{emoji:"🐴",name:"Paard",key:"paard"},
        {emoji:"🫏",name:"Ezel",key:"ezel"},{emoji:"🐷",name:"Varken",key:"varken"},
        {emoji:"🐑",name:"Schaap",key:"schaap"},{emoji:"🐐",name:"Geit",key:"geit"},
        {emoji:"🐶",name:"Hond",key:"hond"},{emoji:"🐱",name:"Poes",key:"poes"}
      ]},
    erf: { title:"Het erf", emoji:"🐔", sceneTab:"🌾 Het erf", sceneName:"erf",
      items:[
        {emoji:"🐔",name:"Kip",key:"kip"},{emoji:"🐓",name:"Haan",key:"haan"},
        {emoji:"🦆",name:"Eend",key:"eend"},{emoji:"🦢",name:"Gans",key:"gans"},
        {emoji:"🦃",name:"Kalkoen",key:"kalkoen"},{emoji:"🕊️",name:"Duif",key:"duif"},
        {emoji:"🐦‍⬛",name:"Kraai",key:"kraai"},{emoji:"🐸",name:"Kikker",key:"kikker"},
        {emoji:"🐝",name:"Bij",key:"bij"},{emoji:"🐭",name:"Muis",key:"muis"}
      ]},
    wild: { title:"Wilde dieren", emoji:"🦁", sceneTab:"🌳 Jungle", sceneName:"jungle",
      items:[
        {emoji:"🦁",name:"Leeuw",key:"leeuw"},{emoji:"🐵",name:"Aap",key:"aap"},
        {emoji:"🐘",name:"Olifant",key:"olifant"},{emoji:"🐯",name:"Tijger",key:"tijger"},
        {emoji:"🦉",name:"Uil",key:"uil"},{emoji:"🐺",name:"Wolf",key:"wolf"},
        {emoji:"🦊",name:"Vos",key:"vos"},{emoji:"🦛",name:"Nijlpaard",key:"nijlpaard"},
        {emoji:"🦏",name:"Neushoorn",key:"neushoorn"},{emoji:"🦍",name:"Gorilla",key:"gorilla"},
        {emoji:"🦜",name:"Papegaai",key:"papegaai"},{emoji:"🦅",name:"Adelaar",key:"adelaar"}
      ]},
    huis: { title:"In huis", emoji:"🏠", sceneTab:"🏠 Het huis", sceneName:"huis",
      items:[
        {emoji:"🚪",name:"Kloppen",key:"kloppen"},{emoji:"⏰",name:"Wekker",key:"wekker"},
        {emoji:"🕰️",name:"Klok",key:"klok"},{emoji:"🧹",name:"Stofzuiger",key:"stofzuiger"},
        {emoji:"🧺",name:"Wasmachine",key:"wasmachine"},{emoji:"🪥",name:"Tandenborstel",key:"tandenborstel"},
        {emoji:"🚽",name:"Wc",key:"wc"},{emoji:"🚰",name:"Water",key:"water"},
        {emoji:"🥫",name:"Blikje",key:"blikje"}
      ]},
    mensen: { title:"Mensen", emoji:"👶", sceneTab:"🧸 Speelkamer", sceneName:"speelkamer",
      items:[
        {emoji:"😄",name:"Lachen",key:"lachen"},{emoji:"🤧",name:"Niezen",key:"niezen"},
        {emoji:"😷",name:"Hoesten",key:"hoesten"},{emoji:"👏",name:"Klappen",key:"klappen"},
        {emoji:"👶",name:"Baby",key:"baby"},{emoji:"👣",name:"Voetstappen",key:"voetstappen"},
        {emoji:"😴",name:"Snurken",key:"snurken"},{emoji:"🥤",name:"Drinken",key:"drinken"}
      ]},
    voertuigen: { title:"Voertuigen", emoji:"🚗", sceneTab:"🌳 Straat", sceneName:"straat",
      items:[
        {emoji:"🚗",name:"Auto",key:"auto"},{emoji:"🏍️",name:"Motor",key:"motor"},
        {emoji:"🚲",name:"Fiets",key:"fiets"},{emoji:"🚂",name:"Trein",key:"trein"},
        {emoji:"🚒",name:"Brandweer",key:"brandweer"},{emoji:"🚜",name:"Traktor",key:"traktor"},
        {emoji:"🚤",name:"Boot",key:"boot"},{emoji:"✈️",name:"Vliegtuig",key:"vliegtuig"},
        {emoji:"🚁",name:"Helikopter",key:"helikopter"}
      ]}
  };
  var THEME_ORDER=["dieren","erf","wild","voertuigen","huis","mensen"];
  var colors=["#FFE5EC","#E5F6FF","#FFF3D6","#E8FBE0","#F3E8FF","#FFEAD6","#E0F7F4","#FDE7F3","#EAF0FF","#FFF0E8"];

  /* ---- audio ---- */
  var actx=null, master=null, buffers={};
  function b64buf(b64){var bin=atob(b64),n=bin.length,u=new Uint8Array(n);for(var i=0;i<n;i++)u[i]=bin.charCodeAt(i);return u.buffer;}
  function initAudio(){
    if(actx) return;
    try{
      actx=new (window.AudioContext||window.webkitAudioContext)();
      master=actx.createGain(); master.gain.value=1.0; master.connect(actx.destination);
      Object.keys(SOUNDS).forEach(function(tid){
        var set=SOUNDS[tid];
        Object.keys(set).forEach(function(k){
          var raw=set[k],b64=raw.indexOf(",")>=0?raw.split(",")[1]:raw;
          try{ actx.decodeAudioData(b64buf(b64),function(buf){buffers[tid+"|"+k]=buf;},function(){}); }catch(e){}
        });
      });
    }catch(e){ actx=null; }
  }
  function resume(){ if(actx&&actx.state==="suspended") actx.resume(); }
  function playSample(key,cb){
    var b=buffers[theme+"|"+key];
    if(!actx||!b){ if(cb)cb(); return false; }
    var s=actx.createBufferSource(); s.buffer=b; s.connect(master); s.start(0);
    if(cb) s.onended=cb; return true;
  }
  function sparkle(){ if(!actx) return;
    var t=actx.currentTime,o=actx.createOscillator(),g=actx.createGain();
    o.type="sine";o.frequency.setValueAtTime(900,t);o.frequency.exponentialRampToValueAtTime(1700,t+0.12);
    g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(0.12,t+0.02);g.gain.exponentialRampToValueAtTime(0.0001,t+0.2);
    o.connect(g).connect(master||actx.destination);o.start(t);o.stop(t+0.22);}
  initAudio();

  /* ---- speech ---- */
  var nlVoice=null,spUnlocked=false;
  function pickVoice(){if(!("speechSynthesis" in window))return;var vs=window.speechSynthesis.getVoices();nlVoice=vs.filter(function(v){return /^nl/i.test(v.lang);})[0]||null;}
  if("speechSynthesis" in window){pickVoice();window.speechSynthesis.onvoiceschanged=pickVoice;}
  function unlockSpeech(){if(spUnlocked||!("speechSynthesis" in window))return;try{var u=new SpeechSynthesisUtterance(" ");u.volume=0;u.lang="nl-NL";window.speechSynthesis.speak(u);spUnlocked=true;}catch(e){}}
  function speak(t){if(!("speechSynthesis" in window))return;try{var s=window.speechSynthesis;s.resume();if(s.speaking||s.pending)s.cancel();var u=new SpeechSynthesisUtterance(t);u.lang="nl-NL";if(nlVoice)u.voice=nlVoice;u.rate=0.95;u.pitch=1.1;s.speak(u);}catch(e){}}

  /* ---- confetti ---- */
  var canvas=document.getElementById("fx"),ctx=canvas.getContext("2d"),parts=[];
  var reduce=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function resize(){var d=Math.min(window.devicePixelRatio||1,2);canvas.width=innerWidth*d;canvas.height=innerHeight*d;ctx.setTransform(d,0,0,d,0,0);}
  addEventListener("resize",resize);resize();
  var cc=["#FF6B9D","#FFD23F","#7BC950","#4FC3F7","#B980F0","#FF8A5C"];
  function burst(x,y,n){if(reduce)n=Math.min(n,8);for(var i=0;i<n;i++){var a=Math.random()*6.283,sp=3+Math.random()*7;
    parts.push({x:x,y:y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp-3,g:0.22+Math.random()*0.12,size:6+Math.random()*8,
      rot:Math.random()*6.28,vr:(Math.random()-.5)*0.4,life:1,color:cc[(Math.random()*cc.length)|0]});}}
  function tick(){ctx.clearRect(0,0,canvas.width,canvas.height);
    for(var i=parts.length-1;i>=0;i--){var p=parts[i];p.vy+=p.g;p.x+=p.vx;p.y+=p.vy;p.rot+=p.vr;p.life-=0.012;
      if(p.life<=0||p.y>innerHeight+40){parts.splice(i,1);continue;}
      ctx.save();ctx.globalAlpha=Math.max(p.life,0);ctx.translate(p.x,p.y);ctx.rotate(p.rot);
      ctx.fillStyle=p.color;ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size*0.6);ctx.restore();}
    requestAnimationFrame(tick);}
  requestAnimationFrame(tick);
  function bigBurst(){var y=innerHeight*0.4;burst(innerWidth*0.5,y,50);burst(innerWidth*0.28,y,22);burst(innerWidth*0.72,y,22);}
  function flashText(txt,x,y,color){var el=document.createElement("div");el.className="flash";el.textContent=txt;el.style.left=x+"px";el.style.top=y+"px";if(color)el.style.color=color;document.body.appendChild(el);setTimeout(function(){el.remove();},1300);}
  function centerOf(node){var r=node.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2,top:r.top};}

  /* ---- state ---- */
  var theme="dieren", mode="free", view="tiles";
  var items=[], byKey={}, idxOf={};
  var current=null, locked=false, stars=0, qTimer=null, CHOICES=3;
  function shuffle(a){for(var i=a.length-1;i>0;i--){var j=(Math.random()*(i+1))|0,t=a[i];a[i]=a[j];a[j]=t;}return a;}

  var homeSec=document.getElementById("home");
  var themeSec=document.getElementById("themeView");
  var themeGrid=document.getElementById("themeGrid");
  var themeTitle=document.getElementById("themeTitle");
  var tilesFree=document.getElementById("tilesFree");
  var tilesQuiz=document.getElementById("tilesQuiz");
  var sceneWrap=document.getElementById("sceneWrap");
  var replayBtn=document.getElementById("replay");
  var starsEl=document.getElementById("stars");
  var subtitle=document.getElementById("subtitle");
  var tabScene=document.getElementById("tabScene");
  var viewTabs=document.getElementById("viewTabs");
  var hasScene=true;
  function renderStars(){var n=Math.min(stars,10);starsEl.textContent=stars>0?(Array(n+1).join("⭐")+(stars>10?" +"+(stars-10):"")):"";}

  /* ---- HOME grid ---- */
  var themeColors={dieren:"#B7E38C",erf:"#FBE3A0",wild:"#F6D98A",voertuigen:"#A9DCF5",huis:"#F7C9D8",mensen:"#D6CCF2"};
  THEME_ORDER.forEach(function(tid){
    var t=THEMES[tid];
    var c=document.createElement("button"); c.className="theme-card"; c.type="button";
    c.style.background=themeColors[tid]||"#eee";
    c.innerHTML='<span class="tEmoji">'+t.emoji+'</span><span class="tName">'+t.title+'</span>';
    c.addEventListener("pointerdown",function(){ openTheme(tid); });
    themeGrid.appendChild(c);
  });
  (function(){ var c=document.createElement("div"); c.className="theme-card soon"; c.style.background="#EDE7F2";
    c.innerHTML='<span class="tEmoji">➕</span><span class="tName">Meer volgt…</span>'; themeGrid.appendChild(c); })();

  /* ---- free tiles (per theme) ---- */
  function buildTiles(){
    tilesFree.innerHTML="";
    items.forEach(function(a,i){
      var btn=document.createElement("button");
      btn.className="animal";btn.type="button";btn.style.background=colors[i%colors.length];btn.setAttribute("aria-label",a.name);
      btn.innerHTML='<span class="emoji" aria-hidden="true">'+a.emoji+'</span><span class="name">'+a.name+'</span>';
      btn.addEventListener("pointerdown",function(){
        initAudio();resume();unlockSpeech();
        var em=btn.querySelector(".emoji");em.classList.remove("pop");void em.offsetWidth;em.classList.add("pop");
        playSample(a.key);speak(a.name);
        var r=btn.getBoundingClientRect();burst(r.left+r.width/2,r.top+r.height/2,26);flashText(a.name,r.left+r.width/2,r.top);
      });
      tilesFree.appendChild(btn);
    });
  }
  tilesFree.addEventListener("pointerdown",function(e){
    if(e.target.closest(".animal"))return;initAudio();resume();unlockSpeech();sparkle();burst(e.clientX,e.clientY,10);
  });

  /* ---- scene handlers ---- */
  function clearSceneFx(){sceneWrap.querySelectorAll(".animal-node").forEach(function(n){n.classList.remove("a-bounce","a-shake","a-glow");});}
  sceneWrap.addEventListener("pointerdown",function(e){
    var node=e.target.closest(".animal-node"); if(!node) return;
    var key=node.getAttribute("data-key"); initAudio();resume();unlockSpeech();
    if(mode==="free"){
      node.classList.remove("a-bounce");void node.getBBox();node.classList.add("a-bounce");
      playSample(key);speak(byKey[key].name);
      var c=centerOf(node);burst(c.x,c.y,24);flashText(byKey[key].name,c.x,c.top);
    }else{
      if(locked)return;
      if(key===current.key){
        locked=true;node.classList.add("a-bounce","a-glow");bigBurst();
        flashText("Goed zo! 🎉",innerWidth/2,innerHeight*0.30,"#fff");stars++;renderStars();
        playSample(key,function(){speak(byKey[key].name);});
        qTimer=setTimeout(function(){if(mode==="quiz"&&view==="scene"){clearSceneFx();newQuestion();}},1900);
      }else{ node.classList.remove("a-shake");void node.getBBox();node.classList.add("a-shake");playQuestion(); }
    }
  });

  /* ---- quiz ---- */
  function playQuestion(){if(!current)return;replayBtn.classList.add("playing");
    playSample(current.key,function(){replayBtn.classList.remove("playing");});
    setTimeout(function(){replayBtn.classList.remove("playing");},2200);}
  function renderChoiceTiles(){
    var pool=shuffle(items.slice()),opts=[current];
    for(var i=0;i<pool.length&&opts.length<Math.min(CHOICES,items.length);i++){if(pool[i].key!==current.key)opts.push(pool[i]);}
    shuffle(opts);tilesQuiz.innerHTML="";
    opts.forEach(function(a){
      var btn=document.createElement("button");btn.className="animal";btn.type="button";
      btn.style.background=colors[idxOf[a.key]%colors.length];btn.setAttribute("aria-label",a.name);
      btn.innerHTML='<span class="emoji" aria-hidden="true">'+a.emoji+'</span><span class="name">'+a.name+'</span>';
      btn.addEventListener("pointerdown",function(){chooseTile(a,btn);});
      tilesQuiz.appendChild(btn);
    });
  }
  function chooseTile(a,btn){
    initAudio();resume();unlockSpeech();if(locked)return;
    if(a.key===current.key){
      locked=true;btn.classList.add("right");
      var em=btn.querySelector(".emoji");em.classList.remove("pop");void em.offsetWidth;em.classList.add("pop");
      bigBurst();flashText("Goed zo! 🎉",innerWidth/2,innerHeight*0.30,"#fff");stars++;renderStars();
      playSample(current.key,function(){speak(current.name);});
      qTimer=setTimeout(function(){if(mode==="quiz"&&view==="tiles")newQuestion();},1900);
    }else{ btn.classList.remove("shake");void btn.offsetWidth;btn.classList.add("shake");playQuestion(); }
  }
  function sceneKeySet(){
    var o={}; sceneWrap.querySelectorAll(".animal-node").forEach(function(n){o[n.getAttribute("data-key")]=1;});
    return o;
  }
  function newQuestion(){
    locked=false;
    var pool=items;
    if(view==="scene"){
      var ks=sceneKeySet(), f=items.filter(function(a){return ks[a.key];});
      if(f.length) pool=f;
    }
    current=pool[(Math.random()*pool.length)|0];
    if(view==="tiles")renderChoiceTiles();
    clearTimeout(qTimer);setTimeout(playQuestion,430);
  }
  replayBtn.addEventListener("pointerdown",function(){initAudio();resume();unlockSpeech();playQuestion();});

  /* ---- render + navigation ---- */
  var tabPlay=document.getElementById("tabPlay"),tabQuiz=document.getElementById("tabQuiz");
  var tabTiles=document.getElementById("tabTiles");
  function render(){
    clearTimeout(qTimer);locked=false;clearSceneFx();
    tabPlay.classList.toggle("active",mode==="free");
    tabQuiz.classList.toggle("active",mode==="quiz");
    tabTiles.classList.toggle("active",view==="tiles");
    tabScene.classList.toggle("active",view==="scene");
    tilesFree.hidden=!(view==="tiles"&&mode==="free");
    tilesQuiz.hidden=!(view==="tiles"&&mode==="quiz");
    sceneWrap.hidden=!(view==="scene");
    replayBtn.classList.toggle("show",mode==="quiz");
    starsEl.hidden=(mode!=="quiz");
    if(mode==="quiz"){stars=0;renderStars();}
    if(mode==="free"){try{window.speechSynthesis&&window.speechSynthesis.cancel();}catch(e){}}
    var sn=THEMES[theme].sceneName||"tekening";
    subtitle.textContent = mode==="free"
      ? (view==="scene"?("Tik op de "+sn+"!"):"Tik op een plaatje!")
      : (view==="scene"?"Zoek wat je hoort!":"Wat hoor je?");
    if(mode==="quiz")newQuestion();
  }
  function openTheme(tid){
    initAudio();resume();unlockSpeech();
    theme=tid;var t=THEMES[tid];items=t.items;byKey={};idxOf={};
    items.forEach(function(a,i){byKey[a.key]=a;idxOf[a.key]=i;});
    themeTitle.textContent=t.emoji+" "+t.title;
    var sc=document.getElementById("scene-"+tid);
    hasScene=!!sc;
    if(hasScene){ tabScene.textContent=t.sceneTab; sceneWrap.innerHTML=sc.innerHTML; }
    else { sceneWrap.innerHTML=""; }
    viewTabs.hidden=!hasScene;
    buildTiles();
    mode="free";view="tiles";
    homeSec.hidden=true;themeSec.hidden=false;
    render();
  }
  function goHome(){
    clearTimeout(qTimer);try{window.speechSynthesis&&window.speechSynthesis.cancel();}catch(e){}
    themeSec.hidden=true;homeSec.hidden=false;
  }
  document.getElementById("homeBtn").addEventListener("pointerdown",goHome);
  tabPlay.addEventListener("pointerdown",function(){initAudio();resume();unlockSpeech();mode="free";render();});
  tabQuiz.addEventListener("pointerdown",function(){initAudio();resume();unlockSpeech();mode="quiz";render();});
  tabTiles.addEventListener("pointerdown",function(){initAudio();resume();unlockSpeech();view="tiles";render();});
  tabScene.addEventListener("pointerdown",function(){initAudio();resume();unlockSpeech();view="scene";render();});
})();
</script>
'''

out = (HTML
  .replace("__SCENE_DIEREN__", SCENE_DIEREN)
  .replace("__SCENE_ERF__", SCENE_ERF)
  .replace("__SCENE_WILD__", SCENE_WILD)
  .replace("__SCENE_HUIS__", SCENE_HUIS)
  .replace("__SCENE_MENSEN__", SCENE_MENSEN)
  .replace("__SCENE_VOERTUIGEN__", SCENE_VOERT)
  .replace("__SOUNDS__", SOUNDS_JS))
open("app.html","w").write(out)
print("Wrote app.html:", os.path.getsize("app.html"), "bytes")
