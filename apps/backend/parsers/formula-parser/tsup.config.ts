import process from "node:process";
import { defineConfig } from "tsup";

export default defineConfig(() => {
    const isProduction = process.env.NODE_ENV === "production";

    return {
        entry: ["src/server.ts"],
        outDir: "dist",
        format: ["esm", "cjs"],
        clean: true,
        dts: true,
        sourcemap: true,
        minify: isProduction,
        external: ["@grpc/grpc-js", "google-protobuf", "winston"],
    };
});
