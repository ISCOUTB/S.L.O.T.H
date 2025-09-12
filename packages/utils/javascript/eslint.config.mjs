import antfu from "@antfu/eslint-config";

export default antfu({
    type: "lib",
    typescript: true,
    stylistic: {
        semi: true,
        indent: 4,
        quotes: "double",
    },
});
