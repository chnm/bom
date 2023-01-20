// src/lib/shift-nodes-before-parent.js
function shiftNodesBeforeParent(node) {
  const parent = node.parent;
  const index = parent.index(node);
  if (index) {
    parent.cloneBefore().removeAll().append(parent.nodes.slice(0, index));
  }
  parent.before(node);
  return parent;
}

// src/lib/cleanup-parent.js
function cleanupParent(parent) {
  if (!parent.nodes.length) {
    parent.remove();
  }
}

// src/lib/valid-selector.js
var valid_selector_default = /&(?:[^\w-|]|$)/;
var complex = /&[^]*&/;
var replaceable = /&/g;

// src/lib/merge-selectors.js
function mergeSelectors(fromSelectors, toSelectors) {
  return fromSelectors.reduce((selectors, fromSelector) => selectors.concat(toSelectors.map((toSelector) => complex.test(toSelector) ? toSelector.replace(replaceable, `:is(${fromSelector})`) : toSelector.replace(replaceable, fromSelector))), []);
}

// src/lib/rule-within-rule.js
function transformRuleWithinRule(node) {
  const parent = shiftNodesBeforeParent(node);
  node.selectors = mergeSelectors(parent.selectors, node.selectors);
  const areSameRule = node.type === "rule" && parent.type === "rule" && node.selector === parent.selector || node.type === "atrule" && parent.type === "atrule" && node.params === parent.params;
  if (areSameRule) {
    node.append(...parent.nodes);
  }
  cleanupParent(parent);
}
var isRuleWithinRule = (node) => node.type === "rule" && Object(node.parent).type === "rule" && node.selectors.every((selector) => selector.trim().lastIndexOf("&") === 0 && valid_selector_default.test(selector));

// src/lib/list.js
var split = (string, separators, last) => {
  let array = [];
  let current = "";
  let split2 = false;
  let func = 0;
  let quote = false;
  let escape = false;
  for (let letter of string) {
    if (escape) {
      escape = false;
    } else if (letter === "\\") {
      escape = true;
    } else if (quote) {
      if (letter === quote) {
        quote = false;
      }
    } else if (letter === '"' || letter === "'") {
      quote = letter;
    } else if (letter === "(") {
      func += 1;
    } else if (letter === ")") {
      if (func > 0)
        func -= 1;
    } else if (func === 0) {
      if (separators.includes(letter))
        split2 = true;
    }
    if (split2) {
      if (current !== "")
        array.push(current.trim());
      current = "";
      split2 = false;
    } else {
      current += letter;
    }
  }
  if (last || current !== "")
    array.push(current.trim());
  return array;
};
var comma = (string) => split(string, [","], true);

// src/lib/nest-rule-within-rule.js
function transformNestRuleWithinRule(node) {
  const parent = shiftNodesBeforeParent(node);
  const rule = parent.clone().removeAll().append(node.nodes);
  node.replaceWith(rule);
  rule.selectors = mergeSelectors(parent.selectors, comma(node.params));
  cleanupParent(parent);
  walk(rule);
}
var isNestRuleWithinRule = (node) => node.type === "atrule" && node.name === "nest" && Object(node.parent).type === "rule" && comma(node.params).every((selector) => selector.split("&").length >= 2 && valid_selector_default.test(selector));

// src/lib/valid-atrules.js
var valid_atrules_default = ["container", "document", "media", "supports"];

// src/lib/atrule-within-rule.js
function atruleWithinRule(node) {
  const parent = shiftNodesBeforeParent(node);
  const rule = parent.clone().removeAll().append(node.nodes);
  node.append(rule);
  cleanupParent(parent);
  walk(rule);
}
var isAtruleWithinRule = (node) => node.type === "atrule" && valid_atrules_default.includes(node.name) && Object(node.parent).type === "rule";

// src/lib/merge-params.js
function mergeParams(fromParams, toParams) {
  return comma(fromParams).map((params1) => comma(toParams).map((params2) => `${params1} and ${params2}`).join(", ")).join(", ");
}

// src/lib/atrule-within-atrule.js
function transformAtruleWithinAtrule(node) {
  const parent = shiftNodesBeforeParent(node);
  node.params = mergeParams(parent.params, node.params);
  cleanupParent(parent);
}
var isAtruleWithinAtrule = (node) => node.type === "atrule" && valid_atrules_default.includes(node.name) && Object(node.parent).type === "atrule" && node.name === node.parent.name;

// src/lib/walk.js
function walk(node) {
  node.nodes.slice(0).forEach((child) => {
    if (child.parent === node) {
      if (isRuleWithinRule(child)) {
        transformRuleWithinRule(child);
      } else if (isNestRuleWithinRule(child)) {
        transformNestRuleWithinRule(child);
      } else if (isAtruleWithinRule(child)) {
        atruleWithinRule(child);
      } else if (isAtruleWithinAtrule(child)) {
        transformAtruleWithinAtrule(child);
      }
      if (Object(child.nodes).length) {
        walk(child);
      }
    }
  });
}

// src/postcss-8-nesting.js
function postcssNesting() {
  return {
    postcssPlugin: "postcss-nesting",
    Once(root) {
      walk(root);
    }
  };
}
postcssNesting.postcss = true;

// src/postcss-7-nesting.js
var postcss_7_nesting_default = Object.defineProperties(postcssNesting, Object.getOwnPropertyDescriptors({
  get postcss() {
    function postcssPlugin(cssRoot) {
      const visitors = postcssNesting();
      if (typeof visitors.Once === "function") {
        visitors.Once(cssRoot);
      }
    }
    postcssPlugin.postcssPlugin = "postcss-nesting";
    postcssPlugin.postcssVersion = "8.2.13";
    return postcssPlugin;
  }
}));
module.exports=Object.assign(postcss_7_nesting_default,{default:postcss_7_nesting_default})
//# sourceMappingUrl=index.map