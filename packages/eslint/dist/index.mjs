// src/index.ts
import { antfu } from "@antfu/eslint-config";
import merge from "lodash.merge";
function withConfig(config) {
  return antfu(
    merge(
      {},
      {
        stylistic: {
          quotes: "double",
          indent: 4,
          semi: true
        },
        rules: {
          "yaml/indent": ["warn", 4, { indicatorValueIndent: 2 }]
        }
      },
      config
    )
  );
}
export {
  withConfig
};
//# sourceMappingURL=index.mjs.map