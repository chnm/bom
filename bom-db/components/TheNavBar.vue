<template>
  <nav
    class="relative flex flex-wrap items-center justify-between px-2 py-3"
  >
    <div
      class="container px-4 mx-auto flex flex-wrap items-center justify-between"
    >
      <div
        class="w-full relative flex justify-between lg:w-auto px-4 lg:static lg:block lg:justify-start"
      >
      <div class="flex items-center flex-no-shrink text-white mr-6">
        <img src="/death-by-numbers.jpg" alt="Death by Numbers" class="object-scale-down w-48 overflow-hidden" />
        <NuxtLink
          id="site-title"
          class="text-sm font-bold leading-relaxed inline-block mr-4 py-2 whitespace-nowrap uppercase text-white"
          to="/"
          >London Bills of Mortality</NuxtLink
        >
      </div>
        <button
          class="text-white cursor-pointer text-xl leading-none px-3 py-1 border border-solid border-transparent rounded bg-transparent block lg:hidden outline-none focus:outline-none"
          type="button"
          @click="toggleNavbar()"
        >
          <i class="fas fa-bars"></i>
        </button>
      </div>
      <div
        :class="{ hidden: !showMenu, flex: showMenu }"
        class="lg:flex lg:flex-grow items-center"
      >
        <ul class="flex flex-col lg:flex-row list-none ml-auto">
          <li class="nav-item">
            <a
              target="_window"
              href="https://deathbynumbers.org/posts/"
              class="px-3 py-2 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75 ml-2"
              >Blog</a
            >
          </li>
          <li class="nav-item">
            <NuxtLink
              to="/"
              class="px-3 py-2 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75 ml-2"
              >Database</NuxtLink
            >
          </li>
          <li class="nav-item">
            <NuxtLink
              to="/visualizations/"
              class="px-3 py-2 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75 ml-2"
              >Visualizations</NuxtLink
            >
          </li>
          <li class="nav-item">
              <a href="https://github.com/chnm/bom" class="px-3 py-2 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75 ml-2">
              Data</a>
          </li>
          <div class="relative inline-flex align-middle w-full">
            <li ref="btnDropdownRef" class="nav-item" @click="toggleDropdown()">
              <a
                class="px-3 py-2 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75"
                href="#"
              >
                <span class="ml-2">About</span>
              </a>
            </li>
            <div
              ref="popoverDropdownRef"
              :class="{
                hidden: !dropdownPopoverShow,
                block: dropdownPopoverShow,
              }"
              class="bg-white text-base z-50 float-left py-2 list-none text-left rounded shadow-lg mt-1"
              style="min-width: 12rem"
            >
              <a
                target="_window"
                href="https://deathbynumbers.org"
                class="text-sm py-2 px-4 font-normal block w-full whitespace-nowrap bg-transparent text-blueGray-700"
              >
                Project description &amp; team
              </a>
              <div
                class="h-0 my-2 border border-solid border-t-0 border-blueGray-800 opacity-25"
              ></div>
              <a
                target="_window"
                href="https://github.com/chnm/bom-db/issues"
                class="text-sm py-2 px-4 font-normal block w-full whitespace-nowrap bg-transparent text-blueGray-700"
              >
                Report an issue
              </a>
            </div>
          </div>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { createPopper } from "@popperjs/core";

export default {
  name: "IndigoNavbar",
  data() {
    return {
      showMenu: false,
      dropdownPopoverShow: false,
    };
  },
  methods: {
    toggleNavbar() {
      this.showMenu = !this.showMenu;
    },
    toggleDropdown() {
      if (this.dropdownPopoverShow) {
        this.dropdownPopoverShow = false;
      } else {
        this.dropdownPopoverShow = true;
        createPopper(this.$refs.btnDropdownRef, this.$refs.popoverDropdownRef, {
          placement: "bottom-start",
        });
      }
    },
  },
};
</script>
