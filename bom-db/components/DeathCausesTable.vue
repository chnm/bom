<template>
  <div class="bg-white">
    <!-- start of filters -->
    <div id="filters" class="accordion">
      <app-accordion
        class="mb-4 pt-6 pb-6 ml-4 mr-4"
      >
        <template #title>
          <span class="font-semibold text-base">Filter by</span>
        </template>
        <template #content>
          <div class="grid grid-cols-4 gap-4 pb-6">
            <!-- parishes -->
            <app-accordion class="pb-6 ml-4 mr-4 border-slate-200">
              <template #title>
                <span class="font-semibold text-base">Causes of death</span>
              </template>
              <template #content>
                <div
                  class="accordion-body py-4 px-5 max-h-64 overflow-scroll border border-slate-200"
                >
                  <div id="search-wrapper" class="py-3">
                    <input
                      v-model="search"
                      class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      type="text"
                      placeholder="Search parishes"
                    />
                  </div>
                  <ul
                    class="dropdown-menu"
                    aria-labelledby="parish-selection-menu"
                  >
                  <li
                            v-for="(cause, index) in filterCausesList"
                            :key="index"
                          >
                            <input
                              :id="'cause-' + index"
                              v-model="filteredCauseIDs"
                              :value="cause.name"
                              name="causes"
                              type="checkbox"
                              class="dropdown-item"
                            />
                            <label :for="cause.name"
                              ><span>{{ cause.name }}</span></label
                            >
                          </li>
                  </ul>
                </div>
              </template>
            </app-accordion>
            <!-- year range -->
            <div>
              <div class="accordion-body py-4 px-5">
                <div class="font-semibold text-base">Year Range</div>
                <div class="slider-container mt-4">
                  <vue-slider
                    v-model="filteredYears"
                    :min="1636"
                    :max="1754"
                    :interval="1"
                    :enable-cross="false"
                    :lazy="true"
                    :dot-options="dotOptions"
                    @change="updateFilteredYearsArray"
                  />
                </div>
              </div>
            </div>
            <!-- count type -->
            <div>
              <!--spacer-->
            </div>
            <!-- buttons -->
            <div class="overflow-y-auto h-48 px-4 py-4">
              <button
                class="text-xs font-bold uppercase px-5 py-3 m-0.5 w-40 rounded block leading-normal border-solid border-2 border-dbn-yellow text-white bg-dbn-yellow hover:bg-dbn-yellowdark"
                @click="resetFilters"
              >
                Reset Filters
              </button>

              <button
                class="text-xs font-bold uppercase px-5 py-3 m-0.5 w-40 rounded block leading-normal border-solid border-2 border-dbn-yellow text-white bg-dbn-yellow hover:bg-dbn-yellowdark"
                @click="applyFilters()"
              >
                Apply Filters
              </button>

              <div
                  class="text-xs font-bold uppercase px-1 py-3 m-0.5 leading-normal text-black hover:underline"
                  @click="($event) => showInstructionsModal()"
                >
                  How to use this table
                </div>
            </div>
          </div>
        </template>
      </app-accordion>
    </div>
    <!-- end of filter -->
    <vue-good-table
      mode="remote"
      :columns="columns"
      :rows="totalDeaths"
      :total-rows="totalRecords"
      max-height="600px"
      :pagination-options="{
        enabled: true,
        position: 'bottom',
        perPageDropdown: [25, 50, 100],
        dropdownAllowAll: false,
        firstLabel: 'First page',
        lastLable: 'Last page',
        nextLabel: 'Next page',
        previousLabel: 'Previous page',
        rowsPerPageLabel: 'Causes per page',
      }"
      :sort-options="{ enabled: false }"
      :search-options="{ enabled: false }"
      style-class="vgt-table condensed striped"
      @on-page-change="onPageChange"
      @on-row-click="onRowClick"
      @on-per-page-change="onPerPageChange"
    >
      <template slot="table-column" slot-scope="props">
        <span v-if="props.column.label == 'Cause'">
          <span class="hint--right z-50" aria-label="The cause of death.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Count'">
          <span class="hint--bottom z-50" aria-label="The total cause of death.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Week Number'">
          <span class="hint--bottom z-50" aria-label="The week number in the year.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Year'">
          <span class="hint--left z-50" aria-label="The year for the data.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else>
          {{ props.column.label }}
        </span>
      </template>
    </vue-good-table>
    <Modal v-show="isModalVisible" :params="params" @close="closeModal">
      <template v-if="params.row" #header>
        <h3 class="text-xl font-bold">
          <!-- show the params -->
          {{ params.row.death }}
        </h3>
      </template>
      <template v-if="params.row" #body>
        <div v-if="params.row.descriptive_text">
          This cause of death is described as: "{{ params.row.descriptive_text }}"
        </div>
        <!-- if params.row.descriptive_text is an empty string, display a different message-->
        <div v-else>
          This cause of death is not described.
        </div>
      </template>
      <template v-if="params.row" #footer>
        This is a new modal footer.
      </template>
    </Modal>
    <!-- instructions -->
    <div
      v-if="showInstructions"
      class="fixed top-0 left-0 w-full h-full bg-gray-900 bg-opacity-50 z-50"
    >
      <div
        class="relative z-10"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        ></div>
        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div
            class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"
          >
            <div
              class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
            >
              <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div class="sm:flex sm:items-start">
                  <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3
                      id="modal-title"
                      class="text-base font-semibold leading-6 text-gray-900"
                    >
                      How to use this table
                    </h3>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500 pb-3">
                        The filter is divided into two areas: causes of death and years. 
                        You can select one or more options from each area.
                        The causes of death can be searched by typing in the search box.
                      </p>
                      <p class="text-sm text-gray-500 pb-3">
                        Once you've made adjustments to the filters, click "Apply Filters"
                        to update the table. Click "Reset Filters" to reset the table to its 
                        default state.
                      </p>
                      <p class="text-sm text-gray-500 pb-3">
                        You can click on an individual row to view additional information.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div
                class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6"
              >
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md bg-dbn-red px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                  aria-label="Close instructions"
                  @click="close"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import VueSlider from "vue-slider-component";
import "vue-slider-component/theme/antd.css";
import Modal from "@/components/Modal.vue";
import AppAccordion from "@/components/AppAccordion.vue";

export default {
  name: "DeathCausesTable",
  components: {
    VueSlider,
    Modal,
    AppAccordion,
  },
  data() {
    return {
      search: "",
      params: {},
      totalDeaths: [],
      causesList: [],
      totalRecords: 0,
      errors: [],
      isModalVisible: false,
      showInstructions: false,
      columns: [
        {
          label: "Cause",
          field: "death",
        },
        {
          label: "Count",
          field: "count",
          type: "number",
        },
        {
          label: "Week Number",
          field: "week_no",
          type: "number",
        },
        {
          label: "Year",
          field: "year",
          type: "date",
          dateInputFormat: "yyyy",
          dateOutputFormat: "yyyy",
        },
      ],
      // Always show vue-slider tooltips
      dotOptions: [
        {
          tooltip: "always",
        },
        {
          tooltip: "always",
        },
      ],
      filteredYears: [1636, 1754],
      filteredCauseIDs: [],
      serverParams: {
        limit: 25,
        offset: 0,
        causes: "",
        year: [1636, 1754],
        perPage: 25,
        page: 1,
      },
    };
  },
  computed: {
    filterCausesList() {
      return this.causesList.filter((cause) => {
        return cause.name.toLowerCase().includes(this.search.toLowerCase());
      });
    },
  },
  mounted() {
    axios
      .get(
        "https://data.chnm.org/bom/causes?start-year=" +
          this.serverParams.year[0] +
          "&end-year=" +
          this.serverParams.year[1] +
          "&id=" +
          this.serverParams.causes +
          "&limit=" +
          this.serverParams.limit +
          "&offset=" +
          this.serverParams.offset
      )
      .then((response) => {
        this.totalDeaths = response.data;
        this.getTotalRecords();
      })
      .catch((e) => {
        this.errors.push(e);
        // eslint-disable-next-line no-console
        console.log(this.errors);
      });
    axios
      .get("https://data.chnm.org/bom/list-deaths")
      .then((response) => {
        this.causesList = response.data;
      })
      .catch((e) => {
        this.errors.push(e);
        // eslint-disable-next-line no-console
        console.log(this.errors);
      });
  },
  methods: {
    getTotalRecords() {
      // the total records are the in the totalrecords property of the first item in the array
      this.totalRecords = this.totalDeaths[0].totalrecords;
    },
    showModal(params) {
      this.params = params;
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
    },
    onRowClick(params) {
      this.showModal(params);
    },
    updateParams(newProps) {
      this.serverParams = Object.assign({}, this.serverParams, newProps);
    },

    onPageChange(params) {
      this.updateParams({
        page: params.currentPage,
        offset: (params.currentPage - 1) * params.currentPerPage,
      });
      this.loadItems();
    },

    onPerPageChange(params) {
      this.updateParams({ perPage: params.currentPerPage });
      this.loadItems();
    },

    // display instructions
    showInstructionsModal() {
      this.showInstructions = true;
    },

    // close instructions
    close() {
      this.showInstructions = false;
    },

    loadItems() {
      return axios
        .get(
          "https://data.chnm.org/bom/causes?start-year=" +
            this.filteredYears[0] +
            "&end-year=" +
            this.filteredYears[1] +
            "&id=" +
            this.serverParams.causes +
            "&limit=" +
            this.serverParams.limit +
            "&offset=" +
            this.serverParams.offset
        )
        .then((response) => {
          this.totalDeaths = response.data;
          this.getTotalRecords();
        })
        .catch((e) => {
          this.errors.push(e);
          // eslint-disable-next-line no-console
          console.log(this.errors);
        });
    },
    // When a user adjusts the year range sliders, those years are added to the
    // filteredYears array. That array then updates the serverParams.year array and submits
    // a new request to the server.
    updateFilteredYearsArray(newYears) {
      this.filteredYears = newYears;
      // eslint-disable-next-line no-console
      this.updateParams({
        year: newYears,
      });
    },
    // When the user clicks the Apply Filters button, we use the
    // v-model data in filteredParishIDs, filteredYears, and
    // filteredCountType to update the serverParams.parishes, serverParams.year, and
    // serverParams.count_type arrays. Then we submit a new request to the server.
    applyFilters() {
      this.updateParams({
        causes: this.filteredCauseIDs,
        year: this.filteredYears,
      });
      this.loadItems();
    },

    // When a user clicks the Reset Filters button, we return the data to their defaults.
    resetFilters() {
      this.filteredCauseIDs = [];
      this.filteredYears = [1636, 1754];
      this.search = "";
      this.updateParams({
        causes: [],
        year: [1636, 1754],
      });
      this.loadItems();
    },
  },
};
</script>
