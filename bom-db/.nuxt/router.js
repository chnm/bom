import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _1460bb4e = () => interopDefault(import('../pages/About.vue' /* webpackChunkName: "pages/About" */))
const _43873c0e = () => interopDefault(import('../pages/Data.vue' /* webpackChunkName: "pages/Data" */))
const _756ffd41 = () => interopDefault(import('../pages/Team.vue' /* webpackChunkName: "pages/Team" */))
const _d6129a9a = () => interopDefault(import('../pages/Visualizations.vue' /* webpackChunkName: "pages/Visualizations" */))
const _136aae17 = () => interopDefault(import('../pages/WeeklyBills.vue' /* webpackChunkName: "pages/WeeklyBills" */))
const _d3545854 = () => interopDefault(import('../pages/visualizations/causes.vue' /* webpackChunkName: "pages/visualizations/causes" */))
const _41b16044 = () => interopDefault(import('../pages/visualizations/plague.vue' /* webpackChunkName: "pages/visualizations/plague" */))
const _c3d54584 = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))

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
    component: _1460bb4e,
    name: "About"
  }, {
    path: "/Data",
    component: _43873c0e,
    name: "Data"
  }, {
    path: "/Team",
    component: _756ffd41,
    name: "Team"
  }, {
    path: "/Visualizations",
    component: _d6129a9a,
    name: "Visualizations"
  }, {
    path: "/WeeklyBills",
    component: _136aae17,
    name: "WeeklyBills"
  }, {
    path: "/visualizations/causes",
    component: _d3545854,
    name: "visualizations-causes"
  }, {
    path: "/visualizations/plague",
    component: _41b16044,
    name: "visualizations-plague"
  }, {
    path: "/",
    component: _c3d54584,
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
