<template>
  <footer class="relative bg-gray-200 pt-8 pb-6">
    <div class="container mx-auto px-4">
      <div class="flex flex-wrap">
        <div class="w-full lg:w-6/12 px-4">
          <p>
            Bills of Mortality is generously funded in part by the
            <a class="underline" href="https://www.nsf.gov/">National Science Foundation</a> and
            developed by the
            <a class="underline" href="https://rrchnm.org/"
              >Roy Rosenzweig Center for History and New Media</a
            >
            at <a class="underline" href="https://www2.gmu.edu/">George Mason University</a>.
          </p>
          <div class="logos row">
            <a href="https://rrchnm.org/"
              ><img
                class="rrchnm-logo"
                src="~/assets/img/rrchnm-logo.png"
                alt="Roy Rosenzweig Center for History and New Media logo"
            /></a>
            <a href="https://www2.gmu.edu/"
              ><img
                class="gmu-logo"
                src="~/assets/img/gmu-logo.png"
                alt="George Mason University logo"
            /></a>
            <a href="https://www.nsf.gov/"
              ><img
                class="nsf-logo"
                src="~/assets/img/nsf-logo.png"
                alt="National Science Foundation logo"
            /></a>
          </div>
        </div>
        <div class="w-full lg:w-6/12 px-4">
          <div class="flex flex-wrap items-top mb-6">
            
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
<script>
export default {
  data() {
    return {
      date: new Date().getFullYear(),
    };
  },
};
</script>
