<script>
export default {
  name: "InstructionsModal",
  methods: {
    close() {
      this.$emit("close");
    },
  },
};
</script>

<template>
  <div>
    <div
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
                      <p class="text-sm text-gray-500">
                        Lorem, ipsum dolor sit amet consectetur adipisicing
                        elit. Quia, porro. Non a excepturi, voluptatibus ipsam
                        magnam, eligendi, accusantium ipsa quae quis praesentium
                        voluptate saepe ullam sint ea itaque consectetur
                        impedit?
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
