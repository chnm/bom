<template>
  <div id="visualizations">
    <TheNavBar />
    <div class="flex min-h-screen items-center justify-start bg-white">
      <div class="mx-auto w-full max-w-lg">
        <h2 class="text-4xl font-medium">Visualizations</h2>

        <p>
          <strong>Coming soon</strong>. Visualizing, mapping, and aggregating
          data about the London Bills of Mortality.
        </p>
      </div>
    </div>
    <TheFooter />
  </div>
</template>

<script type="text/javascript">
import TheNavBar from "~/components/TheNavBar.vue";
import TheFooter from "~/components/TheFooter.vue";

export default {
  components: {
    TheNavBar,
    TheFooter,
  },
  data() {
    return {
    };
  },
};
</script>
