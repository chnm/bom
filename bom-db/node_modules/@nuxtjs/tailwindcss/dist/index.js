'use strict';

const path = require('path');
const fs = require('fs');
const defu = require('defu');
const clearModule = require('clear-module');
const chalk = require('chalk');
const ufo = require('ufo');
const consola = require('consola');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

const defu__default = /*#__PURE__*/_interopDefaultLegacy(defu);
const clearModule__default = /*#__PURE__*/_interopDefaultLegacy(clearModule);
const chalk__default = /*#__PURE__*/_interopDefaultLegacy(chalk);
const consola__default = /*#__PURE__*/_interopDefaultLegacy(consola);

var name = "@nuxtjs/tailwindcss";
var version = "4.2.1";

const defaultTailwindConfig = ({rootDir, srcDir}) => ({
  theme: {
    extend: {}
  },
  variants: {
    extend: {}
  },
  plugins: [],
  purge: {
    content: [
      `${srcDir}/components/**/*.{vue,js,ts}`,
      `${srcDir}/layouts/**/*.vue`,
      `${srcDir}/pages/**/*.vue`,
      `${srcDir}/plugins/**/*.{js,ts}`,
      `${rootDir}/nuxt.config.js`,
      `${rootDir}/nuxt.config.ts`
    ]
  }
});

const logger = consola__default['default'].withScope("nuxt:tailwindcss");
async function tailwindCSSModule(moduleOptions) {
  const {nuxt} = this;
  const options = defu__default['default'].arrayFn(moduleOptions, nuxt.options.tailwindcss, {
    configPath: "tailwind.config.js",
    cssPath: path.join(nuxt.options.dir.assets, "css", "tailwind.css"),
    exposeConfig: false,
    config: defaultTailwindConfig(nuxt.options),
    viewer: nuxt.options.dev
  });
  const configPath = nuxt.resolver.resolveAlias(options.configPath);
  const cssPath = options.cssPath && nuxt.resolver.resolveAlias(options.cssPath);
  nuxt.options.build.postcss = defu__default['default'](nuxt.options.build.postcss, {
    plugins: {
      "postcss-nesting": {},
      "postcss-custom-properties": {}
    }
  });
  await this.addModule("@nuxt/postcss8");
  if (typeof cssPath === "string") {
    if (fs.existsSync(cssPath)) {
      logger.info(`Using Tailwind CSS from ~/${path.relative(nuxt.options.srcDir, cssPath)}`);
      nuxt.options.css.unshift(cssPath);
    } else {
      nuxt.options.css.unshift(path.resolve(__dirname, "runtime", "tailwind.css"));
    }
  }
  let tailwindConfig = {};
  if (fs.existsSync(configPath)) {
    clearModule__default['default'](configPath);
    tailwindConfig = nuxt.resolver.requireModule(configPath);
    logger.info(`Merging Tailwind config from ~/${path.relative(this.options.srcDir, configPath)}`);
    if (Array.isArray(tailwindConfig.purge)) {
      tailwindConfig.purge = {content: tailwindConfig.purge};
    }
  }
  tailwindConfig = defu__default['default'].arrayFn(tailwindConfig, options.config);
  if (nuxt.options.dev) {
    nuxt.options.watch.push(configPath);
  }
  nuxt.hook("build:before", async () => {
    if (!nuxt.options.dev && !process.env.NODE_ENV) {
      process.env.NODE_ENV = "production";
    }
    await nuxt.callHook("tailwindcss:config", tailwindConfig);
    tailwindConfig._hash = String(Date.now());
    if (options.jit === true) {
      logger.warn("`tailwindcss.jit` option had been deprecated in favour of tailwind config `mode: 'jit'`");
      tailwindConfig.mode = "jit";
    }
    if (tailwindConfig.mode === "jit") {
      logger.info("Tailwind JIT activated");
    }
    nuxt.options.build.postcss.plugins.tailwindcss = tailwindConfig;
    if (options.exposeConfig) {
      const resolveConfig = require("tailwindcss/resolveConfig");
      const resolvedConfig = resolveConfig(tailwindConfig);
      this.addTemplate({
        src: path.resolve(__dirname, "runtime/tailwind.config.json"),
        fileName: "tailwind.config.json",
        options: {config: resolvedConfig}
      });
      nuxt.options.alias["~tailwind.config"] = path.resolve(nuxt.options.buildDir, "tailwind.config.json");
      const {cacheGroups} = nuxt.options.build.optimization.splitChunks;
      cacheGroups.tailwindConfig = {
        test: /tailwind\.config/,
        chunks: "all",
        priority: 10,
        name: true
      };
    }
  });
  if (nuxt.options.dev && options.viewer) {
    const path = "/_tailwind/";
    process.nuxt = process.nuxt || {};
    process.nuxt.$config = process.nuxt.$config || {};
    process.nuxt.$config.tailwind = {
      viewerPath: path,
      getConfig: () => tailwindConfig
    };
    this.addServerMiddleware({path, handler: require.resolve("./runtime/config-viewer")});
    nuxt.hook("listen", () => {
      const url = ufo.withTrailingSlash(ufo.joinURL(nuxt.server.listeners && nuxt.server.listeners[0] ? nuxt.server.listeners[0].url : "/", path));
      nuxt.options.cli.badgeMessages.push(`Tailwind Viewer: ${chalk__default['default'].underline.yellow(url)}`);
    });
  }
}
tailwindCSSModule.meta = {name, version};

module.exports = tailwindCSSModule;
