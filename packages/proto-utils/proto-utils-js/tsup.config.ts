import process from "node:process";
import { defineConfig } from "tsup";

export default defineConfig(() => {
    const isProduction = process.env.NODE_ENV === "production";

    return {
        entry: ["src/index.ts"],
        outDir: "dist",
        format: ["esm", "cjs"],
        clean: true,
        dts: !isProduction,
        sourcemap: !isProduction,
        minify: isProduction,
        bundle: true,
        splitting: false,
        noExternal: [/.*/],
    };
});
