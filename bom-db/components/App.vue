<template>
  <div class="flex flex-wrap">
    <div class="w-full px-12 py-8">
      <ul class="flex mb-0 list-none flex-wrap pt-3 pb-4 flex-row">
        <li class="-mb-px mr-2 last:mr-0 flex-auto text-center">
          <a
            class="text-xs font-bold uppercase px-5 py-3 rounded block leading-normal border-solid border-2 border-dbn-yellow"
            :class="{
              'text-black bg-white': openTab !== 1,
              'text-white bg-dbn-yellow': openTab === 1,
            }"
            @click="toggleTabs(1)"
          >
            Weekly Bills
          </a>
        </li>
        <li class="-mb-px mr-2 last:mr-0 flex-auto text-center">
          <a
            class="text-xs font-bold uppercase px-5 py-3 rounded block leading-normal border-solid border-2 border-dbn-yellow"
            :class="{
              'text-black bg-white': openTab !== 2,
              'text-white bg-dbn-yellow': openTab === 2,
            }"
            @click="toggleTabs(2)"
          >
            General Bills
          </a>
        </li>
        <li class="-mb-px mr-2 last:mr-0 flex-auto text-center">
          <a
            class="text-xs font-bold uppercase px-5 py-3 rounded block leading-normal border-solid border-2 border-dbn-yellow"
            :class="{
              'text-black bg-white': openTab !== 3,
              'text-white bg-dbn-yellow': openTab === 3,
            }"
            @click="toggleTabs(3)"
          >
            Total Deaths
          </a>
        </li>
        <li class="-mb-px mr-2 last:mr-0 flex-auto text-center">
          <a
            class="text-xs font-bold uppercase px-5 py-3 rounded block leading-normal border-solid border-2 border-dbn-yellow"
            :class="{
              'text-black bg-white': openTab !== 4,
              'text-white bg-dbn-yellow': openTab === 4,
            }"
            @click="toggleTabs(4)"
          >
            Christenings
          </a>
        </li>
      </ul>
      <div :class="{ hidden: openTab !== 1, block: openTab === 1 }">
        <WeeklyBillsTable />
      </div>
      <div :class="{ hidden: openTab !== 2, block: openTab === 2 }">
        <div>
          <GeneralBillsTable />
        </div>
      </div>
      <div :class="{ hidden: openTab !== 3, block: openTab === 3 }">
        <div>
          <DeathCausesTable />
        </div>
      </div>
      <div :class="{ hidden: openTab !== 4, block: openTab === 4 }">
        <div>
          <ChristeningsDataTable />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import WeeklyBillsTable from "./WeeklyBillsTable.vue";
import GeneralBillsTable from "./GeneralBillsTable.vue";
import ChristeningsDataTable from "./ChristeningsDataTable.vue";
import DeathCausesTable from "./DeathCausesTable.vue";

export default {
  name: "BoM",
  components: {
    WeeklyBillsTable,
    GeneralBillsTable,
    ChristeningsDataTable,
    DeathCausesTable,
  },
  data() {
    return {
      checked: false,
      showModal: false,
      // Always show vue-slider tooltips
      dotOptions: [
        {
          tooltip: "always",
        },
        {
          tooltip: "always",
        },
      ],
      errors: [],
      countType: ["All", "Buried", "Plague"],
      countTypeGeneral: ["All", "Total"],
      filteredCountType: "All",
      filteredBillsData: [],
      totalParishes: [],
      parishNames: [],
      totalGeneralBills: [],
      totalRecords: 100000,
      filteredYears: [1640, 1754],
      openTab: 1,
      serverParams: {
        limit: 50,
        offset: 0,
        perPage: 25,
        page: 1,
      },
    };
  },
  methods: {
    // TODO: testing -- delete before prod
    log(item) {
      // eslint-disable-next-line no-console
      console.log(item);
    },
    toggleTabs(tabNum) {
      this.openTab = tabNum;
    },
    // applyUpdate is called when the user clicks the "Update" button and returns the vmodel
    // data in filteredData() to the table.
    applyFilters() {
      // eslint-disable-next-line no-console
      console.log("applied");
    },
    // this function resets any filters that have been applied to their default values.
    resetFilters() {
      this.$emit(
        "reset-filters",
        (this.filteredCountType = "All"),
        (this.filteredBillsData = []),
        (this.filteredYears = [1640, 1754])
      );
    },
  },
};
</script>

<style scoped>
/** https://loading.io/css/ */
.lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}
.lds-ellipsis div {
  position: absolute;
  top: 27px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #ddd;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.lds-ellipsis div:nth-child(1) {
  left: 6px;
  animation: lds-ellipsis1 0.6s infinite;
}
.lds-ellipsis div:nth-child(2) {
  left: 6px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(3) {
  left: 26px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(4) {
  left: 45px;
  animation: lds-ellipsis3 0.6s infinite;
}
@keyframes lds-ellipsis1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes lds-ellipsis3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}
@keyframes lds-ellipsis2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(19px, 0);
  }
}
</style>
