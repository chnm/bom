<template>
  <div id="app">
    <TheNavBar />
    <App />
    <TheFooter />
  </div>
</template>

<script type="text/javascript">
import TheNavBar from "~/components/TheNavBar.vue";
import App from "~/components/App.vue";
import TheFooter from "~/components/TheFooter.vue";

export default {
  components: {
    TheNavBar,
    App,
    TheFooter,
  },
};
</script>