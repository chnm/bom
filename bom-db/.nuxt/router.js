import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _699a41ac = () => interopDefault(import('../pages/About.vue' /* webpackChunkName: "pages/About" */))
const _315ebdc6 = () => interopDefault(import('../pages/Data.vue' /* webpackChunkName: "pages/Data" */))
const _19396250 = () => interopDefault(import('../pages/Team.vue' /* webpackChunkName: "pages/Team" */))
const _75275dfc = () => interopDefault(import('../pages/Visualizations.vue' /* webpackChunkName: "pages/Visualizations" */))
const _38674a28 = () => interopDefault(import('../pages/WeeklyBills.vue' /* webpackChunkName: "pages/WeeklyBills" */))
const _1f2162b2 = () => interopDefault(import('../pages/visualizations/causes.vue' /* webpackChunkName: "pages/visualizations/causes" */))
const _3940caaf = () => interopDefault(import('../pages/visualizations/plague.vue' /* webpackChunkName: "pages/visualizations/plague" */))
const _73789a0f = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))

const emptyFn = () => {}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: '/',
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/About",
    component: _699a41ac,
    name: "About"
  }, {
    path: "/Data",
    component: _315ebdc6,
    name: "Data"
  }, {
    path: "/Team",
    component: _19396250,
    name: "Team"
  }, {
    path: "/Visualizations",
    component: _75275dfc,
    name: "Visualizations"
  }, {
    path: "/WeeklyBills",
    component: _38674a28,
    name: "WeeklyBills"
  }, {
    path: "/visualizations/causes",
    component: _1f2162b2,
    name: "visualizations-causes"
  }, {
    path: "/visualizations/plague",
    component: _3940caaf,
    name: "visualizations-plague"
  }, {
    path: "/",
    component: _73789a0f,
    name: "index"
  }],

  fallback: false
}

export function createRouter (ssrContext, config) {
  const base = (config._app && config._app.basePath) || routerOptions.base
  const router = new Router({ ...routerOptions, base  })

  // TODO: remove in Nuxt 3
  const originalPush = router.push
  router.push = function push (location, onComplete = emptyFn, onAbort) {
    return originalPush.call(this, location, onComplete, onAbort)
  }

  const resolve = router.resolve.bind(router)
  router.resolve = (to, current, append) => {
    if (typeof to === 'string') {
      to = normalizeURL(to)
    }
    return resolve(to, current, append)
  }

  return router
}
