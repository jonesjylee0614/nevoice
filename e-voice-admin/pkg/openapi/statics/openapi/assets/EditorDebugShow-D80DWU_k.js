import{VAceEditor as e,__commonJSMin as t,__toESM as n,createElementBlock as r,createVNode as i,normalizeStyle as a,openBlock as o,reactive as s,ref as c,toRefs as l,unref as u,watch as d}from"./index-eM6Wc6ON.js";import{require_ext_language_tools as f,require_mode_javascript as p,require_theme_eclipse as m}from"./ext-language_tools-Xmce0BJU.js";var h=t((exports,t)=>{ace.define(`ace/mode/json_highlight_rules`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/mode/text_highlight_rules`],function(e,t,n){"use strict";var r=e(`../lib/oop`),i=e(`./text_highlight_rules`).TextHighlightRules,a=function(){this.$rules={start:[{token:`variable`,regex:`["](?:(?:\\\\.)|(?:[^"\\\\]))*?["]\\s*(?=:)`},{token:`string`,regex:`"`,next:`string`},{token:`constant.numeric`,regex:`0[xX][0-9a-fA-F]+\\b`},{token:`constant.numeric`,regex:`[+-]?\\d+(?:(?:\\.\\d*)?(?:[eE][+-]?\\d+)?)?\\b`},{token:`constant.language.boolean`,regex:`(?:true|false)\\b`},{token:`text`,regex:`['](?:(?:\\\\.)|(?:[^'\\\\]))*?[']`},{token:`comment`,regex:`\\/\\/.*$`},{token:`comment.start`,regex:`\\/\\*`,next:`comment`},{token:`paren.lparen`,regex:`[[({]`},{token:`paren.rparen`,regex:`[\\])}]`},{token:`punctuation.operator`,regex:/[,]/},{token:`text`,regex:`\\s+`}],string:[{token:`constant.language.escape`,regex:/\\(?:x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|["\\\/bfnrt])/},{token:`string`,regex:`"|$`,next:`start`},{defaultToken:`string`}],comment:[{token:`comment.end`,regex:`\\*\\/`,next:`start`},{defaultToken:`comment`}]}};r.inherits(a,i),t.JsonHighlightRules=a}),ace.define(`ace/mode/matching_brace_outdent`,[`require`,`exports`,`module`,`ace/range`],function(e,t,n){"use strict";var r=e(`../range`).Range,i=function(){};(function(){this.checkOutdent=function(e,t){return/^\s+$/.test(e)?/^\s*\}/.test(t):!1},this.autoOutdent=function(e,t){var n=e.getLine(t),i=n.match(/^(\s*\})/);if(!i)return 0;var a=i[1].length,o=e.findMatchingBracket({row:t,column:a});if(!o||o.row==t)return 0;var s=this.$getIndent(e.getLine(o.row));e.replace(new r(t,0,t,a-1),s)},this.$getIndent=function(e){return e.match(/^\s*/)[0]}}).call(i.prototype),t.MatchingBraceOutdent=i}),ace.define(`ace/mode/folding/cstyle`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/range`,`ace/mode/folding/fold_mode`],function(e,t,n){"use strict";var r=e(`../../lib/oop`),i=e(`../../range`).Range,a=e(`./fold_mode`).FoldMode,o=t.FoldMode=function(e){e&&(this.foldingStartMarker=new RegExp(this.foldingStartMarker.source.replace(/\|[^|]*?$/,`|`+e.start)),this.foldingStopMarker=new RegExp(this.foldingStopMarker.source.replace(/\|[^|]*?$/,`|`+e.end)))};r.inherits(o,a),function(){this.foldingStartMarker=/([\{\[\(])[^\}\]\)]*$|^\s*(\/\*)/,this.foldingStopMarker=/^[^\[\{\(]*([\}\]\)])|^[\s\*]*(\*\/)/,this.singleLineBlockCommentRe=/^\s*(\/\*).*\*\/\s*$/,this.tripleStarBlockCommentRe=/^\s*(\/\*\*\*).*\*\/\s*$/,this.startRegionRe=/^\s*(\/\*|\/\/)#?region\b/,this._getFoldWidgetBase=this.getFoldWidget,this.getFoldWidget=function(e,t,n){var r=e.getLine(n);if(this.singleLineBlockCommentRe.test(r)&&!this.startRegionRe.test(r)&&!this.tripleStarBlockCommentRe.test(r))return``;var i=this._getFoldWidgetBase(e,t,n);return!i&&this.startRegionRe.test(r)?`start`:i},this.getFoldWidgetRange=function(e,t,n,r){var i=e.getLine(n);if(this.startRegionRe.test(i))return this.getCommentRegionBlock(e,i,n);var a=i.match(this.foldingStartMarker);if(a){var o=a.index;if(a[1])return this.openingBracketBlock(e,a[1],n,o);var s=e.getCommentFoldRange(n,o+a[0].length,1);return s&&!s.isMultiLine()&&(r?s=this.getSectionRange(e,n):t!=`all`&&(s=null)),s}if(t!==`markbegin`){var a=i.match(this.foldingStopMarker);if(a){var o=a.index+a[0].length;return a[1]?this.closingBracketBlock(e,a[1],n,o):e.getCommentFoldRange(n,o,-1)}}},this.getSectionRange=function(e,t){var n=e.getLine(t),r=n.search(/\S/),a=t,o=n.length;t+=1;for(var s=t,c=e.getLength();++t<c;){n=e.getLine(t);var l=n.search(/\S/);if(l!==-1){if(r>l)break;var u=this.getFoldWidgetRange(e,`all`,t);if(u){if(u.start.row<=a)break;if(u.isMultiLine())t=u.end.row;else if(r==l)break}s=t}}return new i(a,o,s,e.getLine(s).length)},this.getCommentRegionBlock=function(e,t,n){for(var r=t.search(/\s*$/),a=e.getLength(),o=n,s=/^\s*(?:\/\*|\/\/|--)#?(end)?region\b/,c=1;++n<a;){t=e.getLine(n);var l=s.exec(t);if(l&&(l[1]?c--:c++,!c))break}var u=n;if(u>o)return new i(o,r,u,t.length)}}.call(o.prototype)}),ace.define(`ace/mode/json`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/mode/text`,`ace/mode/json_highlight_rules`,`ace/mode/matching_brace_outdent`,`ace/mode/folding/cstyle`,`ace/worker/worker_client`],function(e,t,n){"use strict";var r=e(`../lib/oop`),i=e(`./text`).Mode,a=e(`./json_highlight_rules`).JsonHighlightRules,o=e(`./matching_brace_outdent`).MatchingBraceOutdent,s=e(`./folding/cstyle`).FoldMode,c=e(`../worker/worker_client`).WorkerClient,l=function(){this.HighlightRules=a,this.$outdent=new o,this.$behaviour=this.$defaultBehaviour,this.foldingRules=new s};r.inherits(l,i),function(){this.lineCommentStart=`//`,this.blockComment={start:`/*`,end:`*/`},this.getNextLineIndent=function(e,t,n){var r=this.$getIndent(t);if(e==`start`){var i=t.match(/^.*[\{\(\[]\s*$/);i&&(r+=n)}return r},this.checkOutdent=function(e,t,n){return this.$outdent.checkOutdent(t,n)},this.autoOutdent=function(e,t,n){this.$outdent.autoOutdent(t,n)},this.createWorker=function(e){var t=new c([`ace`],`ace/mode/json_worker`,`JsonWorker`);return t.attachToDocument(e.getDocument()),t.on(`annotate`,function(t){e.setAnnotations(t.data)}),t.on(`terminate`,function(){e.clearAnnotations()}),t},this.$id=`ace/mode/json`}.call(l.prototype),t.Mode=l}),function(){ace.require([`ace/mode/json`],function(n){typeof t==`object`&&typeof exports==`object`&&t&&(t.exports=n)})}()}),g=t((exports,t)=>{ace.define(`ace/ext/searchbox.css`,[`require`,`exports`,`module`],function(e,t,n){n.exports=`

/* ------------------------------------------------------------------------------------------
 * Editor Search Form
 * --------------------------------------------------------------------------------------- */
.ace_search {
    background-color: #ddd;
    color: #666;
    border: 1px solid #cbcbcb;
    border-top: 0 none;
    overflow: hidden;
    margin: 0;
    padding: 4px 6px 0 4px;
    position: absolute;
    top: 0;
    z-index: 99;
    white-space: normal;
}
.ace_search.left {
    border-left: 0 none;
    border-radius: 0px 0px 5px 0px;
    left: 0;
}
.ace_search.right {
    border-radius: 0px 0px 0px 5px;
    border-right: 0 none;
    right: 0;
}

.ace_search_form, .ace_replace_form {
    margin: 0 20px 4px 0;
    overflow: hidden;
    line-height: 1.9;
}
.ace_replace_form {
    margin-right: 0;
}
.ace_search_form.ace_nomatch {
    outline: 1px solid red;
}

.ace_search_field {
    border-radius: 3px 0 0 3px;
    background-color: white;
    color: black;
    border: 1px solid #cbcbcb;
    border-right: 0 none;
    outline: 0;
    padding: 0;
    font-size: inherit;
    margin: 0;
    line-height: inherit;
    padding: 0 6px;
    min-width: 17em;
    vertical-align: top;
    min-height: 1.8em;
    box-sizing: content-box;
}
.ace_searchbtn {
    border: 1px solid #cbcbcb;
    line-height: inherit;
    display: inline-block;
    padding: 0 6px;
    background: #fff;
    border-right: 0 none;
    border-left: 1px solid #dcdcdc;
    cursor: pointer;
    margin: 0;
    position: relative;
    color: #666;
}
.ace_searchbtn:last-child {
    border-radius: 0 3px 3px 0;
    border-right: 1px solid #cbcbcb;
}
.ace_searchbtn:disabled {
    background: none;
    cursor: default;
}
.ace_searchbtn:hover {
    background-color: #eef1f6;
}
.ace_searchbtn.prev, .ace_searchbtn.next {
     padding: 0px 0.7em
}
.ace_searchbtn.prev:after, .ace_searchbtn.next:after {
     content: "";
     border: solid 2px #888;
     width: 0.5em;
     height: 0.5em;
     border-width:  2px 0 0 2px;
     display:inline-block;
     transform: rotate(-45deg);
}
.ace_searchbtn.next:after {
     border-width: 0 2px 2px 0 ;
}
.ace_searchbtn_close {
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAcCAYAAABRVo5BAAAAZ0lEQVR42u2SUQrAMAhDvazn8OjZBilCkYVVxiis8H4CT0VrAJb4WHT3C5xU2a2IQZXJjiQIRMdkEoJ5Q2yMqpfDIo+XY4k6h+YXOyKqTIj5REaxloNAd0xiKmAtsTHqW8sR2W5f7gCu5nWFUpVjZwAAAABJRU5ErkJggg==) no-repeat 50% 0;
    border-radius: 50%;
    border: 0 none;
    color: #656565;
    cursor: pointer;
    font: 16px/16px Arial;
    padding: 0;
    height: 14px;
    width: 14px;
    top: 9px;
    right: 7px;
    position: absolute;
}
.ace_searchbtn_close:hover {
    background-color: #656565;
    background-position: 50% 100%;
    color: white;
}

.ace_button {
    margin-left: 2px;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    -o-user-select: none;
    -ms-user-select: none;
    user-select: none;
    overflow: hidden;
    opacity: 0.7;
    border: 1px solid rgba(100,100,100,0.23);
    padding: 1px;
    box-sizing:    border-box!important;
    color: black;
}

.ace_button:hover {
    background-color: #eee;
    opacity:1;
}
.ace_button:active {
    background-color: #ddd;
}

.ace_button.checked {
    border-color: #3399ff;
    opacity:1;
}

.ace_search_options{
    margin-bottom: 3px;
    text-align: right;
    -webkit-user-select: none;
    -moz-user-select: none;
    -o-user-select: none;
    -ms-user-select: none;
    user-select: none;
    clear: both;
}

.ace_search_counter {
    float: left;
    font-family: arial;
    padding: 0 8px;
}`}),ace.define(`ace/ext/searchbox`,[`require`,`exports`,`module`,`ace/lib/dom`,`ace/lib/lang`,`ace/lib/event`,`ace/ext/searchbox.css`,`ace/keyboard/hash_handler`,`ace/lib/keys`,`ace/config`],function(e,t,n){"use strict";var r=e(`../lib/dom`),i=e(`../lib/lang`),a=e(`../lib/event`),o=e(`./searchbox.css`),s=e(`../keyboard/hash_handler`).HashHandler,c=e(`../lib/keys`),l=e(`../config`).nls,u=999;r.importCssString(o,`ace_searchbox`,!1);var d=function(){function e(e,t,n){var i=r.createElement(`div`);r.buildDom([`div`,{class:`ace_search right`},[`span`,{action:`hide`,class:`ace_searchbtn_close`}],[`div`,{class:`ace_search_form`},[`input`,{class:`ace_search_field`,placeholder:l(`Search for`),spellcheck:`false`}],[`span`,{action:`findPrev`,class:`ace_searchbtn prev`},`​`],[`span`,{action:`findNext`,class:`ace_searchbtn next`},`​`],[`span`,{action:`findAll`,class:`ace_searchbtn`,title:`Alt-Enter`},l(`All`)]],[`div`,{class:`ace_replace_form`},[`input`,{class:`ace_search_field`,placeholder:l(`Replace with`),spellcheck:`false`}],[`span`,{action:`replaceAndFindNext`,class:`ace_searchbtn`},l(`Replace`)],[`span`,{action:`replaceAll`,class:`ace_searchbtn`},l(`All`)]],[`div`,{class:`ace_search_options`},[`span`,{action:`toggleReplace`,class:`ace_button`,title:l(`Toggle Replace mode`),style:`float:left;margin-top:-2px;padding:0 5px;`},`+`],[`span`,{class:`ace_search_counter`}],[`span`,{action:`toggleRegexpMode`,class:`ace_button`,title:l(`RegExp Search`)},`.*`],[`span`,{action:`toggleCaseSensitive`,class:`ace_button`,title:l(`CaseSensitive Search`)},`Aa`],[`span`,{action:`toggleWholeWords`,class:`ace_button`,title:l(`Whole Word Search`)},`\\b`],[`span`,{action:`searchInSelection`,class:`ace_button`,title:l(`Search In Selection`)},`S`]]],i),this.element=i.firstChild,this.setSession=this.setSession.bind(this),this.$init(),this.setEditor(e),r.importCssString(o,`ace_searchbox`,e.container)}return e.prototype.setEditor=function(e){e.searchBox=this,e.renderer.scroller.appendChild(this.element),this.editor=e},e.prototype.setSession=function(e){this.searchRange=null,this.$syncOptions(!0)},e.prototype.$initElements=function(e){this.searchBox=e.querySelector(`.ace_search_form`),this.replaceBox=e.querySelector(`.ace_replace_form`),this.searchOption=e.querySelector(`[action=searchInSelection]`),this.replaceOption=e.querySelector(`[action=toggleReplace]`),this.regExpOption=e.querySelector(`[action=toggleRegexpMode]`),this.caseSensitiveOption=e.querySelector(`[action=toggleCaseSensitive]`),this.wholeWordOption=e.querySelector(`[action=toggleWholeWords]`),this.searchInput=this.searchBox.querySelector(`.ace_search_field`),this.replaceInput=this.replaceBox.querySelector(`.ace_search_field`),this.searchCounter=e.querySelector(`.ace_search_counter`)},e.prototype.$init=function(){var e=this.element;this.$initElements(e);var t=this;a.addListener(e,`mousedown`,function(e){setTimeout(function(){t.activeInput.focus()},0),a.stopPropagation(e)}),a.addListener(e,`click`,function(e){var n=e.target||e.srcElement,r=n.getAttribute(`action`);r&&t[r]?t[r]():t.$searchBarKb.commands[r]&&t.$searchBarKb.commands[r].exec(t),a.stopPropagation(e)}),a.addCommandKeyListener(e,function(e,n,r){var i=c.keyCodeToString(r),o=t.$searchBarKb.findKeyCommand(n,i);o&&o.exec&&(o.exec(t),a.stopEvent(e))}),this.$onChange=i.delayedCall(function(){t.find(!1,!1)}),a.addListener(this.searchInput,`input`,function(){t.$onChange.schedule(20)}),a.addListener(this.searchInput,`focus`,function(){t.activeInput=t.searchInput,t.searchInput.value&&t.highlight()}),a.addListener(this.replaceInput,`focus`,function(){t.activeInput=t.replaceInput,t.searchInput.value&&t.highlight()})},e.prototype.setSearchRange=function(e){this.searchRange=e,e?this.searchRangeMarker=this.editor.session.addMarker(e,`ace_active-line`):this.searchRangeMarker&&(this.editor.session.removeMarker(this.searchRangeMarker),this.searchRangeMarker=null)},e.prototype.$syncOptions=function(e){r.setCssClass(this.replaceOption,`checked`,this.searchRange),r.setCssClass(this.searchOption,`checked`,this.searchOption.checked),this.replaceOption.textContent=this.replaceOption.checked?`-`:`+`,r.setCssClass(this.regExpOption,`checked`,this.regExpOption.checked),r.setCssClass(this.wholeWordOption,`checked`,this.wholeWordOption.checked),r.setCssClass(this.caseSensitiveOption,`checked`,this.caseSensitiveOption.checked);var t=this.editor.getReadOnly();this.replaceOption.style.display=t?`none`:``,this.replaceBox.style.display=this.replaceOption.checked&&!t?``:`none`,this.find(!1,!1,e)},e.prototype.highlight=function(e){this.editor.session.highlight(e||this.editor.$search.$options.re),this.editor.renderer.updateBackMarkers()},e.prototype.find=function(e,t,n){var i=this.editor.find(this.searchInput.value,{skipCurrent:e,backwards:t,wrap:!0,regExp:this.regExpOption.checked,caseSensitive:this.caseSensitiveOption.checked,wholeWord:this.wholeWordOption.checked,preventScroll:n,range:this.searchRange}),a=!i&&this.searchInput.value;r.setCssClass(this.searchBox,`ace_nomatch`,a),this.editor._emit(`findSearchBox`,{match:!a}),this.highlight(),this.updateCounter()},e.prototype.updateCounter=function(){var e=this.editor,t=e.$search.$options.re,n=0,r=0;if(t){var i=this.searchRange?e.session.getTextRange(this.searchRange):e.getValue(),a=e.session.doc.positionToIndex(e.selection.anchor);this.searchRange&&(a-=e.session.doc.positionToIndex(this.searchRange.start));for(var o=t.lastIndex=0,s;(s=t.exec(i))&&(n++,o=s.index,o<=a&&r++,!(n>u||!s[0]&&(t.lastIndex=o+=1,o>=i.length))););}this.searchCounter.textContent=l(`$0 of $1`,[r,n>u?u+`+`:n])},e.prototype.findNext=function(){this.find(!0,!1)},e.prototype.findPrev=function(){this.find(!0,!0)},e.prototype.findAll=function(){var e=this.editor.findAll(this.searchInput.value,{regExp:this.regExpOption.checked,caseSensitive:this.caseSensitiveOption.checked,wholeWord:this.wholeWordOption.checked}),t=!e&&this.searchInput.value;r.setCssClass(this.searchBox,`ace_nomatch`,t),this.editor._emit(`findSearchBox`,{match:!t}),this.highlight(),this.hide()},e.prototype.replace=function(){this.editor.getReadOnly()||this.editor.replace(this.replaceInput.value)},e.prototype.replaceAndFindNext=function(){this.editor.getReadOnly()||(this.editor.replace(this.replaceInput.value),this.findNext())},e.prototype.replaceAll=function(){this.editor.getReadOnly()||this.editor.replaceAll(this.replaceInput.value)},e.prototype.hide=function(){this.active=!1,this.setSearchRange(null),this.editor.off(`changeSession`,this.setSession),this.element.style.display=`none`,this.editor.keyBinding.removeKeyboardHandler(this.$closeSearchBarKb),this.editor.focus()},e.prototype.show=function(e,t){this.active=!0,this.editor.on(`changeSession`,this.setSession),this.element.style.display=``,this.replaceOption.checked=t,e&&(this.searchInput.value=e),this.searchInput.focus(),this.searchInput.select(),this.editor.keyBinding.addKeyboardHandler(this.$closeSearchBarKb),this.$syncOptions(!0)},e.prototype.isFocused=function(){var e=document.activeElement;return e==this.searchInput||e==this.replaceInput},e}(),f=new s;f.bindKeys({"Ctrl-f|Command-f":function(e){var t=e.isReplace=!e.isReplace;e.replaceBox.style.display=t?``:`none`,e.replaceOption.checked=!1,e.$syncOptions(),e.searchInput.focus()},"Ctrl-H|Command-Option-F":function(e){e.editor.getReadOnly()||(e.replaceOption.checked=!0,e.$syncOptions(),e.replaceInput.focus())},"Ctrl-G|Command-G":function(e){e.findNext()},"Ctrl-Shift-G|Command-Shift-G":function(e){e.findPrev()},esc:function(e){setTimeout(function(){e.hide()})},Return:function(e){e.activeInput==e.replaceInput&&e.replace(),e.findNext()},"Shift-Return":function(e){e.activeInput==e.replaceInput&&e.replace(),e.findPrev()},"Alt-Return":function(e){e.activeInput==e.replaceInput&&e.replaceAll(),e.findAll()},Tab:function(e){(e.activeInput==e.replaceInput?e.searchInput:e.replaceInput).focus()}}),f.addCommands([{name:`toggleRegexpMode`,bindKey:{win:`Alt-R|Alt-/`,mac:`Ctrl-Alt-R|Ctrl-Alt-/`},exec:function(e){e.regExpOption.checked=!e.regExpOption.checked,e.$syncOptions()}},{name:`toggleCaseSensitive`,bindKey:{win:`Alt-C|Alt-I`,mac:`Ctrl-Alt-R|Ctrl-Alt-I`},exec:function(e){e.caseSensitiveOption.checked=!e.caseSensitiveOption.checked,e.$syncOptions()}},{name:`toggleWholeWords`,bindKey:{win:`Alt-B|Alt-W`,mac:`Ctrl-Alt-B|Ctrl-Alt-W`},exec:function(e){e.wholeWordOption.checked=!e.wholeWordOption.checked,e.$syncOptions()}},{name:`toggleReplace`,exec:function(e){e.replaceOption.checked=!e.replaceOption.checked,e.$syncOptions()}},{name:`searchInSelection`,exec:function(e){e.searchOption.checked=!e.searchRange,e.setSearchRange(e.searchOption.checked&&e.editor.getSelectionRange()),e.$syncOptions()}}]);var p=new s([{bindKey:`Esc`,name:`closeSearchBar`,exec:function(e){e.searchBox.hide()}}]);d.prototype.$searchBarKb=f,d.prototype.$closeSearchBarKb=p,t.SearchBox=d,t.Search=function(e,t){var n=e.searchBox||new d(e);n.show(e.session.getTextRange(),t)}}),function(){ace.require([`ace/ext/searchbox`],function(n){typeof t==`object`&&typeof exports==`object`&&t&&(t.exports=n)})}()}),_=t((exports,t)=>{ace.define(`ace/mode/xml_highlight_rules`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/mode/text_highlight_rules`],function(e,t,n){"use strict";var r=e(`../lib/oop`),i=e(`./text_highlight_rules`).TextHighlightRules,a=function(e){var t=`[_:a-zA-ZÀ-￿][-_:.a-zA-Z0-9À-￿]*`;this.$rules={start:[{token:`string.cdata.xml`,regex:`<\\!\\[CDATA\\[`,next:`cdata`},{token:[`punctuation.instruction.xml`,`keyword.instruction.xml`],regex:`(<\\?)(`+t+`)`,next:`processing_instruction`},{token:`comment.start.xml`,regex:`<\\!--`,next:`comment`},{token:[`xml-pe.doctype.xml`,`xml-pe.doctype.xml`],regex:`(<\\!)(DOCTYPE)(?=[\\s])`,next:`doctype`,caseInsensitive:!0},{include:`tag`},{token:`text.end-tag-open.xml`,regex:`</`},{token:`text.tag-open.xml`,regex:`<`},{include:`reference`},{defaultToken:`text.xml`}],processing_instruction:[{token:`entity.other.attribute-name.decl-attribute-name.xml`,regex:t},{token:`keyword.operator.decl-attribute-equals.xml`,regex:`=`},{include:`whitespace`},{include:`string`},{token:`punctuation.xml-decl.xml`,regex:`\\?>`,next:`start`}],doctype:[{include:`whitespace`},{include:`string`},{token:`xml-pe.doctype.xml`,regex:`>`,next:`start`},{token:`xml-pe.xml`,regex:`[-_a-zA-Z0-9:]+`},{token:`punctuation.int-subset`,regex:`\\[`,push:`int_subset`}],int_subset:[{token:`text.xml`,regex:`\\s+`},{token:`punctuation.int-subset.xml`,regex:`]`,next:`pop`},{token:[`punctuation.markup-decl.xml`,`keyword.markup-decl.xml`],regex:`(<\\!)(`+t+`)`,push:[{token:`text`,regex:`\\s+`},{token:`punctuation.markup-decl.xml`,regex:`>`,next:`pop`},{include:`string`}]}],cdata:[{token:`string.cdata.xml`,regex:`\\]\\]>`,next:`start`},{token:`text.xml`,regex:`\\s+`},{token:`text.xml`,regex:`(?:[^\\]]|\\](?!\\]>))+`}],comment:[{token:`comment.end.xml`,regex:`-->`,next:`start`},{defaultToken:`comment.xml`}],reference:[{token:`constant.language.escape.reference.xml`,regex:`(?:&#[0-9]+;)|(?:&#x[0-9a-fA-F]+;)|(?:&[a-zA-Z0-9_:\\.-]+;)`}],attr_reference:[{token:`constant.language.escape.reference.attribute-value.xml`,regex:`(?:&#[0-9]+;)|(?:&#x[0-9a-fA-F]+;)|(?:&[a-zA-Z0-9_:\\.-]+;)`}],tag:[{token:[`meta.tag.punctuation.tag-open.xml`,`meta.tag.punctuation.end-tag-open.xml`,`meta.tag.tag-name.xml`],regex:`(?:(<)|(</))((?:`+t+`:)?`+t+`)`,next:[{include:`attributes`},{token:`meta.tag.punctuation.tag-close.xml`,regex:`/?>`,next:`start`}]}],tag_whitespace:[{token:`text.tag-whitespace.xml`,regex:`\\s+`}],whitespace:[{token:`text.whitespace.xml`,regex:`\\s+`}],string:[{token:`string.xml`,regex:`'`,push:[{token:`string.xml`,regex:`'`,next:`pop`},{defaultToken:`string.xml`}]},{token:`string.xml`,regex:`"`,push:[{token:`string.xml`,regex:`"`,next:`pop`},{defaultToken:`string.xml`}]}],attributes:[{token:`entity.other.attribute-name.xml`,regex:t},{token:`keyword.operator.attribute-equals.xml`,regex:`=`},{include:`tag_whitespace`},{include:`attribute_value`}],attribute_value:[{token:`string.attribute-value.xml`,regex:`'`,push:[{token:`string.attribute-value.xml`,regex:`'`,next:`pop`},{include:`attr_reference`},{defaultToken:`string.attribute-value.xml`}]},{token:`string.attribute-value.xml`,regex:`"`,push:[{token:`string.attribute-value.xml`,regex:`"`,next:`pop`},{include:`attr_reference`},{defaultToken:`string.attribute-value.xml`}]}]},this.constructor===a&&this.normalizeRules()};(function(){this.embedTagRules=function(e,t,n){this.$rules.tag.unshift({token:[`meta.tag.punctuation.tag-open.xml`,`meta.tag.`+n+`.tag-name.xml`],regex:`(<)(`+n+`(?=\\s|>|$))`,next:[{include:`attributes`},{token:`meta.tag.punctuation.tag-close.xml`,regex:`/?>`,next:t+`start`}]}),this.$rules[n+`-end`]=[{include:`attributes`},{token:`meta.tag.punctuation.tag-close.xml`,regex:`/?>`,next:`start`,onMatch:function(e,t,n){return n.splice(0),this.token}}],this.embedRules(e,t,[{token:[`meta.tag.punctuation.end-tag-open.xml`,`meta.tag.`+n+`.tag-name.xml`],regex:`(</)(`+n+`(?=\\s|>|$))`,next:n+`-end`},{token:`string.cdata.xml`,regex:`<\\!\\[CDATA\\[`},{token:`string.cdata.xml`,regex:`\\]\\]>`}])}}).call(i.prototype),r.inherits(a,i),t.XmlHighlightRules=a}),ace.define(`ace/mode/behaviour/xml`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/mode/behaviour`,`ace/token_iterator`,`ace/lib/lang`],function(e,t,n){"use strict";var r=e(`../../lib/oop`),i=e(`../behaviour`).Behaviour,a=e(`../../token_iterator`).TokenIterator,o=e(`../../lib/lang`);function s(e,t){return e&&e.type.lastIndexOf(t+`.xml`)>-1}var c=function(){this.add(`string_dquotes`,`insertion`,function(e,t,n,r,i){if(i==`"`||i==`'`){var o=i,c=r.doc.getTextRange(n.getSelectionRange());if(c!==``&&c!==`'`&&c!=`"`&&n.getWrapBehavioursEnabled())return{text:o+c+o,selection:!1};var l=n.getCursorPosition(),u=r.doc.getLine(l.row),d=u.substring(l.column,l.column+1),f=new a(r,l.row,l.column),p=f.getCurrentToken();if(d==o&&(s(p,`attribute-value`)||s(p,`string`)))return{text:``,selection:[1,1]};if(p||=f.stepBackward(),!p)return;for(;s(p,`tag-whitespace`)||s(p,`whitespace`);)p=f.stepBackward();var m=!d||d.match(/\s/);if(s(p,`attribute-equals`)&&(m||d==`>`)||s(p,`decl-attribute-equals`)&&(m||d==`?`))return{text:o+o,selection:[1,1]}}}),this.add(`string_dquotes`,`deletion`,function(e,t,n,r,i){var a=r.doc.getTextRange(i);if(!i.isMultiLine()&&(a==`"`||a==`'`)){var o=r.doc.getLine(i.start.row),s=o.substring(i.start.column+1,i.start.column+2);if(s==a)return i.end.column++,i}}),this.add(`autoclosing`,`insertion`,function(e,t,n,r,i){if(i==`>`){var o=n.getSelectionRange().start,c=new a(r,o.row,o.column),l=c.getCurrentToken()||c.stepBackward();if(!l||!(s(l,`tag-name`)||s(l,`tag-whitespace`)||s(l,`attribute-name`)||s(l,`attribute-equals`)||s(l,`attribute-value`))||s(l,`reference.attribute-value`))return;if(s(l,`attribute-value`)){var u=c.getCurrentTokenColumn()+l.value.length;if(o.column<u)return;if(o.column==u){var d=c.stepForward();if(d&&s(d,`attribute-value`))return;c.stepBackward()}}if(/^\s*>/.test(r.getLine(o.row).slice(o.column)))return;for(;!s(l,`tag-name`);)if(l=c.stepBackward(),l.value==`<`){l=c.stepForward();break}var f=c.getCurrentTokenRow(),p=c.getCurrentTokenColumn();if(s(c.stepBackward(),`end-tag-open`))return;var m=l.value;return f==o.row&&(m=m.substring(0,o.column-p)),this.voidElements.hasOwnProperty(m.toLowerCase())?void 0:{text:`></`+m+`>`,selection:[1,1]}}}),this.add(`autoindent`,`insertion`,function(e,t,n,r,i){if(i==`
`){var o=n.getCursorPosition(),s=r.getLine(o.row),c=new a(r,o.row,o.column),l=c.getCurrentToken();if(l&&l.type.indexOf(`tag-close`)!==-1){if(l.value==`/>`)return;for(;l&&l.type.indexOf(`tag-name`)===-1;)l=c.stepBackward();if(!l)return;var u=l.value,d=c.getCurrentTokenRow();if(l=c.stepBackward(),!l||l.type.indexOf(`end-tag`)!==-1)return;if(this.voidElements&&!this.voidElements[u]){var f=r.getTokenAt(o.row,o.column+1),s=r.getLine(d),p=this.$getIndent(s),m=p+r.getTabString();return f&&f.value===`</`?{text:`
`+m+`
`+p,selection:[1,m.length,1,m.length]}:{text:`
`+m}}}}})};r.inherits(c,i),t.XmlBehaviour=c}),ace.define(`ace/mode/folding/xml`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/range`,`ace/mode/folding/fold_mode`],function(e,t,n){"use strict";var r=e(`../../lib/oop`),i=e(`../../range`).Range,a=e(`./fold_mode`).FoldMode,o=t.FoldMode=function(e,t){a.call(this),this.voidElements=e||{},this.optionalEndTags=r.mixin({},this.voidElements),t&&r.mixin(this.optionalEndTags,t)};r.inherits(o,a);var s=function(){this.tagName=``,this.closing=!1,this.selfClosing=!1,this.start={row:0,column:0},this.end={row:0,column:0}};function c(e,t){return e.type.lastIndexOf(t+`.xml`)>-1}(function(){this.getFoldWidget=function(e,t,n){var r=this._getFirstTagInLine(e,n);return r?r.closing||!r.tagName&&r.selfClosing?t===`markbeginend`?`end`:``:!r.tagName||r.selfClosing||this.voidElements.hasOwnProperty(r.tagName.toLowerCase())||this._findEndTagInLine(e,n,r.tagName,r.end.column)?``:`start`:this.getCommentFoldWidget(e,n)},this.getCommentFoldWidget=function(e,t){return/comment/.test(e.getState(t))&&/<!-/.test(e.getLine(t))?`start`:``},this._getFirstTagInLine=function(e,t){for(var n=e.getTokens(t),r=new s,i=0;i<n.length;i++){var a=n[i];if(c(a,`tag-open`)){if(r.end.column=r.start.column+a.value.length,r.closing=c(a,`end-tag-open`),a=n[++i],!a)return null;for(r.tagName=a.value,r.end.column+=a.value.length,i++;i<n.length;i++)if(a=n[i],r.end.column+=a.value.length,c(a,`tag-close`)){r.selfClosing=a.value==`/>`;break}return r}else if(c(a,`tag-close`))return r.selfClosing=a.value==`/>`,r;r.start.column+=a.value.length}return null},this._findEndTagInLine=function(e,t,n,r){for(var i=e.getTokens(t),a=0,o=0;o<i.length;o++){var s=i[o];if(a+=s.value.length,!(a<r)&&c(s,`end-tag-open`)&&(s=i[o+1],s&&s.value==n))return!0}return!1},this.getFoldWidgetRange=function(e,t,n){var r=e.getMatchingTags({row:n,column:0});return r?new i(r.openTag.end.row,r.openTag.end.column,r.closeTag.start.row,r.closeTag.start.column):this.getCommentFoldWidget(e,n)&&e.getCommentFoldRange(n,e.getLine(n).length)}}).call(o.prototype)}),ace.define(`ace/mode/xml`,[`require`,`exports`,`module`,`ace/lib/oop`,`ace/lib/lang`,`ace/mode/text`,`ace/mode/xml_highlight_rules`,`ace/mode/behaviour/xml`,`ace/mode/folding/xml`,`ace/worker/worker_client`],function(e,t,n){"use strict";var r=e(`../lib/oop`),i=e(`../lib/lang`),a=e(`./text`).Mode,o=e(`./xml_highlight_rules`).XmlHighlightRules,s=e(`./behaviour/xml`).XmlBehaviour,c=e(`./folding/xml`).FoldMode,l=e(`../worker/worker_client`).WorkerClient,u=function(){this.HighlightRules=o,this.$behaviour=new s,this.foldingRules=new c};r.inherits(u,a),function(){this.voidElements=i.arrayToMap([]),this.blockComment={start:`<!--`,end:`-->`},this.createWorker=function(e){var t=new l([`ace`],`ace/mode/xml_worker`,`Worker`);return t.attachToDocument(e.getDocument()),t.on(`error`,function(t){e.setAnnotations(t.data)}),t.on(`terminate`,function(){e.clearAnnotations()}),t},this.$id=`ace/mode/xml`}.call(u.prototype),t.Mode=u}),function(){ace.require([`ace/mode/xml`],function(n){typeof t==`object`&&typeof exports==`object`&&t&&(t.exports=n)})}()}),v=t((exports,t)=>{(function(){ace.require([`ace/mode/text`],function(n){typeof t==`object`&&typeof exports==`object`&&t&&(t.exports=n)})})()}),y=n(h()),b=n(g()),x=n(_()),S=n(v()),C=n(p()),w=n(m()),T=n(f());const E={key:0},D={key:1},O={__name:`EditorDebugShow`,props:{value:{type:String,required:!0,default:``},mode:{type:String,required:!0,default:`json`},debugResponse:{type:Boolean,default:!1}},emits:[`update:value`,`debugEditorChange`,`showDescription`],setup(t,{emit:n}){let f=t,p=c(f.value);d(()=>f.value,()=>{p.value=f.value});let m=s({editor:null,editorHeight:380,debugOptions:{readOnly:!1,autoScrollEditorIntoView:!0,displayIndentGuides:!1,fixedWidthGutter:!0},commonOptions:{readOnly:!1}}),{editor:h,editorHeight:g,debugOptions:_,commonOptions:v}=l(m);function y(){}function b(){n(`update:value`,p.value),f.debugResponse||y()}function x(e){m.editor=e,f.debugResponse?(m.editor.getSession().setUseWrapMode(!0),m.editor.setOptions(m.debugOptions),f.mode===`text`&&m.editor.getSession().setUseWrapMode(!0)):m.editor.setOptions(m.commonOptions),y(),m.editor.renderer.on(`afterRender`,function(){let e=m.editor.session.getLength();n(`showDescription`,e)})}return(n,s)=>(o(),r(`div`,null,[t.debugResponse?(o(),r(`div`,E,[i(u(e),{class:`knife4j-debug-ace-editor`,onInput:b,options:u(_),value:p.value,"onUpdate:value":s[0]||=e=>p.value=e,onInit:x,lang:t.mode,theme:`eclipse`,width:`100%`,style:a({height:u(g)+`px`})},null,8,[`options`,`value`,`lang`,`style`])])):(o(),r(`div`,D,[i(u(e),{value:p.value,"onUpdate:value":s[1]||=e=>p.value=e,onInit:x,onInput:b,lang:t.mode,theme:`eclipse`,width:`100%`,style:a({height:u(g)+`px`})},null,8,[`value`,`lang`,`style`])]))]))}};var k=O;export{k as default};