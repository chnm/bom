<template>
  <div id="app">
    <NavBar />
    <App />
    <Footer />
  </div>
</template>

<script type="text/javascript">
import NavBar from "~/components/NavBar.vue";
import App from "~/components/App.vue";
import Footer from "~/components/Footer.vue";

export default {
  components: {
    NavBar,
    App,
    Footer,
  },
};
</script>