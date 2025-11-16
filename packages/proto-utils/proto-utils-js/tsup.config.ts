import process from "node:process";
import { defineConfig } from "tsup";

export default defineConfig(() => {
    const isProduction = process.env.NODE_ENV === "production";

    return {
        entry: ["src/index.ts"],
        outDir: "dist",
        format: ["cjs", "esm"],
        clean: true,
        dts: !isProduction,
        sourcemap: !isProduction,
        minify: isProduction,
        platform: "node",
        external: ["@grpc/grpc-js", "google-protobuf"],
        outExtension({ format }) {
            if (format === "esm") {
                return {
                    js: ".mjs",
                    dts: ".d.mts",
                };
            }

            if (format === "cjs") {
                return {
                    js: ".cjs",
                    dts: ".d.cts",
                };
            }

            return {
                js: ".js",
                dts: ".d.ts",
            };
        },
    };
});
