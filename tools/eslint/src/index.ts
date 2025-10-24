import { antfu } from "@antfu/eslint-config";
import pluginDepend from "eslint-plugin-depend";
// @ts-expect-error "theres no official .d.ts for this module"
import pluginYouDontNeedLodash from "eslint-plugin-you-dont-need-lodash-underscore";
import merge from "lodash.merge";

type Config = Parameters<typeof antfu>[0];

export function withConfig(config?: Config): ReturnType<typeof antfu> {
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
                plugins: {
                    "you-dont-need-lodash-underscore": pluginYouDontNeedLodash,
                    depend: pluginDepend,
                },
            } satisfies Config,
            config,
        ),
    );
}
