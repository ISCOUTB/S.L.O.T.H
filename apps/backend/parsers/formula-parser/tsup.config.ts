import process from "node:process";
import { defineConfig } from "tsup";

export default defineConfig(() => {
    const isProduction = process.env.NODE_ENV === "production";

    return {
        entry: ["src/server.ts"],
        outDir: "dist",
        format: ["cjs"],
        clean: true,
        dts: !isProduction,
        sourcemap: !isProduction,
        minify: isProduction,
        platform: "node",
        external: ["@grpc/grpc-js", "google-protobuf"],
    };
});
