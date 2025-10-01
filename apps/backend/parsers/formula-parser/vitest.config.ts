import { resolve } from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        globals: true,
        environment: "node",
        include: ["tests/**/*.test.ts"],
        exclude: ["./dist/**"],
        coverage: {
            provider: "v8",
            reportsDirectory: "./coverage",
            reporter: ["text", "html", "lcov", "cobertura"],
        },
    },
    resolve: {
        alias: {
            "@": resolve(__dirname, "./src"),
            "@@": resolve(__dirname, "./"),
        },
    },
});
