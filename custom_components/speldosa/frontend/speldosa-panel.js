var Le=Object.defineProperty;var Te=(a,e,t)=>e in a?Le(a,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):a[e]=t;var W=(a,e,t)=>Te(a,typeof e!="symbol"?e+"":e,t);var H=globalThis,O=H.ShadowRoot&&(H.ShadyCSS===void 0||H.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,D=Symbol(),ae=new WeakMap,S=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==D)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(O&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=ae.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&ae.set(t,e))}return e}toString(){return this.cssText}},ne=a=>new S(typeof a=="string"?a:a+"",void 0,D),q=(a,...e)=>{let t=a.length===1?a[0]:e.reduce((s,i,n)=>s+(r=>{if(r._$cssResult$===!0)return r.cssText;if(typeof r=="number")return r;throw Error("Value passed to 'css' function must be a 'css' function result: "+r+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+a[n+1],a[0]);return new S(t,a,D)},re=(a,e)=>{if(O)a.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=H.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,a.appendChild(s)}},K=O?a=>a:a=>a instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return ne(t)})(a):a;var{is:Pe,defineProperty:Ne,getOwnPropertyDescriptor:Ue,getOwnPropertyNames:Me,getOwnPropertySymbols:Re,getPrototypeOf:He}=Object,j=globalThis,oe=j.trustedTypes,Oe=oe?oe.emptyScript:"",je=j.reactiveElementPolyfillSupport,A=(a,e)=>a,V={toAttribute(a,e){switch(e){case Boolean:a=a?Oe:null;break;case Object:case Array:a=a==null?a:JSON.stringify(a)}return a},fromAttribute(a,e){let t=a;switch(e){case Boolean:t=a!==null;break;case Number:t=a===null?null:Number(a);break;case Object:case Array:try{t=JSON.parse(a)}catch{t=null}}return t}},de=(a,e)=>!Pe(a,e),le={attribute:!0,type:String,converter:V,reflect:!1,useDefault:!1,hasChanged:de};Symbol.metadata??=Symbol("metadata"),j.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=le){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&Ne(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:n}=Ue(this.prototype,e)??{get(){return this[t]},set(r){this[t]=r}};return{get:i,set(r){let h=i?.call(this);n?.call(this,r),this.requestUpdate(e,h,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??le}static _$Ei(){if(this.hasOwnProperty(A("elementProperties")))return;let e=He(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(A("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(A("properties"))){let t=this.properties,s=[...Me(t),...Re(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(K(i))}else e!==void 0&&t.push(K(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return re(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:V).toAttribute(t,s.type);this._$Em=e,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let n=s.getPropertyOptions(i),r=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:V;this._$Em=i;let h=r.fromAttribute(t,n.type);this[i]=h??this._$Ej?.get(i)??h,this._$Em=null}}requestUpdate(e,t,s,i=!1,n){if(e!==void 0){let r=this.constructor;if(i===!1&&(n=this[e]),s??=r.getPropertyOptions(e),!((s.hasChanged??de)(n,t)||s.useDefault&&s.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(r._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:n},r){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,r??t??this[e]),n!==!0||r!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,n]of s){let{wrapped:r}=n,h=this[i];r!==!0||this._$AL.has(i)||h===void 0||this.C(i,void 0,n,h)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[A("elementProperties")]=new Map,g[A("finalized")]=new Map,je?.({ReactiveElement:g}),(j.reactiveElementVersions??=[]).push("2.1.2");var Y=globalThis,he=a=>a,z=Y.trustedTypes,ce=z?z.createPolicy("lit-html",{createHTML:a=>a}):void 0,be="$lit$",b=`lit$${Math.random().toFixed(9).slice(2)}$`,fe="?"+b,ze=`<${fe}>`,$=document,C=()=>$.createComment(""),L=a=>a===null||typeof a!="object"&&typeof a!="function",ee=Array.isArray,Be=a=>ee(a)||typeof a?.[Symbol.iterator]=="function",F=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,pe=/-->/g,ue=/>/g,y=RegExp(`>|${F}(?:([^\\s"'>=/]+)(${F}*=${F}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),_e=/'/g,ge=/"/g,ye=/^(?:script|style|textarea|title)$/i,te=a=>(e,...t)=>({_$litType$:a,strings:e,values:t}),o=te(1),tt=te(2),st=te(3),x=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),me=new WeakMap,v=$.createTreeWalker($,129);function ve(a,e){if(!ee(a)||!a.hasOwnProperty("raw"))throw Error("invalid template strings array");return ce!==void 0?ce.createHTML(e):e}var Ie=(a,e)=>{let t=a.length-1,s=[],i,n=e===2?"<svg>":e===3?"<math>":"",r=E;for(let h=0;h<t;h++){let l=a[h],p,u,c=-1,_=0;for(;_<l.length&&(r.lastIndex=_,u=r.exec(l),u!==null);)_=r.lastIndex,r===E?u[1]==="!--"?r=pe:u[1]!==void 0?r=ue:u[2]!==void 0?(ye.test(u[2])&&(i=RegExp("</"+u[2],"g")),r=y):u[3]!==void 0&&(r=y):r===y?u[0]===">"?(r=i??E,c=-1):u[1]===void 0?c=-2:(c=r.lastIndex-u[2].length,p=u[1],r=u[3]===void 0?y:u[3]==='"'?ge:_e):r===ge||r===_e?r=y:r===pe||r===ue?r=E:(r=y,i=void 0);let m=r===y&&a[h+1].startsWith("/>")?" ":"";n+=r===E?l+ze:c>=0?(s.push(p),l.slice(0,c)+be+l.slice(c)+b+m):l+b+(c===-2?h:m)}return[ve(a,n+(a[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},T=class a{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let n=0,r=0,h=e.length-1,l=this.parts,[p,u]=Ie(e,t);if(this.el=a.createElement(p,s),v.currentNode=this.el.content,t===2||t===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(i=v.nextNode())!==null&&l.length<h;){if(i.nodeType===1){if(i.hasAttributes())for(let c of i.getAttributeNames())if(c.endsWith(be)){let _=u[r++],m=i.getAttribute(c).split(b),R=/([.?@])?(.*)/.exec(_);l.push({type:1,index:n,name:R[2],strings:m,ctor:R[1]==="."?Q:R[1]==="?"?G:R[1]==="@"?X:w}),i.removeAttribute(c)}else c.startsWith(b)&&(l.push({type:6,index:n}),i.removeAttribute(c));if(ye.test(i.tagName)){let c=i.textContent.split(b),_=c.length-1;if(_>0){i.textContent=z?z.emptyScript:"";for(let m=0;m<_;m++)i.append(c[m],C()),v.nextNode(),l.push({type:2,index:++n});i.append(c[_],C())}}}else if(i.nodeType===8)if(i.data===fe)l.push({type:2,index:n});else{let c=-1;for(;(c=i.data.indexOf(b,c+1))!==-1;)l.push({type:7,index:n}),c+=b.length-1}n++}}static createElement(e,t){let s=$.createElement("template");return s.innerHTML=e,s}};function k(a,e,t=a,s){if(e===x)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,n=L(e)?void 0:e._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(a),i._$AT(a,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=k(a,i._$AS(a,e.values),i,s)),e}var J=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??$).importNode(t,!0);v.currentNode=i;let n=v.nextNode(),r=0,h=0,l=s[0];for(;l!==void 0;){if(r===l.index){let p;l.type===2?p=new P(n,n.nextSibling,this,e):l.type===1?p=new l.ctor(n,l.name,l.strings,this,e):l.type===6&&(p=new Z(n,this,e)),this._$AV.push(p),l=s[++h]}r!==l?.index&&(n=v.nextNode(),r++)}return v.currentNode=$,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},P=class a{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=k(this,e,t),L(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==x&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Be(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&L(this._$AH)?this._$AA.nextSibling.data=e:this.T($.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=T.createElement(ve(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let n=new J(i,this),r=n.u(this.options);n.p(t),this.T(r),this._$AH=n}}_$AC(e){let t=me.get(e.strings);return t===void 0&&me.set(e.strings,t=new T(e)),t}k(e){ee(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let n of e)i===t.length?t.push(s=new a(this.O(C()),this.O(C()),this,this.options)):s=t[i],s._$AI(n),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=he(e).nextSibling;he(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},w=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,n){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=d}_$AI(e,t=this,s,i){let n=this.strings,r=!1;if(n===void 0)e=k(this,e,t,0),r=!L(e)||e!==this._$AH&&e!==x,r&&(this._$AH=e);else{let h=e,l,p;for(e=n[0],l=0;l<n.length-1;l++)p=k(this,h[s+l],t,l),p===x&&(p=this._$AH[l]),r||=!L(p)||p!==this._$AH[l],p===d?e=d:e!==d&&(e+=(p??"")+n[l+1]),this._$AH[l]=p}r&&!i&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},Q=class extends w{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}},G=class extends w{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}},X=class extends w{constructor(e,t,s,i,n){super(e,t,s,i,n),this.type=5}_$AI(e,t=this){if((e=k(this,e,t,0)??d)===x)return;let s=this._$AH,i=e===d&&s!==d||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,n=e!==d&&(s===d||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},Z=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){k(this,e)}};var We=Y.litHtmlPolyfillSupport;We?.(T,P),(Y.litHtmlVersions??=[]).push("3.3.3");var $e=(a,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let n=t?.renderBefore??null;s._$litPart$=i=new P(e.insertBefore(C(),n),n,void 0,t??{})}return i._$AI(a),i};var se=globalThis,f=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=$e(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}};f._$litElement$=!0,f.finalized=!0,se.litElementHydrateSupport?.({LitElement:f});var De=se.litElementPolyfillSupport;De?.({LitElement:f});(se.litElementVersions??=[]).push("4.2.2");var B=class{constructor(e){this.hass=e}overview(){return this.hass.callWS({type:"speldosa/overview"})}search(e,t,s){let i={type:"speldosa/search",query:e};return t&&(i.box_id=t),s&&s.length&&(i.types=s),this.hass.callWS(i)}nowPlaying(e){let t={type:"speldosa/now_playing"};return e&&(t.box_id=e),this.hass.callWS(t)}link({uid:e,item:t,name:s,mode:i,boxId:n,episodes:r}){let h={type:"speldosa/tag/link",uid:e,uri:t.uri,media_type:t.media_type,name:s||t.name,mode:i,image:t.source_image??t.image??null,subtitle:t.subtitle??null};return n&&(h.box_id=n),r&&(h.episodes=r.map(({uri:l,title:p,number:u,included:c})=>({uri:l,title:p,number:u,included:c}))),this.hass.callWS(h)}episodes(e,t,s){let i={type:"speldosa/episodes",uri:e.uri,media_type:e.media_type};return t&&(i.uid=t),s&&(i.box_id=s),this.hass.callWS(i)}tag(e){return this.hass.callWS({type:"speldosa/tag/get",uid:e})}update(e,t){return this.hass.callWS({type:"speldosa/tag/update",uid:e,...t})}unlink(e){return this.hass.callWS({type:"speldosa/tag/unlink",uid:e})}tryPlay(e,t,s){let i={type:"speldosa/tag/try",uri:e.uri,media_type:e.media_type};return t&&(i.mode=t),s&&(i.box_id=s),this.hass.callWS(i)}forgetSeen(e){return this.hass.callWS({type:"speldosa/seen/forget",uid:e})}subscribe(e){return this.hass.connection.subscribeMessage(e,{type:"speldosa/subscribe"})}};function xe(a,e){let t=null,s=(...i)=>{clearTimeout(t),t=setTimeout(()=>a(...i),e)};return s.cancel=()=>clearTimeout(t),s}var ie={title:"Speldosa",boxes:"Boxes",linked_tags:"Linked tags",linked_hint:"A tag plays the same on every box in the home",seen:"Seen, not linked",seen_on:"Last seen on {box}, {when}",on_box_now:"On {box} now",new_tag_title:"A new tag is on {box}",new_tag_text:"Tag {tag} has no music yet. Leave it on the box and pick what it should play.",link_this:"Link this tag",link:"Link",forget:"Forget",link_new:"Link a new tag",link_new_hint:"Put it on any box first",no_tag_on_box:"No new tag is on a box. Put the tag on a box, then select Link a new tag again.",no_box:"No Speldosa box is set up yet. Add one under Settings, Devices and services, Add integration, Speldosa.",no_tags:"No tags are linked yet.",change:"Change",unlink:"Unlink",unlink_confirm:"Unlink {name}? The tag stays, it just plays nothing until you link it again.",play_on:"Play on {player}",try_on:"Try on {player}",playing_on:"Playing on {player}",tag_on:"Tag on: {state}",tag_none:"No tag on",tag_id:"Tag {tag}",tag_on_named:"Tag on: {name}",tag_on_unlinked:"Tag on: not linked",linked:"linked",not_linked:"not linked",reader_ok:"Reader OK",reader_problem:"Reader problem: unplug the box for a few seconds",offline:"Offline",plays_on:"plays on {player}",back:"Back",link_tag_title:"Link tag {tag}",change_tag_title:"Change {name}",search_label:"Search Music Assistant",search_hint:"Searches your Music Assistant library and its services, such as Spotify",too_short:"Type at least 3 characters",searching:"Searching",empty:"Nothing came back. If you expected results, Spotify may be busy: try again in half a minute.",try_again:"Try again",all:"All",best:"Best match",weaker:"Weaker matches",weaker_hint:"Results that match only some of the words",now_playing:"Playing on {player} now",link_album:"Link the album",link_song:"Link the song",pick_first:"Pick what the tag should play",current_content:"Plays now: {name}",name_label:"Name on the tag list",how_it_plays:"How it plays",mode_from_start:"From the start",mode_shuffle:"In random order",mode_random_episode:"A random episode each time",mode_random_episode_hint:"Plays one whole episode. Every chosen episode is heard once before any repeats.",mode_resume:"Continue where it stopped",window_hint:"Put back within the box's resume window, a tag always continues where it was.",link_tag:"Link tag",save:"Save",linked_done:"Linked {name}",saved:"Saved",error:"Something went wrong: {error}",type_artist:"Artist",type_album:"Album",type_playlist:"Playlist",type_audiobook:"Audiobook",type_podcast:"Podcast",type_track:"Song",type_radio:"Radio",type_folder:"Folder",group_artist:"Artists",group_album:"Albums",group_playlist:"Playlists",group_audiobook:"Audiobooks",group_podcast:"Podcasts",group_track:"Songs",group_radio:"Radio",mode_random_album:"A random album each time",mode_random_album_hint:"For audiobook series where each album is one episode, such as Die drei ??? or Bamse. Plays one whole album, in order. Every chosen album is heard once before any repeats.",mode_next_album:"The next album each time",mode_next_album_hint:"Plays the chosen albums one after another, in episode-number order.",mode_next_episode:"The next episode each time",mode_next_episode_hint:"Plays the episodes one after another, in order.",series_hint:"Lifted halfway, the tag continues there when it comes back, however much later. It moves on only when the album has been heard to the end.",albums_title:"Albums to play",episodes_title:"Episodes to play",albums_count:"{n} of {total} chosen",albums_loading:"Loading the albums",albums_none:"No albums found. Until the list loads, the tag shuffles the artist.",select_all:"All",select_numbered:"Numbered episodes only",select_none:"None",series_progress:"{included} chosen \xB7 {heard} heard",listening:"Listening: {title}"};var ke={title:"Speldosa",boxes:"Speldosor",linked_tags:"Kopplade brickor",linked_hint:"En bricka spelar samma sak p\xE5 alla speldosor hemma",seen:"L\xE4sta, inte kopplade",seen_on:"Senast p\xE5 {box}, {when}",on_box_now:"Ligger p\xE5 {box} nu",new_tag_title:"En ny bricka ligger p\xE5 {box}",new_tag_text:"Bricka {tag} har ingen musik \xE4nnu. L\xE5t den ligga kvar och v\xE4lj vad den ska spela.",link_this:"Koppla brickan",link:"Koppla",forget:"Gl\xF6m",link_new:"Koppla en ny bricka",link_new_hint:"L\xE4gg det p\xE5 en speldosa f\xF6rst",no_tag_on_box:"Ingen ny bricka ligger p\xE5 en speldosa. L\xE4gg brickan p\xE5 en speldosa och v\xE4lj Koppla en ny bricka igen.",no_box:"Ingen speldosa \xE4r tillagd \xE4nnu. L\xE4gg till en under Inst\xE4llningar, Enheter och tj\xE4nster, L\xE4gg till integration, Speldosa.",no_tags:"Inga brickor \xE4r kopplade \xE4nnu.",change:"\xC4ndra",unlink:"Koppla bort",unlink_confirm:"Koppla bort {name}? Brickan finns kvar men spelar inget f\xF6rr\xE4n du kopplar den igen.",play_on:"Spela p\xE5 {player}",try_on:"Prova p\xE5 {player}",playing_on:"Spelar p\xE5 {player}",tag_on:"Bricka p\xE5: {state}",tag_none:"Ingen bricka p\xE5",tag_id:"Bricka {tag}",tag_on_named:"Bricka p\xE5: {name}",tag_on_unlinked:"Bricka p\xE5: inte kopplad",linked:"kopplat",not_linked:"inte kopplat",reader_ok:"L\xE4saren fungerar",reader_problem:"Problem med l\xE4saren: dra ur sladden en stund",offline:"Inte ansluten",plays_on:"spelar p\xE5 {player}",back:"Tillbaka",link_tag_title:"Koppla bricka {tag}",change_tag_title:"\xC4ndra {name}",search_label:"S\xF6k i Music Assistant",search_hint:"S\xF6ker i ditt Music Assistant-bibliotek och dess tj\xE4nster, till exempel Spotify",too_short:"Skriv minst 3 tecken",searching:"S\xF6ker",empty:"Inget kom tillbaka. Om du v\xE4ntade dig tr\xE4ffar kan Spotify vara upptaget: f\xF6rs\xF6k igen om en halv minut.",try_again:"F\xF6rs\xF6k igen",all:"Allt",best:"B\xE4sta tr\xE4ff",weaker:"Svagare tr\xE4ffar",weaker_hint:"Tr\xE4ffar som bara matchar n\xE5gra av orden",now_playing:"Spelas p\xE5 {player} nu",link_album:"Koppla albumet",link_song:"Koppla l\xE5ten",pick_first:"V\xE4lj vad brickan ska spela",current_content:"Spelar nu: {name}",name_label:"Namn i bricklistan",how_it_plays:"S\xE5 spelar brickan",mode_from_start:"Fr\xE5n b\xF6rjan",mode_shuffle:"I slumpvis ordning",mode_random_episode:"Ett slumpvis avsnitt varje g\xE5ng",mode_random_episode_hint:"Spelar ett helt avsnitt. Varje valt avsnitt h\xF6rs en g\xE5ng innan n\xE5got upprepas.",mode_resume:"Forts\xE4tt d\xE4r det slutade",window_hint:"L\xE4ggs brickan tillbaka inom speldosans tid f\xF6r att komma ih\xE5g forts\xE4tter den alltid d\xE4r den var.",link_tag:"Koppla brickan",save:"Spara",linked_done:"Kopplade {name}",saved:"Sparat",error:"N\xE5got gick fel: {error}",type_artist:"Artist",type_album:"Album",type_playlist:"Spellista",type_audiobook:"Ljudbok",type_podcast:"Podd",type_track:"L\xE5t",type_radio:"Radio",type_folder:"Mapp",group_artist:"Artister",group_album:"Album",group_playlist:"Spellistor",group_audiobook:"Ljudb\xF6cker",group_podcast:"Poddar",group_track:"L\xE5tar",group_radio:"Radio",mode_random_album:"Ett slumpvis album varje g\xE5ng",mode_random_album_hint:"F\xF6r ljudboksserier d\xE4r varje album \xE4r ett avsnitt, till exempel Die drei ??? eller Bamse. Spelar ett helt album i ordning. Varje valt album h\xF6rs en g\xE5ng innan n\xE5got upprepas.",mode_next_album:"N\xE4sta album varje g\xE5ng",mode_next_album_hint:"Spelar de valda albumen efter varandra, i avsnittsordning.",mode_next_episode:"N\xE4sta avsnitt varje g\xE5ng",mode_next_episode_hint:"Spelar avsnitten efter varandra, i ordning.",series_hint:"Lyfts brickan mitt i forts\xE4tter den d\xE4r n\xE4r den kommer tillbaka, hur l\xE4nge det \xE4n dr\xF6jer. Den g\xE5r vidare f\xF6rst n\xE4r albumet har h\xF6rts till slutet.",albums_title:"Album som ska spelas",episodes_title:"Avsnitt som ska spelas",albums_count:"{n} av {total} valda",albums_loading:"H\xE4mtar albumen",albums_none:"Inga album hittades. Tills listan finns blandar brickan artistens l\xE5tar.",select_all:"Alla",select_numbered:"Bara numrerade avsnitt",select_none:"Inga",series_progress:"{included} valda \xB7 {heard} h\xF6rda",listening:"Lyssnar p\xE5: {title}"};var Ve={en:ie,sv:ke};function Fe(a){return(a?.locale?.language||a?.language||"en").toLowerCase().startsWith("sv")?"sv":"en"}function we(a){let e=Ve[Fe(a)];return(t,s={})=>(e[t]??ie[t]??t).replace(/\{(\w+)\}/g,(n,r)=>r in s?String(s[r]):n)}function Se(a,e){let t=a?.locale?.language||a?.language||"en";try{return new Intl.DateTimeFormat(t,{dateStyle:"medium",timeStyle:"short"}).format(new Date(e*1e3))}catch{return new Date(e*1e3).toISOString().slice(0,16).replace("T"," ")}}var Ae=q`
  :host {
    display: block;
    min-height: 100vh;
    background: var(--primary-background-color, #fafafa);
    color: var(--primary-text-color, #212121);
    font-family: var(--ha-font-family-body, Roboto, system-ui, sans-serif);
    font-size: 14px;
    line-height: 20px;
  }
  .toolbar {
    height: var(--header-height, 56px);
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 8px 0 16px;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
    background: var(--app-header-background-color, var(--primary-background-color, #fafafa));
    color: var(--app-header-text-color, var(--primary-text-color, #212121));
    box-sizing: border-box;
  }
  .toolbar.narrow { padding-left: 0; }
  .toolbar h1 { margin: 0; font-size: 20px; font-weight: 400; flex: 1 1 auto; min-width: 0;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .toolbar .aside { color: var(--secondary-text-color, #727272); white-space: nowrap; }
  .content { padding: 16px; display: flex; flex-direction: column; gap: 16px; max-width: 1040px;
    box-sizing: border-box; margin: 0 auto; }
  .tag { display: block; background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1px solid var(--divider-color, #e0e0e0); border-radius: var(--ha-card-border-radius, 12px);
    color: var(--primary-text-color); }
  .tag-title { padding: 16px 16px 8px; font-size: 20px; line-height: 28px; display: flex;
    align-items: baseline; gap: 12px; flex-wrap: wrap; }
  .tag-title .hint, .secondary { color: var(--secondary-text-color, #727272); font-size: 14px; }
  .banner { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12); border-radius: 12px;
    padding: 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
  .banner .text { flex: 1 1 320px; min-width: 0; }
  .banner .text strong { display: block; font-size: 16px; font-weight: 500; }
  button, a.button { font: inherit; font-weight: 500; cursor: pointer; border-radius: 18px; height: 36px;
    padding: 0 16px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    text-decoration: none; box-sizing: border-box; }
  button.primary { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); border: 0; }
  button.text { background: transparent; color: var(--primary-color, #03a9f4); border: 0; padding: 0 12px; }
  button.outlined { background: transparent; color: var(--primary-color, #03a9f4);
    border: 1px solid var(--outline-color, var(--divider-color, #bdbdbd)); }
  button:disabled { opacity: 0.5; cursor: default; }
  button:focus-visible, input:focus-visible, .result:focus-visible {
    outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 2px; }
  .row { display: flex; align-items: center; gap: 16px; padding: 8px 16px; min-height: 56px;
    border-top: 1px solid var(--divider-color, #eee); flex-wrap: wrap; }
  .row .grow { flex: 1 1 200px; min-width: 0; }
  .chip { background: var(--secondary-background-color, #f5f5f5); border-radius: 8px; padding: 4px 10px; }
  .chip.warn { background: rgba(var(--rgb-warning-color, 255, 166, 0), 0.2); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px;
    padding: 8px 16px 16px; }
  .tile { border: 1px solid var(--divider-color, #e0e0e0); border-radius: 12px; overflow: hidden;
    display: flex; flex-direction: column; background: var(--card-background-color, #fff); }
  .tile .body { padding: 12px; }
  .tile .body .name { font-weight: 500; }
  .tile .actions { display: flex; flex-wrap: wrap; gap: 4px; padding: 0 8px 8px; }
  .cover { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; display: block;
    background: var(--secondary-background-color, #eceff1); }
  .cover.placeholder { display: flex; align-items: center; justify-content: center;
    color: var(--secondary-text-color); }
  .thumb { width: 48px; height: 48px; border-radius: 6px; object-fit: cover; flex: 0 0 auto;
    background: var(--secondary-background-color, #eceff1); }
  .thumb.round { border-radius: 50%; }
  .search { position: relative; display: flex; align-items: center; gap: 12px; height: 56px; padding: 0 12px;
    border: 1px solid var(--outline-color, #9e9e9e); border-radius: 4px;
    background: var(--card-background-color, #fff); }
  .search label, .field label { position: absolute; top: -9px; left: 10px; padding: 0 4px; font-size: 12px;
    background: var(--card-background-color, #fff); color: var(--primary-color, #03a9f4); }
  .search input, .field input { flex: 1 1 auto; border: 0; outline: none; font: inherit; font-size: 16px;
    background: transparent; color: var(--primary-text-color); min-width: 0; }
  .field { position: relative; display: flex; align-items: center; height: 56px; padding: 0 12px;
    border: 1px solid var(--outline-color, #9e9e9e); border-radius: 4px; }
  .field label { color: var(--secondary-text-color); }
  .filters { display: flex; gap: 8px; flex-wrap: wrap; }
  .filter { height: 32px; border-radius: 8px; padding: 0 12px; font-weight: 400;
    background: transparent; color: var(--primary-text-color); border: 1px solid var(--outline-color, #bdbdbd); }
  .filter[aria-pressed="true"] { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.16);
    border-color: transparent; font-weight: 500; }
  .split { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-start; }
  .split > .main { flex: 999 1 480px; min-width: 0; display: flex; flex-direction: column; gap: 16px; }
  .split > .side { flex: 1 1 300px; min-width: 0; position: sticky; top: 16px; }
  .results { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px;
    padding: 0 16px 16px; }
  .result { display: flex; flex-direction: column; gap: 6px; padding: 7px; text-align: left; height: auto;
    border-radius: 12px; border: 1px solid var(--divider-color, #e0e0e0); background: transparent;
    color: var(--primary-text-color); font-weight: 400; align-items: stretch; }
  .result[aria-pressed="true"] { border: 2px solid var(--primary-color, #03a9f4); padding: 6px;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08); }
  .result .cover { border-radius: 8px; }
  .result.line { flex-direction: row; align-items: center; gap: 12px; border: 0; border-radius: 8px; padding: 8px; }
  .result.line[aria-pressed="true"] { padding: 6px; }
  .side .tag { overflow: hidden; }
  .side .inner { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
  .side .hero { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; display: block;
    background: var(--secondary-background-color, #eceff1); }
  fieldset { border: 0; margin: 0; padding: 0; display: flex; flex-direction: column; }
  legend { font-weight: 500; padding: 0; margin-bottom: 4px; }
  .mode { display: flex; gap: 12px; align-items: flex-start; min-height: 40px; padding: 4px 0; cursor: pointer; }
  .mode input { width: 18px; height: 18px; margin: 1px 0 0; accent-color: var(--primary-color, #03a9f4); }
  .mode small { display: block; color: var(--secondary-text-color); }
  .episodes { gap: 8px; }
  .episodes legend { display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
  .episode-list { max-height: 320px; overflow-y: auto; border: 1px solid var(--divider-color, #e0e0e0);
    border-radius: 8px; padding: 4px 8px; }
  .episode { display: flex; gap: 10px; align-items: center; min-height: 36px; cursor: pointer; }
  .episode input { width: 18px; height: 18px; margin: 0; accent-color: var(--primary-color, #03a9f4); }
  .actions-end { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; }
  .message { padding: 16px; color: var(--secondary-text-color); }
  .toast { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
    background: var(--primary-text-color, #323232); color: var(--primary-background-color, #fff);
    padding: 12px 20px; border-radius: 8px; z-index: 10; max-width: calc(100% - 32px); }
  .error { color: var(--error-color, #db4437); }
  svg.icon { width: 24px; height: 24px; fill: currentColor; flex: 0 0 auto; }
  .tag-id {
    font-family: var(--code-font-family, monospace);
    font-size: 0.85em;
  }
`;var Je=600,Ee=3,Qe=["artist","playlist","album","audiobook","podcast"],I=new Set(["random_album","next_album","random_episode","next_episode"]),Ce=new Set(["artist","podcast"]),N={back:"M20 11H7.8l5.6-5.6L12 4l-8 8 8 8 1.4-1.4L7.8 13H20z",search:"M15.5 14h-.8l-.3-.3A6.5 6.5 0 1 0 14 15.5l.3.3v.8l5 5 1.5-1.5zm-6 0a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9z",music:"M15 6H3v2h12zm0 4H3v2h12zM3 16h8v-2H3zM17 6v8.18A3 3 0 1 0 19 17V8h3V6z",plus:"M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z"},U=a=>o`<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d=${a}></path></svg>`,M=class extends f{constructor(){super(),this._overview=null,this._view="tags",this._results=null,this._filter=null,this._query="",this._search=xe(e=>this._runSearch(e),Je),this._searchSeq=0}get _t(){return we(this.hass)}get _api(){return(!this.__api||this.__api.hass!==this.hass)&&(this.__api=new B(this.hass)),this.__api}connectedCallback(){super.connectedCallback(),this._subscribe()}disconnectedCallback(){super.disconnectedCallback(),this._search.cancel(),this._unsub?.then(e=>e()).catch(()=>{}),this._unsub=null}updated(e){e.has("hass")&&this.hass&&!this._overview&&!this._loading&&this._load(),e.has("hass")&&this.hass&&!this._unsub&&this.isConnected&&this._subscribe()}_subscribe(){!this.hass||this._unsub||(this._unsub=this._api.subscribe(()=>this._load()),this._unsub.catch(()=>this._unsub=null))}async _load(){this._loading=!0;try{this._overview=await this._api.overview()}catch(e){this._error=e?.message||String(e)}finally{this._loading=!1}}_box(e){let t=this._overview?.boxes||[];return t.find(s=>s.entry_id===e)||t[0]}_boxWithTag(e){return(this._overview?.boxes||[]).find(t=>t.tag===e)}_flash(e){this._toast=e,clearTimeout(this._toastTimer),this._toastTimer=setTimeout(()=>this._toast=null,3500)}async _call(e){try{return await e()}catch(t){this._flash(this._t("error",{error:t?.message||String(t)}));return}}_openLink(e,t=null){this._uid=e,this._editing=t,this._view="link",this._results=null,this._query="",this._filter=null,this._selected=null,this._name=t?.name||"",this._mode=t?.mode||null,this._confirmUnlink=!1,this._now=null,this._episodes=null,this._episodesLoading=!1,t&&Ce.has(t.media_type)&&(this._episodesLoading=!0,this._api.tag(e).then(i=>{i.episode_list?.length?(this._episodes=i.episode_list,this._episodesLoading=!1):this._loadEpisodes(t)}).catch(()=>this._episodesLoading=!1));let s=this._boxWithTag(e)||this._box();s&&this._api.nowPlaying(s.entry_id).then(i=>this._now=i).catch(()=>{})}_openNewTag(){let e=(this._overview?.boxes||[]).find(t=>t.tag&&!t.tag_linked);if(!e){this._flash(this._t("no_tag_on_box"));return}this._openLink(e.tag)}_back(){this._search.cancel(),this._view="tags",this._load()}_onQuery(e){if(this._query=e.target.value,this._query.trim().length<Ee){this._search.cancel(),this._results=null;return}this._search(this._query)}async _runSearch(e){let t=++this._searchSeq;this._searching=!0;let s=this._boxWithTag(this._uid)||this._box();try{let i=await this._api.search(e,s?.entry_id);t===this._searchSeq&&(this._results=i)}catch(i){t===this._searchSeq&&(this._results={error:i?.message||String(i)})}finally{t===this._searchSeq&&(this._searching=!1)}}_select(e){this._selected=e,this._mode=e.mode,this._editing||(this._name=""),this._episodes=null,Ce.has(e.media_type)&&this._loadEpisodes(e)}async _loadEpisodes(e){let t=this._boxWithTag(this._uid)||this._box();this._episodesLoading=!0;let s=e.uri;try{let i=await this._api.episodes(e,this._uid,t?.entry_id);(this._selected||this._editing)?.uri===s&&(this._episodes=i.episodes)}catch{this._episodes=[]}finally{this._episodesLoading=!1}}_setIncluded(e){this._episodes=this._episodes.map(t=>({...t,included:e(t)}))}_seriesEpisodes(e){return I.has(e)&&this._episodes?.length?this._episodes:void 0}async _link(){let e=this._selected;if(!e)return;let t=this._boxWithTag(this._uid)||this._box(),s=await this._call(()=>this._api.link({uid:this._uid,item:e,name:this._name.trim()||(this._editing?this._editing.name:e.name),mode:this._mode||e.mode,boxId:t?.entry_id,episodes:this._seriesEpisodes(this._mode||e.mode)}));s&&(this._flash(this._t("linked_done",{name:s.name})),this._back())}async _saveEdit(){let e={mode:this._mode};this._name.trim()&&(e.name=this._name.trim());let t=this._seriesEpisodes(this._mode);t&&(e.episodes=t.map(({uri:i,title:n,number:r,included:h})=>({uri:i,title:n,number:r,included:h}))),await this._call(()=>this._api.update(this._uid,e))&&(this._flash(this._t("saved")),this._back())}async _tryItem(e,t){let s=this._boxWithTag(this._uid)||this._box(),i=await this._call(()=>this._api.tryPlay(e,t,s?.entry_id));i&&this._flash(this._t("playing_on",{player:i.player_name}))}async _unlink(e){await this._call(()=>this._api.unlink(e)),this._back()}async _forget(e){await this._call(()=>this._api.forgetSeen(e)),this._load()}render(){return this.hass?o`
      ${this._view==="link"?this._renderLink():this._renderTags()}
      ${this._toast?o`<div class="toast" role="status">${this._toast}</div>`:d}
    `:d}_toolbar(e,{back:t=!1,aside:s=""}={}){let i=!t&&customElements.get("ha-menu-button")?o`<ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>`:d;return o`<div class="toolbar ${this.narrow?"narrow":""}">
      ${i}
      ${t?o`<button class="text" aria-label=${this._t("back")} @click=${this._back}>${U(N.back)}</button>`:d}
      <h1>${e}</h1>
      ${s?o`<span class="aside">${s}</span>`:d}
    </div>`}_cover(e,t="cover",s=!1){return e?o`<img class="${t} ${s?"round":""}" src=${e} alt="" loading="lazy" />`:o`<div class="${t} placeholder ${s?"round":""}">${U(N.music)}</div>`}_modeLabel(e){return this._t(`mode_${e}`)}_hint(e){let t=`mode_${e}_hint`,s=this._t(t);return s===t?"":s}_renderEpisodes(e){let t=this._t,s=e.media_type==="artist";if(this._episodesLoading&&!this._episodes)return o`<div class="secondary">${t("albums_loading")}…</div>`;let i=this._episodes||[];if(!i.length)return o`<div class="secondary">${t("albums_none")}</div>`;let n=i.filter(r=>r.included).length;return o`<fieldset class="episodes">
      <legend>${t(s?"albums_title":"episodes_title")}
        <span class="secondary">${t("albums_count",{n,total:i.length})}</span></legend>
      <div class="filters">
        <button class="filter" @click=${()=>this._setIncluded(()=>!0)}>${t("select_all")}</button>
        <button class="filter" @click=${()=>this._setIncluded(r=>r.number!=null)}>${t("select_numbered")}</button>
        <button class="filter" @click=${()=>this._setIncluded(()=>!1)}>${t("select_none")}</button>
      </div>
      <div class="episode-list">
        ${i.map((r,h)=>o`<label class="episode">
            <input type="checkbox" .checked=${r.included}
              @change=${l=>this._episodes=i.map((p,u)=>u===h?{...p,included:l.target.checked}:p)} />
            <span>${r.title}</span>
          </label>`)}
      </div>
    </fieldset>`}_renderTags(){let e=this._t,t=this._overview;if(!t)return o`${this._toolbar(e("title"))}
        <div class="message">${this._error?o`<span class="error">${e("error",{error:this._error})}</span>`:"\u2026"}</div>`;let s=t.boxes.filter(i=>i.tag&&!i.tag_linked);return o`
      ${this._toolbar(e("title"))}
      <div class="content">
        ${t.boxes.length===0?o`<div class="tag"><div class="message">${e("no_box")}</div></div>`:d}
        ${s.map(i=>o`<div class="banner">
            ${U(N.plus)}
            <div class="text">
              <strong>${e("new_tag_title",{box:i.name})}</strong>
              ${e("new_tag_text",{tag:i.tag})}
            </div>
            <button class="primary" @click=${()=>this._openLink(i.tag)}>${e("link_this")}</button>
          </div>`)}
        ${t.boxes.length?o`<section class="tag">
              <div class="tag-title">${e("boxes")}</div>
              ${t.boxes.map(i=>this._renderBox(i))}
            </section>`:d}
        <section class="tag">
          <div class="tag-title">${e("linked_tags")} <span class="hint">${e("linked_hint")}</span></div>
          ${t.tags.length===0?o`<div class="message">${e("no_tags")}</div>`:d}
          <div class="grid">
            ${t.tags.map(i=>this._renderTagTile(i))}
            <button class="tile outlined" style="height:auto;min-height:200px;flex-direction:column" @click=${this._openNewTag}>
              ${U(N.plus)}<span>${e("link_new")}</span><span class="secondary">${e("link_new_hint")}</span>
            </button>
          </div>
        </section>
        ${t.seen.length?o`<section class="tag">
              <div class="tag-title">${e("seen")}</div>
              ${t.seen.map(i=>o`<div class="row">
                  <span class="grow"><strong>${i.uid}</strong></span>
                  <span class="secondary grow">${this._boxWithTag(i.uid)?e("on_box_now",{box:this._boxWithTag(i.uid).name}):e("seen_on",{box:i.box||"",when:Se(this.hass,i.last_seen)})}</span>
                  <button class="text" @click=${()=>this._openLink(i.uid)}>${e("link")}</button>
                  <button class="text" @click=${()=>this._forget(i.uid)}>${e("forget")}</button>
                </div>`)}
            </section>`:d}
      </div>
    `}_renderBox(e){let t=this._t,s=e.tag?(this._overview?.tags||[]).find(n=>n.uid===e.tag):null,i=t("tag_none");return e.tag&&(i=s?t("tag_on_named",{name:s.name}):t("tag_on_unlinked")),o`<div class="row">
      <div class="grow">
        <div><strong>${e.name}</strong></div>
        <div class="secondary">${[e.area,t("plays_on",{player:e.player_name})].filter(Boolean).join(" \xB7 ")}</div>
        ${e.tag?o`<div class="secondary tag-id">${t("tag_id",{tag:e.tag})}</div>`:d}
      </div>
      ${e.available?o`<span class="chip">${i}</span>`:o`<span class="chip warn">${t("offline")}</span>`}
      ${e.reader_problem?o`<span class="chip warn">${t("reader_problem")}</span>`:o`<span class="chip">${t("reader_ok")}</span>`}
    </div>`}_renderTagTile(e){let t=this._t,s=this._box()?.player_name||"",i=[t(`type_${e.media_type}`),this._modeLabel(e.mode)];return I.has(e.mode)&&e.episodes&&i.push(t("series_progress",{included:e.included,heard:e.heard})),o`<div class="tile">
      ${this._cover(e.image)}
      <div class="body">
        <div class="name">${e.name}</div>
        <div class="secondary tag-id">${t("tag_id",{tag:e.uid})}</div>
        <div class="secondary">${i.join(" \xB7 ")}</div>
        ${e.current?o`<div class="secondary">${t("listening",{title:e.current})}</div>`:d}
      </div>
      <div class="actions">
        <button class="text" @click=${()=>this._tryItem(e,e.mode)}>${t("play_on",{player:s})}</button>
        <button class="text" @click=${()=>this._openLink(e.uid,e)}>${t("change")}</button>
      </div>
    </div>`}_renderLink(){let e=this._t,t=this._boxWithTag(this._uid),s=this._editing?e("change_tag_title",{name:this._editing.name}):e("link_tag_title",{tag:this._uid});return o`
      ${this._toolbar(s,{back:!0,aside:t?e("on_box_now",{box:t.name}):""})}
      <div class="content">
        <div class="split">
          <div class="main">
            <div class="search">
              <label for="q">${e("search_label")}</label>
              ${U(N.search)}
              <input id="q" type="search" autocomplete="off" .value=${this._query} @input=${this._onQuery} />
            </div>
            <div class="secondary">${e("search_hint")}</div>
            ${this._renderNowPlaying()}
            ${this._renderResults()}
          </div>
          <div class="side">${this._renderSide()}</div>
        </div>
      </div>
    `}_renderNowPlaying(){let e=this._now?.now;if(!e?.track)return d;let t=this._t;return o`<div class="tag row" style="border-top:0">
      ${this._cover(e.album?.image||e.track.image,"thumb")}
      <div class="grow">
        <div class="secondary">${t("now_playing",{player:this._now.player_name})}</div>
        <div><strong>${e.track.name}</strong>${e.track.subtitle?` \xB7 ${e.track.subtitle}`:""}</div>
      </div>
      ${e.album?o`<button class="text" @click=${()=>this._select(e.album)}>${t("link_album")}</button>`:d}
      <button class="text" @click=${()=>this._select(e.track)}>${t("link_song")}</button>
    </div>`}_renderResults(){let e=this._t,t=this._results;if(this._query.trim()&&this._query.trim().length<Ee)return o`<div class="secondary">${e("too_short")}</div>`;if(this._searching&&!t)return o`<div class="message">${e("searching")}…</div>`;if(!t)return d;if(t.error)return o`<div class="message error">${e("error",{error:t.error})}</div>`;if(t.empty)return o`<div class="tag message">${e("empty")}
        <div><button class="text" @click=${()=>this._runSearch(this._query)}>${e("try_again")}</button></div></div>`;let s=t.groups.filter(n=>!this._filter||n.media_type===this._filter),i=!this._filter||this._filter==="artist"?t.best:[];return o`
      <div class="filters" role="group">
        <button class="filter" aria-pressed=${String(!this._filter)} @click=${()=>this._filter=null}>${e("all")}</button>
        ${Qe.filter(n=>n==="artist"?t.best.length||t.groups.some(r=>r.media_type===n):t.groups.some(r=>r.media_type===n)).map(n=>o`<button class="filter" aria-pressed=${String(this._filter===n)} @click=${()=>this._filter=n}>${e(`group_${n}`)}</button>`)}
      </div>
      ${i.length?o`<section class="tag"><div class="tag-title" style="font-size:16px">${e("best")}</div>
            <div style="padding:0 8px 8px">${i.map(n=>this._renderLine(n,!0))}</div></section>`:d}
      ${s.map(n=>o`<section class="tag"><div class="tag-title" style="font-size:16px">${e(`group_${n.media_type}`)}</div>
          ${n.media_type==="artist"||n.media_type==="track"?o`<div style="padding:0 8px 8px">${n.items.map(r=>this._renderLine(r,n.media_type==="artist"))}</div>`:o`<div class="results">${n.items.map(r=>this._renderResult(r))}</div>`}
        </section>`)}
      ${!this._filter&&t.weaker.length?o`<section class="tag"><div class="tag-title" style="font-size:16px">${e("weaker")}
            <span class="hint">${e("weaker_hint")}</span></div>
            <div style="padding:0 8px 8px">${t.weaker.map(n=>this._renderLine(n))}</div></section>`:d}
    `}_isSelected(e){return this._selected?.uri===e.uri}_renderResult(e){return o`<button class="result" aria-pressed=${String(this._isSelected(e))} @click=${()=>this._select(e)}>
      ${this._cover(e.image)}
      <span>${e.name}</span>
      <span class="secondary">${[this._t(`type_${e.media_type}`),e.subtitle].filter(Boolean).join(" \xB7 ")}</span>
    </button>`}_renderLine(e,t=!1){return o`<button class="result line" aria-pressed=${String(this._isSelected(e))} @click=${()=>this._select(e)}>
      ${this._cover(e.image,"thumb",t)}
      <span><span style="display:block">${e.name}</span>
        <span class="secondary">${[this._t(`type_${e.media_type}`),e.subtitle].filter(Boolean).join(" \xB7 ")}</span></span>
    </button>`}_renderSide(){let e=this._t,t=this._selected,s=this._editing;if(!t&&!s)return o`<div class="tag"><div class="message">${e("pick_first")}</div></div>`;let i=t||s,n=i.modes||[],r=this._mode||i.mode,h=(this._boxWithTag(this._uid)||this._box())?.player_name||"";return o`<div class="tag">
      ${i.image?o`<img class="hero" src=${i.image} alt="" />`:d}
      <div class="inner">
        <div>
          <div style="font-size:20px;line-height:28px">${i.name}</div>
          <div class="secondary">${[e(`type_${i.media_type}`),i.subtitle].filter(Boolean).join(" \xB7 ")}</div>
          ${s&&t?o`<div class="secondary">${e("current_content",{name:s.name})}</div>`:d}
        </div>
        <div class="field">
          <label for="name">${e("name_label")}</label>
          <input id="name" type="text" .value=${this._name} placeholder=${s?.name||t?.name||""}
            @input=${l=>this._name=l.target.value} />
        </div>
        <fieldset>
          <legend>${e("how_it_plays")}</legend>
          ${n.map(l=>o`<label class="mode">
              <input type="radio" name="mode" .checked=${l===r} @change=${()=>this._mode=l} />
              <span>${this._modeLabel(l)}${this._hint(l)?o`<small>${this._hint(l)}</small>`:d}</span>
            </label>`)}
          <small class="secondary">${I.has(r)?e("series_hint"):e("window_hint")}</small>
        </fieldset>
        ${I.has(r)?this._renderEpisodes(i):d}
        <div class="actions-end">
          ${s&&!t?o`${this._confirmUnlink?o`<span class="secondary">${e("unlink_confirm",{name:s.name})}</span>
                      <button class="text" @click=${()=>this._unlink(s.uid)}>${e("unlink")}</button>`:o`<button class="text" @click=${()=>this._confirmUnlink=!0}>${e("unlink")}</button>`}
                <button class="primary" @click=${this._saveEdit}>${e("save")}</button>`:o`<button class="text" @click=${()=>this._tryItem(t,r)}>${e("try_on",{player:h})}</button>
                <button class="primary" @click=${this._link}>${e("link_tag")}</button>`}
        </div>
      </div>
    </div>`}};W(M,"properties",{hass:{attribute:!1},narrow:{type:Boolean},route:{attribute:!1},panel:{attribute:!1},_overview:{state:!0},_view:{state:!0},_uid:{state:!0},_editing:{state:!0},_query:{state:!0},_results:{state:!0},_searching:{state:!0},_filter:{state:!0},_selected:{state:!0},_mode:{state:!0},_name:{state:!0},_now:{state:!0},_confirmUnlink:{state:!0},_episodes:{state:!0},_episodesLoading:{state:!0},_toast:{state:!0},_error:{state:!0}}),W(M,"styles",Ae);customElements.get("speldosa-panel")||customElements.define("speldosa-panel",M);export{M as SpeldosaPanel};
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
