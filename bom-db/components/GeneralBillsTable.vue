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
                        Parishes
                      </button>
                    </h2>
                    <div
                      id="flush-collapseOne"
                      class="accordion-collapse border-0 collapse show"
                      aria-labelledby="flush-headingOne"
                      data-bs-parent="#accordion"
                    >
                      <div class="accordion-body py-4 px-5">
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
                            v-for="(name, index) in filterParishNamesList"
                            :key="index"
                          >
                            <input
                              :id="name.canonical_name"
                              v-model="filteredParishIDs"
                              :value="name.id"
                              name="parish"
                              type="checkbox"
                              class="dropdown-item"
                            />
                            <label :for="name.canonical_name"
                              ><span>{{ name.canonical_name }}</span></label
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
                      class="accordion-collapse border-0 collapse show h-24"
                      aria-labelledby="flush-headingOne"
                      data-bs-parent="#accordion"
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
                            @change="updateFilteredYearsArray"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="overflow-y-auto h-48 px-4 py-4">
                <div
                  id="accordionCount"
                  class="accordion accordion-flush border-2 border-slate-300"
                >
                  <div class="accordion-item rounded-none">
                    <h2 id="count-headingOne" class="accordion-header mb-0">
                      <button
                        class="accordion-button collapsed relative flex items-center w-full py-4 px-5 text-base text-gray-800 text-left bg-white border-0 rounded-none transition focus:outline-none"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#flush-collapseCount"
                        aria-expanded="false"
                        aria-controls="flush-collapseCount"
                      >
                        Count Type
                      </button>
                    </h2>
                    <div
                      id="flush-collapseCount"
                      class="accordion-collapse border-0 collapse show h-24"
                      aria-labelledby="flush-headingOne"
                      data-bs-parent="#accordion"
                    >
                      <div class="accordion-body py-4 px-5">
                        <!-- dropdown -->
                        <div class="dropdown relative">
                          <select
                            v-model="filteredCountType"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                            arias-expanded="false"
                            @change="updateFilteredCountType($event)"
                          >
                            <option
                              v-for="(name, index) in countType"
                              :key="index"
                              :value="name"
                              class="dropdown-menu min-w-max text-base float-left"
                            >
                              {{ name }}
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
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
      :rows="totalParishes"
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
        rowsPerPageLabel: 'Bills per page',
      }"
      :sort-options="{ enabled: false }"
      :search-options="{ enabled: false }"
      style-class="vgt-table condensed striped"
      @on-page-change="onPageChange"
      @on-row-click="onRowClick"
      @on-per-page-change="onPerPageChange"
    >
      <template slot="table-column" slot-scope="props">
        <span v-if="props.column.label == 'Parish'">
          <span class="hint--top" aria-label="The names of the parishes.">
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Count Type'">
          <span
            class="hint--top"
            aria-label="The count type, either by the number in the parish with plague or the number buried in the parish."
          >
            {{ props.column.label }}
          </span>
        </span>
        <span v-else-if="props.column.label == 'Count'">
          <span
            class="hint--top"
            aria-label="The number of plague or buried in the parish."
          >
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
        <span v-else-if="props.column.label == 'Split Year'">
          <span class="hint--top" aria-label="The split year for the data.">
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

export default {
  name: "GeneralBillsTable",
  components: {
    VueSlider,
  },
  data() {
    return {
      errors: [],
      search: "",
      columns: [
        {
          label: "Parish",
          field: "name",
        },
        {
          label: "Count Type",
          field: "count_type",
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
        {
          label: "Split Year",
          field: "split_year",
        },
      ],
      parishNames: [],
      filteredBillsData: [],
      totalParishes: [],
      totalRecords: 0,
      countType: ["Total", "Plague", "Buried"],
      filteredCountType: "Total",
      filteredParishIDs: [],
      filteredYears: [1640, 1754],
      // Always show vue-slider tooltips
      dotOptions: [
        {
          tooltip: "always",
        },
        {
          tooltip: "always",
        },
      ],
      serverParams: {
        limit: 25,
        offset: 0,
        count_type: "Total",
        bill_type: "General",
        parishes: "",
        year: [1640, 1754],
        perPage: 25,
        page: 1,
      },
    };
  },
  computed: {
    filterParishNamesList() {
      return this.parishNames.filter((parish) => {
        return parish.name.toLowerCase().includes(this.search.toLowerCase());
      });
    },
  },
  mounted() {
    axios
      .get(
        "https://data.chnm.org/bom/bills?start-year=" +
          this.serverParams.year[0] +
          "&end-year=" +
          this.serverParams.year[1] +
          "&bill-type=" +
          this.serverParams.bill_type +
          "&count-type=" +
          // if count-type is not All, don't include it in the URL
          (this.serverParams.count_type === "All" ||
          this.serverParams.count_type === "Total"
            ? ""
            : this.serverParams.count_type) +
          // if parish is not empty, use it in the URL to send a query
          (this.serverParams.parishes === ""
            ? ""
            : "&parishes=" + this.serverParams.parishes) +
          "&limit=" +
          this.serverParams.limit +
          "&offset=" +
          this.serverParams.offset
      )
      .then((response) => {
        this.totalParishes = response.data;
      })
      .catch((e) => {
        this.errors.push(e);
        // eslint-disable-next-line no-console
        console.log(this.errors);
      });
    axios
      .get("https://data.chnm.org/bom/parishes")
      .then((response) => {
        this.parishNames = response.data;
      })
      .catch((e) => {
        this.errors.push(e);
        // eslint-disable-next-line no-console
        console.log(this.errors);
      });
    axios
      .get("https://data.chnm.org/bom/totalbills?type=General")
      .then((response) => {
        this.totalRecords = response.data[0].total_records;
      })
      .catch((e) => {
        this.errors.push(e);
        // eslint-disable-next-line no-console
        console.log(this.errors);
      });
  },
  methods: {
    onRowClick(params) {
      // eslint-disable-next-line no-console
      console.log("row clicked", params);
      // params.row - row object
      // params.pageIndex - index of this row on the current page.
      // params.selected - if selection is enabled this argument
      // indicates selected or not
      // params.event - click event
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

    // TODO: Add table sorting.
    // onSortChange(params) {
    //   this.updateParams({
    //     sort: [
    //       {
    //         type: params.sortType,
    //         field: this.parishColumns[params.columnIndex].name,
    //       },
    //     ],
    //   });
    //   this.loadItems();
    // },

    loadItems() {
      return axios
        .get(
          "https://data.chnm.org/bom/bills?start-year=" +
            this.serverParams.year[0] +
            "&end-year=" +
            this.serverParams.year[1] +
            "&bill-type=" +
            this.serverParams.bill_type +
            // if count-type is All, don't include it in the URL to get the right query
            (this.serverParams.count_type === "All" ||
            this.serverParams.count_type === "Total"
              ? ""
              : "&count-type=" + this.serverParams.count_type) +
            // if parish is not empty, use it in the URL to send a query
            (this.serverParams.parishes === ""
              ? ""
              : "&parishes=" + this.serverParams.parishes) +
            "&limit=" +
            this.serverParams.limit +
            "&offset=" +
            this.serverParams.offset
        )
        .then((response) => {
          this.totalParishes = response.data;
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
      console.log(newYears);
      this.updateParams({
        year: newYears,
      });
    },

    // When a user selects a count type, that count type is changed in the serverParams.count_type.
    updateFilteredCountType(event) {
      this.updateParams({
        count_type: event.target.value,
      });
    },

    // When the user clicks the Apply Filters button, we use the
    // v-model data in filteredParishIDs, filteredYears, and
    // filteredCountType to update the serverParams.parishes, serverParams.year, and
    // serverParams.count_type arrays. Then we submit a new request to the server.
    applyFilters() {
      this.updateParams({
        parishes: this.filteredParishIDs,
        year: this.filteredYears,
        count_type: this.filteredCountType,
      });
      this.loadItems();
    },

    // When a user clicks the Reset Filters button, we return the data to their defaults.
    resetFilters() {
      this.filteredParishIDs = [];
      this.filteredYears = [1640, 1754];
      this.filteredCountType = "Total";
      this.search = "";
      this.updateParams({
        parishes: [],
        count_type: "Total",
        year: [1640, 1754],
      });
      this.loadItems();
    },
  },
};
</script>
