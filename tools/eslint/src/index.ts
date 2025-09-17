import { antfu } from "@antfu/eslint-config";
import merge from "lodash.merge";

export function withConfig(
    config?: Parameters<typeof antfu>[0],
): ReturnType<typeof antfu> {
    return antfu(
        merge(
            {},
            {
                stylistic: {
                    quotes: "double",
                    indent: 4,
                    semi: true,
                },
                rules: {
                    "yaml/indent": ["warn", 4, { indicatorValueIndent: 2 }],
                    "style/arrow-parens": ["warn", "always"],
                    "style/operator-linebreak": ["off"],
                    "style/brace-style": ["warn", "1tbs"],
                    "style/quote-props": ["error", "as-needed"],
                },
            },
            config,
        ),
    );
}
