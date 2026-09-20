/** Browser regression checks for the bundled template's generated HTML.
 * npm's playwright is a development-only dependency; the viewer needs none.
 * Usage: node test_interview_viewer.cjs /path/to/generated-template.html
 */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const os=require('node:os');
const fs=require('node:fs');
const input=process.argv[2];
if(!input)throw new Error('Provide HTML generated from assets/interview.template.toml. Requires Playwright; set CHROME_PATH to use an installed Chromium browser.');
const screenshot=name=>path.join(process.env.VIEWER_SCREENSHOTS||os.tmpdir(),name);
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
 const context=await browser.newContext({viewport:{width:1440,height:1000},hasTouch:true,offline:true});
 const page=await context.newPage();const errors=[];const requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto(pathToFileURL(path.resolve(input)).href);await page.waitForSelector('html[data-ready=true]');
 assert.equal(await page.locator('.node').count(),5);assert.equal(await page.locator('.edge').count(),4);
 assert.equal(await page.locator('#readiness').innerText(),'—');
 const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 const inspectorState=async open=>{
  assert.equal(await page.locator('#show-details').isVisible(),true);
  assert.equal(await page.locator('#show-details').getAttribute('aria-controls'),'detail');
  assert.equal(await page.locator('#show-details').getAttribute('aria-expanded'),String(open));
  assert.equal(await page.locator('#detail').isVisible(),open);
  assert.equal(await page.locator('#detail').evaluate(el=>el.classList.contains('open')),open);
  assert.equal(await page.locator('.layout').evaluate(el=>el.classList.contains('details-open')),open);
 };
 const viewportWidth=async()=>(await page.locator('#viewport').boundingBox()).width;
 const assertRestoredWidth=async width=>{
  await settle();assert.ok(Math.abs(await viewportWidth()-width)<1,'Closing the inspector must restore canvas width');
 };
 const fitWithoutOverlaps=async()=>{
  await page.locator('#fit').click();await settle();
  const violations=await page.evaluate(()=>{
   const viewport=document.querySelector('#viewport').getBoundingClientRect();
   const overlays=[...document.querySelectorAll('.toolbar,.map-footer')].map(el=>({name:el.className,rect:el.getBoundingClientRect()}));
   const issues=[];
   for(const node of document.querySelectorAll('.node')){
    const rect=node.getBoundingClientRect();
    if(rect.left<viewport.left-.5||rect.right>viewport.right+.5||rect.top<viewport.top-.5||rect.bottom>viewport.bottom+.5)issues.push(`${node.dataset.id} outside viewport`);
    for(const overlay of overlays){const other=overlay.rect;if(rect.left<other.right&&rect.right>other.left&&rect.top<other.bottom&&rect.bottom>other.top)issues.push(`${node.dataset.id} overlaps ${overlay.name}`);}
   }
   return issues;
  });
  assert.deepEqual(violations,[],'Fit must keep every node clear of floating controls');
 };
 await inspectorState(false);await fitWithoutOverlaps();
 const closedWidth=await viewportWidth();
 assert.ok(await page.locator('.map-panel').evaluate(el=>{const style=getComputedStyle(el);return ['Top','Right','Bottom','Left'].every(side=>parseFloat(style[`border${side}Width`])===0);}), 'The canvas must remain borderless');
 await page.screenshot({animations:'disabled',path:screenshot('interview-viewer-light.png')});
 await page.locator('[data-theme-choice=dark]').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');await page.screenshot({animations:'disabled',path:screenshot('interview-viewer-dark.png')});
 await page.locator('#show-details').click();await inspectorState(true);await settle();assert.ok(await viewportWidth()<closedWidth-100,'Opening details must reduce desktop canvas width');await fitWithoutOverlaps();await page.screenshot({animations:'disabled',path:screenshot('interview-viewer-inspector.png')});
 await page.locator('#show-details').click();await inspectorState(false);await assertRestoredWidth(closedWidth);
 await page.locator('#show-details').click();await inspectorState(true);await page.locator('#close-details').click();await inspectorState(false);await assertRestoredWidth(closedWidth);assert.equal(await page.evaluate(()=>document.activeElement.id),'show-details');
 await page.locator('#show-details').click();await inspectorState(true);await page.keyboard.press('Escape');await inspectorState(false);await assertRestoredWidth(closedWidth);assert.equal(await page.evaluate(()=>document.activeElement.id),'show-details');
 await page.locator('[data-theme-choice=auto]').click();await page.emulateMedia({colorScheme:'dark'});await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');await page.emulateMedia({colorScheme:'light'});await page.waitForFunction(()=>document.documentElement.dataset.theme==='light');assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
 const camera=()=>page.locator('#world').evaluate(el=>{const m=new DOMMatrix(getComputedStyle(el).transform);return{x:m.e,y:m.f,s:m.a}});
 let c=await camera();await page.locator('#zoom-in').click();assert.ok((await camera()).s>c.s);await page.locator('#zoom-out').click();assert.ok(Math.abs((await camera()).s-c.s)<.00001);
 await page.locator('#actual-size').click();assert.equal((await camera()).s,1);
 await page.locator('#show-details').click();await inspectorState(true);await settle();assert.equal((await camera()).s,1,'Opening the inspector must preserve manual zoom');await page.locator('#close-details').click();await inspectorState(false);await settle();assert.equal((await camera()).s,1,'Closing the inspector must preserve manual zoom');
 const box=await page.locator('#viewport').boundingBox();const point={x:box.width*.3,y:box.height*.4};await page.locator('#viewport').evaluate(el=>el.addEventListener('wheel',e=>{const r=el.getBoundingClientRect();window.lastWheel={x:e.clientX-r.left,y:e.clientY-r.top};},{once:true}));const old=await camera();await page.mouse.move(box.x+point.x,box.y+point.y);await page.mouse.wheel(0,-150);await page.waitForTimeout(100);const after=await camera();const actualPoint=await page.evaluate(()=>window.lastWheel);assert.ok(after.s>old.s);assert.ok(Math.abs((actualPoint.x-old.x)/old.s-(actualPoint.x-after.x)/after.s)<.002);assert.ok(Math.abs((actualPoint.y-old.y)/old.s-(actualPoint.y-after.y)/after.s)<.002);
 await fitWithoutOverlaps();const beforePan=await camera();const toolbar=await page.locator('.toolbar').boundingBox();const panStart={x:box.x+20,y:toolbar.y+toolbar.height+20};await page.mouse.move(panStart.x,panStart.y);await page.mouse.down();await page.mouse.move(panStart.x+110,panStart.y+70,{steps:10});await page.mouse.up();const panned=await camera();assert.ok(Math.abs(panned.x-beforePan.x-110)<.1);assert.ok(Math.abs(panned.y-beforePan.y-70)<.1);
 await page.locator('#fit').click();await page.locator('.node[data-id="s1-content"]').click();await inspectorState(true);assert.equal(await page.locator('.node.selected').getAttribute('data-id'),'s1-content');assert.ok((await page.locator('#detail-content').innerText()).includes('Prepare the shop page content'));
 await page.locator('#search').fill('visitor');assert.equal(await page.locator('.node:not(.dimmed)').count(),1);await page.locator('#search').press('Enter');assert.equal(await page.locator('.node.selected').getAttribute('data-id'),'s2');await page.locator('#search').fill('no-matching-name');assert.ok((await page.locator('#search-count').innerText()).includes('No matches'));await page.locator('#search').fill('');
 await page.locator('[data-mode=dependencies]').click();assert.equal(await page.locator('.node').count(),3);assert.equal(await page.locator('.edge').count(),3);
 assert.ok(await page.locator('.edge').evaluateAll(es=>es.every(e=>{const ps=e.getAttribute('points').split(' ').map(p=>p.split(',').map(Number));return ps.length<=4&&ps.slice(1).every((p,i)=>(p[0]===ps[i][0])!==(p[1]===ps[i][1]));})));
 const crossings=await page.evaluate(()=>{const ns=[...document.querySelectorAll('.node')].map(n=>({id:n.dataset.id,x:parseFloat(n.style.left),y:parseFloat(n.style.top),w:n.offsetWidth,h:n.offsetHeight}));return [...document.querySelectorAll('.edge')].some(e=>{const ps=e.getAttribute('points').split(' ').map(p=>p.split(',').map(Number));return ns.some(n=>n.id!==e.dataset.source&&n.id!==e.dataset.target&&ps.slice(1).some((b,i)=>{const a=ps[i];return a[0]===b[0]?a[0]>n.x&&a[0]<n.x+n.w&&Math.max(a[1],b[1])>n.y&&Math.min(a[1],b[1])<n.y+n.h:a[1]>n.y&&a[1]<n.y+n.h&&Math.max(a[0],b[0])>n.x&&Math.min(a[0],b[0])<n.x+n.w;}));});});assert.equal(crossings,false);
 await page.locator('#viewport').focus();await page.keyboard.press('1');assert.equal((await camera()).s,1);await page.keyboard.press('0');assert.ok((await camera()).s<=1);
 const oldTouch=await camera();const client=await context.newCDPSession(page);const touchBox=await page.locator('#viewport').boundingBox();const cx=touchBox.x+touchBox.width/2,cy=touchBox.y+touchBox.height/2;
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:cx-40,y:cy,id:1},{x:cx+40,y:cy,id:2}]});
 await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:cx-80,y:cy,id:1},{x:cx+80,y:cy,id:2}]});
 await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.ok((await camera()).s>oldTouch.s);
 await page.locator('[data-mode=structure]').click();await page.locator('#close-details').click();await inspectorState(false);await page.setViewportSize({width:390,height:844});await fitWithoutOverlaps();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.locator('#show-details').click();await inspectorState(true);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.locator('#close-details').click();await inspectorState(false);assert.equal(await page.evaluate(()=>document.activeElement.id),'show-details');
 await fitWithoutOverlaps();await page.locator('.node[data-id="s1-content"]').click();await inspectorState(true);await page.keyboard.press('Escape');await inspectorState(false);assert.equal(await page.evaluate(()=>document.activeElement.id),'show-details');await fitWithoutOverlaps();await page.screenshot({animations:'disabled',path:screenshot('interview-viewer-mobile.png')});
 // A conversation-language preference must not change the English viewer UI.
 const html=fs.readFileSync(input,'utf8');
 const withPayload=change=>html.replace(/(<script id="interview-data" type="application\/json">)([\s\S]*?)(<\/script>)/,(_,start,json,end)=>{
  const data=JSON.parse(json);change(data);
  return start+JSON.stringify(data).replace(/[<>&\u2028\u2029]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+end;
 });
 const alternate=withPayload(data=>{data.user.language='ko';});
 await page.setViewportSize({width:1440,height:1000});await page.setContent(alternate);await page.waitForSelector('html[data-ready=true]');
 assert.equal(await page.locator('html').getAttribute('lang'),'en');
 assert.equal(await page.locator('#search').getAttribute('placeholder'),'Find a task');
 assert.equal(await page.locator('#zoom-in').getAttribute('aria-label'),'Zoom in (+)');
 await inspectorState(false);await page.locator('#show-details').click();await inspectorState(true);await page.locator('[data-tab=interview]').click();assert.ok((await page.locator('#detail-content').innerText()).includes('Make a small website for my shop.'));
 // Verify rendered, visible provenance and history using synthetic records.
 const attack='<img src=x onerror="window.viewerInjected=true"></script><script>window.viewerInjected=true</script>';
 const unsafeSources=['javascript:window.viewerInjected=true','data:text/html,unsafe','file:///private/synthetic-note.txt','Reference https://example.test/reference and local notes','https://','https://exa mple.test/'];
 const audit=withPayload(data=>{
  data.evidence=[
   {id:'e-answer',kind:'user',text:`Show the email address, with this literal text: ${attack}`,source:'User answer in synthetic round 1',accepted:true,status:'active'},
   {id:'e-finding',kind:'artifact',text:'The reference page supports keyboard navigation.',source:'https://example.test/reference?mode=keyboard&view=full',accepted:true,status:'active'},
   {id:'e-default',kind:'assumption',text:'Use the existing static page method.',source:'Adopted under delegated method choice; notes/default.txt',accepted:true,status:'active'},
   {id:'e-open',kind:'assumption',text:'A form might be useful.',source:'/synthetic/notes/method.txt',accepted:false,status:'active'},
   {id:'e-old',kind:'user',text:'The earlier answer was phone only.',source:'Earlier synthetic user answer',accepted:true,status:'superseded'},
   {id:'e-http',kind:'artifact',text:'An older reference remains available.',source:'http://example.test/archive',accepted:false,status:'superseded'},
   {id:'e-markup',kind:'artifact',text:`Literal finding: ${attack}`,source:attack,accepted:false,status:'active'},
   ...unsafeSources.map((source,index)=>({id:`e-unsafe-${index}`,kind:'artifact',text:'Synthetic source safety case.',source,accepted:false,status:'active'}))
  ];
  data.requirements=[{id:'r-audit',description:'Keep source provenance visible.',kind:'constraint',evidence_ids:data.evidence.map(e=>e.id)}];
  for(const node of data.nodes){node.requirement_ids=['r-audit'];node.criteria=[{id:'c-audit',description:'Check the recorded finding.',check:'Verify keyboard navigation.',required:true,score:2,reported_score:2,reason:'The finding and adopted method support the check.',evidence_ids:['e-finding','e-open','e-old'],rating_evidence_ids:['e-finding','e-default'],decision_ids:['d-audit']}];node.decisions=[{id:'d-audit',question:'Which page method?',status:'resolved',value:'Static page',required:true,evidence_ids:['e-default']}];}
  data.questions=[{id:'q-answer',revision:2,round:1,generator_id:'synthetic-question-worker',isolated:true,targets:['c-audit'],text:'Which contact option should visitors see?',options:['Phone','Email'],why:'This changes the page content.',status:'answered',answer_evidence_ids:['e-answer']},{id:'q-skip',revision:2,round:1,generator_id:'synthetic-skip-worker',isolated:true,targets:['c-audit'],text:'Which method should be used?',options:['Static page','Form'],status:'skipped',answer_evidence_ids:[]}];
  const proposal={question:'Does navigation work without scripts?',method:'Open the synthetic page with scripts disabled.',stop_condition:'Stop after checking two navigation links.',expected_evidence:'A recorded navigation result.',informs_decision:'Whether the static method is sufficient.'};
  data.attempts=[
   {id:'a-inspect',action:'inspect',status:'completed',inspection:'Read the synthetic reference.',result:'The sample has the needed keyboard behavior.',evidence_ids:['e-finding']},
   {id:'a-experiment',action:'experiment',status:'proposed',proposal,result:'',evidence_ids:[]},
   {id:'a-repair',action:'repair',status:'inconclusive',result:'The scope still needs a clear boundary.',evidence_ids:['e-open']},
   {id:'a-pause',action:'pause',status:'skipped',result:'The user asked to continue the interview.',evidence_ids:[]},
   {id:'a-failed',action:'inspect',status:'failed',inspection:'Read an unavailable synthetic sample.',result:'The sample could not be opened.',evidence_ids:[]},
   {id:'a-running',action:'experiment',status:'running',proposal,result:'',evidence_ids:[]}
  ].map((attempt,index)=>({...attempt,revision:2,round:1,generator_id:`synthetic-action-worker-${index}`,isolated:true,targets:['c-audit'],why:'Resolve the gap using existing evidence.'}));
 });
 await page.setContent(audit);await page.waitForSelector('html[data-ready=true]');await page.locator('#show-details').click();
 const requirement=page.locator('.requirement[data-requirement-id="r-audit"]');await requirement.locator('summary').click();
 assert.ok((await requirement.innerText()).includes('The reference page supports keyboard navigation.'));
 assert.ok((await requirement.innerText()).includes('User evidence'));
 assert.ok((await requirement.innerText()).includes('Artifact finding'));
 assert.ok((await requirement.innerText()).includes('Adopted default / assumption'));
 const finding=requirement.locator('[data-evidence-id="e-finding"]');assert.equal(await finding.isVisible(),true);
 assert.equal(await finding.locator('.evidence-source a').getAttribute('href'),'https://example.test/reference?mode=keyboard&view=full');
 assert.equal(await finding.locator('.evidence-source a').getAttribute('rel'),'noopener noreferrer');
 assert.equal(await requirement.locator('[data-evidence-id="e-http"] .evidence-source a').getAttribute('href'),'http://example.test/archive');
 for(const [id,source]of [['e-markup',attack],['e-open','/synthetic/notes/method.txt'],...unsafeSources.map((source,index)=>[`e-unsafe-${index}`,source])]){
  const card=requirement.locator(`[data-evidence-id="${id}"]`);assert.equal(await card.isVisible(),true);assert.equal(await card.locator('.evidence-source a').count(),0);assert.ok((await card.innerText()).includes(source));
 }
 assert.ok((await requirement.locator('[data-evidence-id="e-open"]').innerText()).includes('Not accepted · Active'));
 assert.ok((await requirement.locator('[data-evidence-id="e-old"]').innerText()).includes('Accepted · Superseded'));
 const decision=page.locator('.decision[data-decision-id="d-audit"]');await decision.locator('summary').click();
 assert.ok((await decision.innerText()).includes('Adopted default / assumption'));assert.ok((await decision.innerText()).includes('Adopted under delegated method choice'));
 assert.equal(/user.confirmed/i.test(await decision.innerText()),false);
 const criterion=page.locator('.criterion[data-criterion-id="c-audit"]');await criterion.locator('[data-evidence-label="Rating evidence"] > summary').click();
 assert.ok((await criterion.innerText()).includes('The reference page supports keyboard navigation.'));assert.ok((await criterion.innerText()).includes('Adopted default / assumption'));
 await criterion.locator('[data-evidence-label="Linked evidence"] > summary').click();assert.ok((await criterion.innerText()).includes('Not accepted · Active'));assert.ok((await criterion.innerText()).includes('Accepted · Superseded'));
 await page.locator('[data-tab=interview]').click();
 const answered=page.locator('[data-question-id="q-answer"]');assert.ok((await answered.innerText()).includes('Show the email address'));
 assert.ok((await answered.innerText()).includes(attack));assert.equal(await answered.locator('[data-evidence-id="e-answer"]').isVisible(),true);
 assert.deepEqual(await answered.locator('.question-options li').allTextContents(),['Phone','Email']);
 assert.ok((await answered.innerText()).includes('User answer in synthetic round 1'));
 const skipped=page.locator('[data-question-id="q-skip"]');assert.ok((await skipped.innerText()).includes('Skipped'));assert.ok((await skipped.innerText()).includes('No answer recorded.'));assert.equal(await skipped.locator('.evidence-card').count(),0);
 assert.equal(await page.locator('.question [data-evidence-id="e-default"]').count(),0,'An adopted default is not a user answer');
 assert.equal(await page.locator('.resolution-attempt').count(),6);
 const inspection=page.locator('[data-attempt-id="a-inspect"]');assert.ok((await inspection.innerText()).includes('Inspect sources'));assert.ok((await inspection.innerText()).includes('Completed'));assert.ok((await inspection.innerText()).includes('The sample has the needed keyboard behavior.'));
 await inspection.locator('.record-details > summary').click();assert.ok((await inspection.innerText()).includes('Read the synthetic reference.'));assert.ok((await inspection.innerText()).includes('synthetic-action-worker-0'));
 await inspection.locator('.evidence-details > summary').click();assert.ok((await inspection.innerText()).includes('Artifact finding'));assert.ok((await inspection.innerText()).includes('https://example.test/reference'));
 const experiment=page.locator('[data-attempt-id="a-experiment"]');await experiment.locator('summary').click();
 for(const text of ['Run experiment','Proposed','No result yet.','Resolve the gap using existing evidence.','Does navigation work without scripts?','Open the synthetic page with scripts disabled.','Stop after checking two navigation links.','A recorded navigation result.','Whether the static method is sufficient.'])assert.ok((await experiment.innerText()).includes(text),text);
 assert.ok((await page.locator('[data-attempt-id="a-repair"]').innerText()).includes('Inconclusive'));
 assert.ok((await page.locator('[data-attempt-id="a-pause"]').innerText()).includes('Skipped'));
 assert.ok((await page.locator('[data-attempt-id="a-failed"]').innerText()).includes('Failed'));
 assert.ok((await page.locator('[data-attempt-id="a-running"]').innerText()).includes('In progress'));
 assert.equal(await page.locator('#detail-content img,#detail-content script').count(),0);assert.equal(await page.evaluate(()=>window.viewerInjected),undefined);
 assert.equal(await page.locator('.question').count(),2,'Non-question attempts must not become questions or answers');
 await page.screenshot({animations:'disabled',path:screenshot('interview-viewer-history.png')});
 await page.setContent(withPayload(data=>{delete data.attempts;}));await page.waitForSelector('html[data-ready=true]');await page.locator('#show-details').click();await page.locator('[data-tab=interview]').click();
 assert.ok((await page.locator('[data-section="resolution-history"]').innerText()).includes('No non-question actions recorded.'));
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);console.log('PASS: offline rendering, no page errors/network, light/dark/system, zoom buttons, cursor anchor, wheel, pan, touch pinch, keyboard, search, selection, nested/expanded graphs, orthogonal edges, borderless canvas, inspector toggle/selection/focus, floating-control Fit clearance, mobile details/layout, English UI independent of conversation language, visible answers/choices/source evidence/default provenance, safe source links and literal markup, resolution history/plans/results, optional attempts compatibility');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
