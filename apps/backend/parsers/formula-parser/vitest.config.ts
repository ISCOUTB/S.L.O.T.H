import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        include: ["tests/**/*.test.ts"],
        exclude: ["./dist/**"],
        coverage: {
            provider: "v8",
            reportsDirectory: "./coverage",
            reporter: ["text", "html", "lcov", "cobertura"],
        },
    },
});
