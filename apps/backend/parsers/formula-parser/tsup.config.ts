import process from "node:process";
import { defineConfig } from "tsup";

function $<D, P>(nodeEnv: string, dev: D, prod?: P): D | P | undefined {
    if (nodeEnv === "production") {
        return prod;
    }

    return dev;
}

export default defineConfig(() => {
    const isProduction = process.env.NODE_ENV === "production";

    return {
        entry: ["src/server.ts"],
        outDir: "dist",
        format: ["cjs"],
        clean: true,
        dts: $(process.env.NODE_ENV!, { resolve: true }, false),
        sourcemap: !isProduction,
        minify: isProduction,
        platform: "node",
        external: ["@grpc/grpc-js", "google-protobuf"],
        noExternal: ["@etl-design/packages-proto-utils-js"],
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
