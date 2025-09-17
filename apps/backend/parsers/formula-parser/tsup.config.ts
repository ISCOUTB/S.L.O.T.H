import { defineConfig } from "tsup";

export default defineConfig({
    entry: ["src/server.ts"],
    outDir: "dist",
    format: ["esm", "cjs"],
    clean: true,
    dts: true,
    sourcemap: true,
    external: ["@grpc/grpc-js", "google-protobuf", "winston"],
});
