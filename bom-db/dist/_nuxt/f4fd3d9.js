(window.webpackJsonp=window.webpackJsonp||[]).push([[10],{390:function(t,o,e){var content=e(478);content.__esModule&&(content=content.default),"string"==typeof content&&(content=[[t.i,content,""]]),content.locals&&(t.exports=content.locals);(0,e(76).default)("107fcf72",content,!0,{sourceMap:!1})},477:function(t,o,e){"use strict";e(390)},478:function(t,o,e){var d=e(74)((function(i){return i[1]}));d.push([t.i,".modal[data-v-60b3ff05]{overflow-x:hidden;overflow-y:auto;z-index:9}.modal[data-v-60b3ff05],.modal__backdrop[data-v-60b3ff05]{position:fixed;top:0;right:0;bottom:0;left:0}.modal__backdrop[data-v-60b3ff05]{background-color:rgba(0,0,0,.3);z-index:1}.modal__dialog[data-v-60b3ff05]{background-color:#fff;position:relative;width:600px;margin:50px auto;display:flex;flex-direction:column;border-radius:5px;z-index:2}@media screen and (max-width:992px){.modal__dialog[data-v-60b3ff05]{width:90%}}.modal__close[data-v-60b3ff05]{width:30px;height:30px}.modal__header[data-v-60b3ff05]{padding:20px 20px 10px;display:flex;align-items:flex-start;justify-content:space-between}.modal__body[data-v-60b3ff05]{padding:10px 20px;overflow:auto;display:flex;flex-direction:column;align-items:stretch}.modal__footer[data-v-60b3ff05]{padding:10px 20px 20px}.fade-enter-active[data-v-60b3ff05],.fade-leave-active[data-v-60b3ff05]{transition:opacity .2s}.fade-enter[data-v-60b3ff05],.fade-leave-to[data-v-60b3ff05]{opacity:0}",""]),d.locals={},t.exports=d},492:function(t,o,e){"use strict";e.r(o);var d={name:"Modal",data:function(){return{show:!1}},methods:{closeModal:function(){this.show=!1,document.querySelector("body").classList.remove("overflow-hidden")},openModal:function(){this.show=!0,document.querySelector("body").classList.add("overflow-hidden")}}},l=(e(477),e(60)),component=Object(l.a)(d,(function(){var t=this,o=t.$createElement,e=t._self._c||o;return e("transition",{attrs:{name:"fade"}},[t.show?e("div",{staticClass:"modal"},[e("div",{staticClass:"modal__backdrop",on:{click:function(o){return t.closeModal()}}}),t._v(" "),e("div",{staticClass:"modal__dialog"},[e("div",{staticClass:"modal__header"},[t._t("header"),t._v(" "),e("button",{staticClass:"modal__close",attrs:{type:"button"},on:{click:function(o){return t.closeModal()}}},[e("svg",{attrs:{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 352 512"}},[e("path",{attrs:{fill:"currentColor",d:"M242.72 256l100.07-100.07c12.28-12.28 12.28-32.19 0-44.48l-22.24-22.24c-12.28-12.28-32.19-12.28-44.48 0L176 189.28 75.93 89.21c-12.28-12.28-32.19-12.28-44.48 0L9.21 111.45c-12.28 12.28-12.28 32.19 0 44.48L109.28 256 9.21 356.07c-12.28 12.28-12.28 32.19 0 44.48l22.24 22.24c12.28 12.28 32.2 12.28 44.48 0L176 322.72l100.07 100.07c12.28 12.28 32.2 12.28 44.48 0l22.24-22.24c12.28-12.28 12.28-32.19 0-44.48L242.72 256z"}})])])],2),t._v(" "),e("div",{staticClass:"modal__body"},[t._t("body")],2),t._v(" "),e("div",{staticClass:"modal__footer"},[t._t("footer")],2)])]):t._e()])}),[],!1,null,"60b3ff05",null);o.default=component.exports}}]);