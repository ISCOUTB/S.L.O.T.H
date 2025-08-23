import antfu from "@antfu/eslint-config";

export default antfu({
    type: "app",
    typescript: true,
    stylistic: {
        indent: 4,
        quotes: "double",
        semi: true,
    },
});
