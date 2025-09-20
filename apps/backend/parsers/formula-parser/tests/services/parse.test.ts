import { Effect } from "effect";
import { isEqual } from "lodash";
import { describe, expect, it } from "vitest";
import { parseFormula } from "../../src/services/parse.ts";

describe("parseFormula", () => {
    it("should parse a simple formula", () => {
        const rawFormula = "=A1+B1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);

        expect(
            isEqual(tokens, [
                { value: "A1", type: "operand", subtype: "range" },
                { value: "+", type: "operator-infix", subtype: "math" },
                { value: "B1", type: "operand", subtype: "range" },
            ]),
        ).toBe(true);

        expect(
            isEqual(ast, {
                type: "binary-expression",
                operator: "+",
                left: { type: "cell", refType: "relative", key: "A1" },
                right: { type: "cell", refType: "relative", key: "B1" },
            }),
        ).toBe(true);

        expect(error.length).toBe(0);
    });
});
