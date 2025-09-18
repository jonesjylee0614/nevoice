import{Graph as e}from"./graphlib-DvGDBmTd.js";import{channel_default as t}from"./channel-Dvo_e2vM.js";import{Selection as n,array as r,common$1 as i,evaluate as a,getConfig as o,getStylesFromArray as s,interpolateToCurve as c,isFunction_default as l,isPlainObject_default as u,linear_default as d,log$1 as f,renderKatex as p,rgba_default as m,root as h,select_default as g,setupGraphViewbox$1 as _,utils as v}from"./index-eM6Wc6ON.js";import{render as y}from"./index-3862675e-DmrDpeGC.js";function b(e){return typeof e==`string`?new n([document.querySelectorAll(e)],[document.documentElement]):new n([r(e)],h)}function x(e,t){return!!e.children(t).length}function S(e){return w(e.v)+`:`+w(e.w)+`:`+w(e.name)}var C=/:/g;function w(e){return e?String(e).replace(C,`\\:`):``}function T(e,t){t&&e.attr(`style`,t)}function E(e,t,n){t&&e.attr(`class`,t).attr(`class`,n+` `+e.attr(`class`))}function D(e,t){var n=t.graph();if(u(n)){var r=n.transition;if(l(r))return r(e)}return e}function O(e,t){var n=e.append(`foreignObject`).attr(`width`,`100000`),r=n.append(`xhtml:div`);r.attr(`xmlns`,`http://www.w3.org/1999/xhtml`);var i=t.label;switch(typeof i){case`function`:r.insert(i);break;case`object`:r.insert(function(){return i});break;default:r.html(i)}T(r,t.labelStyle),r.style(`display`,`inline-block`),r.style(`white-space`,`nowrap`);var a=r.node().getBoundingClientRect();return n.attr(`width`,a.width).attr(`height`,a.height),n}const k={},A=function(e){let t=Object.keys(e);for(let n of t)k[n]=e[n]},j=async function(e,t,n,r,c,l){let u=r.select(`[id="${n}"]`),d=Object.keys(e);for(let n of d){let r=e[n],d=`default`;r.classes.length>0&&(d=r.classes.join(` `)),d+=` flowchart-label`;let m=s(r.styles),h=r.text===void 0?r.id:r.text,g;if(f.info(`vertex`,r,r.labelType),r.labelType===`markdown`)f.info(`vertex`,r,r.labelType);else if(a(o().flowchart.htmlLabels)){let e={label:h};g=O(u,e).node(),g.parentNode.removeChild(g)}else{let e=c.createElementNS(`http://www.w3.org/2000/svg`,`text`);e.setAttribute(`style`,m.labelStyle.replace(`color:`,`fill:`));let t=h.split(i.lineBreakRegex);for(let n of t){let t=c.createElementNS(`http://www.w3.org/2000/svg`,`tspan`);t.setAttributeNS(`http://www.w3.org/XML/1998/namespace`,`xml:space`,`preserve`),t.setAttribute(`dy`,`1em`),t.setAttribute(`x`,`1`),t.textContent=n,e.appendChild(t)}g=e}let _=0,v=``;switch(r.type){case`round`:_=5,v=`rect`;break;case`square`:v=`rect`;break;case`diamond`:v=`question`;break;case`hexagon`:v=`hexagon`;break;case`odd`:v=`rect_left_inv_arrow`;break;case`lean_right`:v=`lean_right`;break;case`lean_left`:v=`lean_left`;break;case`trapezoid`:v=`trapezoid`;break;case`inv_trapezoid`:v=`inv_trapezoid`;break;case`odd_right`:v=`rect_left_inv_arrow`;break;case`circle`:v=`circle`;break;case`ellipse`:v=`ellipse`;break;case`stadium`:v=`stadium`;break;case`subroutine`:v=`subroutine`;break;case`cylinder`:v=`cylinder`;break;case`group`:v=`rect`;break;case`doublecircle`:v=`doublecircle`;break;default:v=`rect`}let y=await p(h,o());t.setNode(r.id,{labelStyle:m.labelStyle,shape:v,labelText:y,labelType:r.labelType,rx:_,ry:_,class:d,style:m.style,id:r.id,link:r.link,linkTarget:r.linkTarget,tooltip:l.db.getTooltip(r.id)||``,domId:l.db.lookUpDomId(r.id),haveCallback:r.haveCallback,width:r.type===`group`?500:void 0,dir:r.dir,type:r.type,props:r.props,padding:o().flowchart.padding}),f.info(`setNode`,{labelStyle:m.labelStyle,labelType:r.labelType,shape:v,labelText:y,rx:_,ry:_,class:d,style:m.style,id:r.id,domId:l.db.lookUpDomId(r.id),width:r.type===`group`?500:void 0,type:r.type,dir:r.dir,props:r.props,padding:o().flowchart.padding})}},M=async function(e,t,n){f.info(`abc78 edges = `,e);let r=0,a={},l,u;if(e.defaultStyle!==void 0){let t=s(e.defaultStyle);l=t.style,u=t.labelStyle}for(let n of e){r++;let m=`L-`+n.start+`-`+n.end;a[m]===void 0?(a[m]=0,f.info(`abc78 new entry`,m,a[m])):(a[m]++,f.info(`abc78 new entry`,m,a[m]));let h=m+`-`+a[m];f.info(`abc78 new link id to be used is`,m,h,a[m]);let g=`LS-`+n.start,_=`LE-`+n.end,v={style:``,labelStyle:``};switch(v.minlen=n.length||1,n.type===`arrow_open`?v.arrowhead=`none`:v.arrowhead=`normal`,v.arrowTypeStart=`arrow_open`,v.arrowTypeEnd=`arrow_open`,n.type){case`double_arrow_cross`:v.arrowTypeStart=`arrow_cross`;case`arrow_cross`:v.arrowTypeEnd=`arrow_cross`;break;case`double_arrow_point`:v.arrowTypeStart=`arrow_point`;case`arrow_point`:v.arrowTypeEnd=`arrow_point`;break;case`double_arrow_circle`:v.arrowTypeStart=`arrow_circle`;case`arrow_circle`:v.arrowTypeEnd=`arrow_circle`;break}let y=``,b=``;switch(n.stroke){case`normal`:y=`fill:none;`,l!==void 0&&(y=l),u!==void 0&&(b=u),v.thickness=`normal`,v.pattern=`solid`;break;case`dotted`:v.thickness=`normal`,v.pattern=`dotted`,v.style=`fill:none;stroke-width:2px;stroke-dasharray:3;`;break;case`thick`:v.thickness=`thick`,v.pattern=`solid`,v.style=`stroke-width: 3.5px;fill:none;`;break;case`invisible`:v.thickness=`invisible`,v.pattern=`solid`,v.style=`stroke-width: 0;fill:none;`;break}if(n.style!==void 0){let e=s(n.style);y=e.style,b=e.labelStyle}v.style=v.style+=y,v.labelStyle=v.labelStyle+=b,n.interpolate===void 0?e.defaultInterpolate===void 0?v.curve=c(k.curve,d):v.curve=c(e.defaultInterpolate,d):v.curve=c(n.interpolate,d),n.text===void 0?n.style!==void 0&&(v.arrowheadStyle=`fill: #333`):(v.arrowheadStyle=`fill: #333`,v.labelpos=`c`),v.labelType=n.labelType,v.label=await p(n.text.replace(i.lineBreakRegex,`
`),o()),n.style===void 0&&(v.style=v.style||`stroke: #333; stroke-width: 1.5px;fill:none;`),v.labelStyle=v.labelStyle.replace(`color:`,`fill:`),v.id=h,v.classes=`flowchart-link `+g+` `+_,t.setEdge(n.start,n.end,v,r)}},N=function(e,t){return t.db.getClasses()},P=async function(t,n,r,i){f.info(`Drawing flowchart`);let a=i.db.getDirection();a===void 0&&(a=`TD`);let{securityLevel:s,flowchart:c}=o(),l=c.nodeSpacing||50,u=c.rankSpacing||50,d;s===`sandbox`&&(d=g(`#i`+n));let p=g(s===`sandbox`?d.nodes()[0].contentDocument.body:`body`),m=s===`sandbox`?d.nodes()[0].contentDocument:document,h=new e({multigraph:!0,compound:!0}).setGraph({rankdir:a,nodesep:l,ranksep:u,marginx:0,marginy:0}).setDefaultEdgeLabel(function(){return{}}),x,S=i.db.getSubGraphs();f.info(`Subgraphs - `,S);for(let e=S.length-1;e>=0;e--)x=S[e],f.info(`Subgraph - `,x),i.db.addVertex(x.id,{text:x.title,type:x.labelType},`group`,void 0,x.classes,x.dir);let C=i.db.getVertices(),w=i.db.getEdges();f.info(`Edges`,w);let T=0;for(T=S.length-1;T>=0;T--){x=S[T],b(`cluster`).append(`text`);for(let e=0;e<x.nodes.length;e++)f.info(`Setting up subgraphs`,x.nodes[e],x.id),h.setParent(x.nodes[e],x.id)}await j(C,h,n,p,m,i),await M(w,h);let E=p.select(`[id="${n}"]`),D=p.select(`#`+n+` g`);if(await y(D,h,[`point`,`circle`,`cross`],`flowchart`,n),v.insertTitle(E,`flowchartTitleText`,c.titleTopMargin,i.db.getDiagramTitle()),_(h,E,c.diagramPadding,c.useMaxWidth),i.db.indexNodes(`subGraph`+T),!c.htmlLabels){let e=m.querySelectorAll(`[id="`+n+`"] .edgeLabel .label`);for(let t of e){let e=t.getBBox(),n=m.createElementNS(`http://www.w3.org/2000/svg`,`rect`);n.setAttribute(`rx`,0),n.setAttribute(`ry`,0),n.setAttribute(`width`,e.width),n.setAttribute(`height`,e.height),t.insertBefore(n,t.firstChild)}}let O=Object.keys(C);O.forEach(function(e){let t=C[e];if(t.link){let r=g(`#`+n+` [id="`+e+`"]`);if(r){let e=m.createElementNS(`http://www.w3.org/2000/svg`,`a`);e.setAttributeNS(`http://www.w3.org/2000/svg`,`class`,t.classes.join(` `)),e.setAttributeNS(`http://www.w3.org/2000/svg`,`href`,t.link),e.setAttributeNS(`http://www.w3.org/2000/svg`,`rel`,`noopener`),s===`sandbox`?e.setAttributeNS(`http://www.w3.org/2000/svg`,`target`,`_top`):t.linkTarget&&e.setAttributeNS(`http://www.w3.org/2000/svg`,`target`,t.linkTarget);let n=r.insert(function(){return e},`:first-child`),i=r.select(`.label-container`);i&&n.append(function(){return i.node()});let a=r.select(`.label`);a&&n.append(function(){return a.node()})}}})},F={setConf:A,addVertices:j,addEdges:M,getClasses:N,draw:P},I=(e,n)=>{let r=t,i=r(e,`r`),a=r(e,`g`),o=r(e,`b`);return m(i,a,o,n)},L=e=>`.label {
    font-family: ${e.fontFamily};
    color: ${e.nodeTextColor||e.textColor};
  }
  .cluster-label text {
    fill: ${e.titleColor};
  }
  .cluster-label span,p {
    color: ${e.titleColor};
  }

  .label text,span,p {
    fill: ${e.nodeTextColor||e.textColor};
    color: ${e.nodeTextColor||e.textColor};
  }

  .node rect,
  .node circle,
  .node ellipse,
  .node polygon,
  .node path {
    fill: ${e.mainBkg};
    stroke: ${e.nodeBorder};
    stroke-width: 1px;
  }
  .flowchart-label text {
    text-anchor: middle;
  }
  // .flowchart-label .text-outer-tspan {
  //   text-anchor: middle;
  // }
  // .flowchart-label .text-inner-tspan {
  //   text-anchor: start;
  // }

  .node .katex path {
    fill: #000;
    stroke: #000;
    stroke-width: 1px;
  }

  .node .label {
    text-align: center;
  }
  .node.clickable {
    cursor: pointer;
  }

  .arrowheadPath {
    fill: ${e.arrowheadColor};
  }

  .edgePath .path {
    stroke: ${e.lineColor};
    stroke-width: 2.0px;
  }

  .flowchart-link {
    stroke: ${e.lineColor};
    fill: none;
  }

  .edgeLabel {
    background-color: ${e.edgeLabelBackground};
    rect {
      opacity: 0.5;
      background-color: ${e.edgeLabelBackground};
      fill: ${e.edgeLabelBackground};
    }
    text-align: center;
  }

  /* For html labels only */
  .labelBkg {
    background-color: ${I(e.edgeLabelBackground,.5)};
    // background-color: 
  }

  .cluster rect {
    fill: ${e.clusterBkg};
    stroke: ${e.clusterBorder};
    stroke-width: 1px;
  }

  .cluster text {
    fill: ${e.titleColor};
  }

  .cluster span,p {
    color: ${e.titleColor};
  }
  /* .cluster div {
    color: ${e.titleColor};
  } */

  div.mermaidTooltip {
    position: absolute;
    text-align: center;
    max-width: 200px;
    padding: 2px;
    font-family: ${e.fontFamily};
    font-size: 12px;
    background: ${e.tertiaryColor};
    border: 1px solid ${e.border2};
    border-radius: 2px;
    pointer-events: none;
    z-index: 100;
  }

  .flowchartTitleText {
    text-anchor: middle;
    font-size: 18px;
    fill: ${e.textColor};
  }
`,R=L;export{O as addHtmlLabel,E as applyClass,T as applyStyle,D as applyTransition,S as edgeToId,F as flowRendererV2,R as flowStyles,x as isSubgraph,b as selectAll_default};