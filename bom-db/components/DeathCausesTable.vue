<template>
  <div>
    <!-- start of filters -->
    <div id="filters" class="accordion">
      <div class="filter-item bg-white border border-gray-200 rounded-none">
        <h2 id="headingOne" class="accordion-header mb-0">
          <button
            class="accordion-button relative flex items-center w-full py-4 px-5 text-base text-dbn-purple text-left bg-white border-0 rounded-none transition focus:outline-none"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapseOne"
            aria-expanded="true"
            aria-controls="collapseOne"
          >
            Filter By
          </button>
        </h2>
        <div
          id="collapseOne"
          class="accordion-collapse collapse show"
          aria-labelledby="headingOne"
          data-bs-parent="#accordionFilters"
        >
          <div class="accordion-body py-4 px-5">
            <div class="grid grid-cols-4 gap-4 pb-6">
              <div class="overflow-y-auto h-48 px-4 py-4">
                <div
                  id="accordionParishes"
                  class="accordion accordion-flush border-2 border-slate-300"
                >
                  <div class="accordion-item rounded-none">
                    <h2 id="parish-headingOne" class="accordion-header mb-0">
                      <button
                        class="accordion-button collapsed relative flex items-center w-full py-4 px-5 text-base text-gray-800 text-left bg-white border-0 rounded-none transition focus:outline-none"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#flush-collapseOne"
                        aria-expanded="false"
                        aria-controls="flush-collapseOne"
                      >
                        Causes of Death
                      </button>
                    </h2>
                    <div
                      id="flush-collapseOne"
                      class="accordion-collapse border-0 collapse show"
                      aria-labelledby="flush-headingOne"
                      data-bs-parent="#accordionFlushExample"
                    >
                      <div class="accordion-body py-4 px-5">
                        <div id="search-wrapper" class="py-3">
                          <input
                            v-model="search"
                            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            type="text"
                            placeholder="Search causes of death"
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
                              :value="cause.id"
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
                    </div>
                  </div>
                </div>
              </div>
              <div class="overflow-y-auto h-48 px-4 py-4">
                <div
                  id="accordionYears"
                  class="accordion accordion-flush border-2 border-slate-300"
                >
                  <div class="accordion-item rounded-none">
                    <h2 id="years-headingOne" class="accordion-header mb-0">
                      <button
                        class="accordion-button collapsed relative flex items-center w-full py-4 px-5 text-base text-gray-800 text-left bg-white border-0 rounded-none transition focus:outline-none"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#flush-collapseYear"
                        aria-expanded="false"
                        aria-controls="flush-collapseYear"
                      >
                        Year Range
                      </button>
                    </h2>
                    <div
                      id="flush-collapseYear"
                      class="accordion-collapse border-0 collapse show"
                      aria-labelledby="flush-headingOne"
                      data-bs-parent="#accordionFlushExample"
                    >
                      <div class="accordion-body py-4 px-5">
                        <div class="slider-container">
                          <vue-slider
                            v-model="filteredYears"
                            :min="1640"
                            :max="1754"
                            :interval="1"
                            :enable-cross="false"
                            :lazy="true"
                            :dot-options="dotOptions"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="overflow-y-auto h-48 px-4 py-4">
                <!-- spacer -->
              </div>
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
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- end of filter -->
    <vue-good-table
      mode="remote"
      :columns="columns"
      :rows="totalDeaths"
      :total-rows="totalRecords"
      max-height="600px"
      :fixed-header="true"
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
      @on-per-page-change="onPerPageChange"
    >
      <template slot="table-column" slot-scope="props">
        <span v-if="props.column.label == 'Cause'">
          <span class="hint--top" aria-label="The cause of death.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Count'">
          <span class="hint--top" aria-label="The total cause of death.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Week Number'">
          <span class="hint--top" aria-label="The week number in the year.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Year'">
          <span class="hint--top" aria-label="The year for the data.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else>
          {{ props.column.label }}
        </span>
      </template>
    </vue-good-table>
  </div>
</template>

<script>
import axios from "axios";
import VueSlider from "vue-slider-component";
import "vue-slider-component/theme/antd.css";

export default {
  name: "DeathCausesTable",
  components: {
    VueSlider,
  },
  data() {
    return {
      search: "",
      totalDeaths: [],
      causesList: [],
      totalRecords: 0,
      errors: [],
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
      filteredYears: [1640, 1754],
      filteredCauseIDs: [],
      serverParams: {
        limit: 25,
        offset: 0,
        causes: "",
        year: [1640, 1754],
        perPage: 25,
        page: 1,
      },
    };
  },
  computed: {
    filterCausesList() {
      return this.causesList.filter((parish) => {
        return parish.name.toLowerCase().includes(this.search.toLowerCase());
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
      })
      .catch((e) => {
        this.errors.push(e);
        // eslint-disable-next-line no-console
        console.log(this.errors);
      });
    axios
      .get("https://data.chnm.org/bom/totalbills?type=Causes")
      .then((response) => {
        this.totalRecords = response.data[0].total_records;
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
        })
        .catch((e) => {
          this.errors.push(e);
          // eslint-disable-next-line no-console
          console.log(this.errors);
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
      this.filteredYears = [1640, 1754];
      this.search = "";
      this.updateParams({
        causes: [],
        year: [1640, 1754],
      });
      this.loadItems();
    },
  },
};
</script>
