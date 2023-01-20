<template>
  <div id="visualizations">
    <TheNavBar />
    <div class="flex min-h-screen items-center justify-start bg-white pt-7">
      <div class="container mx-auto px-4">
        <h2 class="text-4xl font-medium pb-4">Understanding Causes of Death</h2>
        <div class="flex flex-wrap w-2/3 p-5 prose">
        <p>Description of the visualization.  Fusce lobortis neque a sapien pharetra, eget scelerisque libero eleifend. Nullam gravida mollis arcu, et porta libero luctus eu. Vivamus id nulla ante. Nunc eu enim elementum, pellentesque ipsum eget, posuere ligula. Sed sit amet est sapien. Proin varius orci diam, a gravida urna dapibus eget. Nam molestie risus id feugiat lacinia. Nulla elit ipsum, pharetra fringilla consectetur et, ultricies sed mi. Proin mattis nulla a neque elementum porttitor. Pellentesque et risus massa. In hac habitasse platea dictumst. Sed viverra, tortor vitae commodo vehicula, nibh arcu gravida purus, eu rutrum sapien velit in lectus. Vivamus sagittis, quam quis condimentum condimentum, sapien quam maximus diam, condimentum gravida diam elit sed nibh. Sed pulvinar quis sem sit amet scelerisque. Morbi sit amet suscipit tortor. Nam volutpat purus quis rhoncus scelerisque. </p>
               <div class=" pt-5 pb-5">
               <BarChart 
                  title="Causes of death across transcribed plague bills"
               />
               </div>
        <p>Fusce lobortis neque a sapien pharetra, eget scelerisque libero eleifend. Nullam gravida mollis arcu, et porta libero luctus eu. Vivamus id nulla ante. Nunc eu enim elementum, pellentesque ipsum eget, posuere ligula. Sed sit amet est sapien. Proin varius orci diam, a gravida urna dapibus eget. Nam molestie risus id feugiat lacinia. Nulla elit ipsum, pharetra fringilla consectetur et, ultricies sed mi. Proin mattis nulla a neque elementum porttitor. Pellentesque et risus massa. In hac habitasse platea dictumst. Sed viverra, tortor vitae commodo vehicula, nibh arcu gravida purus, eu rutrum sapien velit in lectus. Vivamus sagittis, quam quis condimentum condimentum, sapien quam maximus diam, condimentum gravida diam elit sed nibh. Sed pulvinar quis sem sit amet scelerisque. Morbi sit amet suscipit tortor. Nam volutpat purus quis rhoncus scelerisque. </p>
        <p>Fusce lobortis neque a sapien pharetra, eget scelerisque libero eleifend. Nullam gravida mollis arcu, et porta libero luctus eu. Vivamus id nulla ante. Nunc eu enim elementum, pellentesque ipsum eget, posuere ligula. Sed sit amet est sapien. Proin varius orci diam, a gravida urna dapibus eget. Nam molestie risus id feugiat lacinia. Nulla elit ipsum, pharetra fringilla consectetur et, ultricies sed mi. Proin mattis nulla a neque elementum porttitor. Pellentesque et risus massa. In hac habitasse platea dictumst. Sed viverra, tortor vitae commodo vehicula, nibh arcu gravida purus, eu rutrum sapien velit in lectus. Vivamus sagittis, quam quis condimentum condimentum, sapien quam maximus diam, condimentum gravida diam elit sed nibh. Sed pulvinar quis sem sit amet scelerisque. Morbi sit amet suscipit tortor. Nam volutpat purus quis rhoncus scelerisque. </p>
        </div>
      </div>
    </div>
    <TheFooter />
  </div>
</template>

<script type="text/javascript">
import BarChart from "~/components/visualizations/CausesBarChart.vue";
import TheNavBar from "~/components/TheNavBar.vue";
import TheFooter from "~/components/TheFooter.vue";

export default {
  components: {
    TheNavBar,
    TheFooter,
    BarChart,
  },
  data() {
    return {
      data: [],
      serverParams: {
        limit: 500,
        offset: 0,
        count_type: "All",
        bill_type: "Weekly",
        parishes: "",
        year: [1640, 1754],
        perPage: 25,
        page: 1,
      },
    };
  },
  computed: {
    // We sum the number of bills for each year
    // and return an array of objects with the year and the sum
    yearCount() {
      const yearCount = this.data.reduce((acc, bill) => {
        const year = bill.year;
        if (!acc[year]) {
          acc[year] = 0;
        }
        acc[year] += 1;
        return acc;
      }, {});
      return Object.keys(yearCount).map((year) => {
        return { year, count: yearCount[year] };
      });
    },
  },
};
</script>

<style scoped>
.chart {
    display: block;
}
</style>