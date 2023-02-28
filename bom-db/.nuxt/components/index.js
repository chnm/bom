export { default as App } from '../../components/App.vue'
export { default as AppAccordion } from '../../components/AppAccordion.vue'
export { default as ChristeningsDataTable } from '../../components/ChristeningsDataTable.vue'
export { default as DeathCausesTable } from '../../components/DeathCausesTable.vue'
export { default as FoodstuffsDataTable } from '../../components/FoodstuffsDataTable.vue'
export { default as Footer } from '../../components/Footer.vue'
export { default as GeneralBillsTable } from '../../components/GeneralBillsTable.vue'
export { default as Modal } from '../../components/Modal.vue'
export { default as NavBar } from '../../components/NavBar.vue'
export { default as ViewMore } from '../../components/ViewMore.vue'
export { default as WeeklyBillsTable } from '../../components/WeeklyBillsTable.vue'
export { default as TablesSelectCountType } from '../../components/tables/SelectCountType.vue'

// nuxt/nuxt.js#8607
function wrapFunctional(options) {
  if (!options || !options.functional) {
    return options
  }

  const propKeys = Array.isArray(options.props) ? options.props : Object.keys(options.props || {})

  return {
    render(h) {
      const attrs = {}
      const props = {}

      for (const key in this.$attrs) {
        if (propKeys.includes(key)) {
          props[key] = this.$attrs[key]
        } else {
          attrs[key] = this.$attrs[key]
        }
      }

      return h(options, {
        on: this.$listeners,
        attrs,
        props,
        scopedSlots: this.$scopedSlots,
      }, this.$slots.default)
    }
  }
}
