import { defineConfig } from "tsup";

export default defineConfig({
    entry: ["src/server.js"],
    outDir: "dist",
    format: ["esm", "cjs"],
    clean: true,
    dts: true,
    sourcemap: true,
    external: ["@grpc/grpc-js", "google-protobuf"],
});
