import { defineStore } from 'pinia';

export const filterSelections = defineStore('filterOptions', {
    state: () => ({
        /** @type {{ text: string, id: number }} 
         * @description The selected parishes to filter. The default is all parishes are available.
        */
        billsFilters: [],
        /** @type { 'All' | 'Burial' | 'Plague' | 'Total' } 
         * @description The selected count type to filter. The default is to show all.
        */
        countType: 'All',
        /** @type { [startYear, endYear] } 
         * @description The selected years to filter. The default is the entire range of years.
        */
        yearRange: [ 1640, 1754],
    }),
    getters: {
        getBillsFilters: state => state.billsFilters,
        getYearRange: state => state.yearRange,
        getCountType: state => state.countType,        
    },
    actions: {
        addParishes(parish) {
            this.billsFilters.push(parish);
        },
        removeParishes(parish) {
            this.billsFilters.splice(this.billsFilters.indexOf(parish), 1);
        },
        updateYearRangeArray(startYear, endYear) {
            this.yearRange = [startYear, endYear];
        },
        updateCountType(countType) {
            this.countType = countType;
        },
    },
})