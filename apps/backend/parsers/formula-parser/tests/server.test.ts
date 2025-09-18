import { describe, expect, it } from "vitest";

describe("environment variables", () => {
    it("should have FORMULA_PARSER_HOST defined", () => {
        const host = process.env.FORMULA_PARSER_HOST;
        expect(host).toBeDefined();
        expect(host).toBeTypeOf("string");
    });

    it("should have FORMULA_PARSER_PORT defined", () => {
        const port = process.env.FORMULA_PARSER_PORT;
        expect(port).toBeDefined();
        expect(port).toBeTypeOf("string");
    });

    it("should have DEBUG_FORMULA_PARSER defined and be a boolean", () => {
        const debug = process.env.DEBUG_FORMULA_PARSER === true;
        expect(debug).toBeDefined();
        expect(debug).toBeTypeOf("boolean");
    });
});
