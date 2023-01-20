import { isVue2, install, Vue2 } from 'vue-demi';
import { PiniaVuePlugin, createPinia, setActivePinia } from 'pinia';

if (isVue2) {
  install();
  const Vue = "default" in Vue2 ? Vue2.default : Vue2;
  Vue.use(PiniaVuePlugin);
}
const PiniaNuxtPlugin = (context, inject) => {
  const pinia = createPinia();
  if (isVue2) {
    context.app.pinia = pinia;
  } else {
    context.vueApp.use(pinia);
  }
  inject("pinia", pinia);
  context.pinia = pinia;
  setActivePinia(pinia);
  pinia._p.push(({ store }) => {
    Object.defineProperty(store, "$nuxt", { value: context });
  });
  if (process.server) {
    if (isVue2) {
      context.beforeNuxtRender(({ nuxtState }) => {
        nuxtState.pinia = pinia.state.value;
      });
    } else {
      context.nuxtState.pinia = pinia.state.value;
    }
  } else if (context.nuxtState && context.nuxtState.pinia) {
    pinia.state.value = context.nuxtState.pinia;
  }
};

export { PiniaNuxtPlugin as default };
