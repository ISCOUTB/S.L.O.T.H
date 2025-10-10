import { Effect, Exit } from "effect";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { settings } from "@/core/config.ts";

describe("settings", () => {
    const originalEnv = process.env;

    beforeEach(() => {
        process.env = { ...originalEnv };
    });

    afterEach(() => {
        process.env = originalEnv;
    });

    it("should parse valid environment variables", () => {
        process.env = {
            ...originalEnv,
            FORMULA_PARSER_HOST: "test-host",
            FORMULA_PARSER_PORT: "3000",
            DEBUG_FORMULA_PARSER: "true",
        };

        const { FORMULA_PARSER_HOST, FORMULA_PARSER_PORT, DEBUG_FORMULA_PARSER } =
            Effect.runSync(settings);

        expect(FORMULA_PARSER_HOST).toBe("test-host");
        expect(FORMULA_PARSER_PORT).toBe(3000);
        expect(DEBUG_FORMULA_PARSER).toBe(true);
    });

    it("should use default values when env vars are missing", () => {
        process.env = {};

        const { FORMULA_PARSER_HOST, FORMULA_PARSER_PORT, DEBUG_FORMULA_PARSER } =
            Effect.runSync(settings);

        expect(FORMULA_PARSER_HOST).toBe("localhost");
        expect(FORMULA_PARSER_PORT).toBe(50052);
        expect(DEBUG_FORMULA_PARSER).toBe(false);
    });

    it("should fail with EnvParseError when port is invalid", () => {
        process.env = {
            ...originalEnv,
            FORMULA_PARSER_PORT: "not-a-number",
        };

        const exit = Effect.runSyncExit(settings);

        expect(Exit.isFailure(exit)).toBe(true);

        if (Exit.isFailure(exit)) {
            const cause = exit.cause;
            expect(cause._tag).toBe("Fail");
            if (cause._tag === "Fail") {
                expect(cause.error._tag).toBe("EnvParseError");
            }
        }
    });

    it("should fail with EnvParseError when port is out of range", () => {
        process.env = {
            ...originalEnv,
            FORMULA_PARSER_PORT: "99999",
        };

        const exit = Effect.runSyncExit(settings);

        expect(Exit.isFailure(exit)).toBe(true);

        if (Exit.isFailure(exit)) {
            const cause = exit.cause;
            expect(cause._tag).toBe("Fail");
            if (cause._tag === "Fail") {
                expect(cause.error._tag).toBe("EnvParseError");
            }
        }
    });

    it("should handle invalid boolean for DEBUG by defaulting to false", () => {
        process.env = {
            ...originalEnv,
            DEBUG_FORMULA_PARSER: "invalid-boolean",
        };

        const exit = Effect.runSyncExit(settings);

        expect(Exit.isFailure(exit)).toBe(true);
    });

    it("should parse when DEBUG_FORMULA_PARSER is 'true'", () => {
        process.env = {
            ...originalEnv,
            DEBUG_FORMULA_PARSER: "true",
        };

        const { DEBUG_FORMULA_PARSER } = Effect.runSync(settings);

        expect(DEBUG_FORMULA_PARSER).toBe(true);
    });

    it("should parse when DEBUG_FORMULA_PARSER is 'false'", () => {
        process.env = {
            ...originalEnv,
            DEBUG_FORMULA_PARSER: "false",
        };

        const { DEBUG_FORMULA_PARSER } = Effect.runSync(settings);

        expect(DEBUG_FORMULA_PARSER).toBe(false);
    });

    it("should parse when DEBUG_FORMULA_PARSER is 'TRUE' (case insensitive)", () => {
        process.env = {
            ...originalEnv,
            DEBUG_FORMULA_PARSER: "TRUE",
        };

        const { DEBUG_FORMULA_PARSER } = Effect.runSync(settings);

        expect(DEBUG_FORMULA_PARSER).toBe(true);
    });
});
