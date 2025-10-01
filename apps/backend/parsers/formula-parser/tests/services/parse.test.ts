import { Effect } from "effect";
import { isEqual } from "lodash";
import { describe, expect, it } from "vitest";
import { parseFormula } from "@/services/parse.ts";

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

    it("should parse formula with multiplication", () => {
        const rawFormula = "=A1*B1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toHaveLength(3);
        expect(tokens![1]?.value).toBe("*");
        expect(ast!.type).toBe("binary-expression");
    });

    it("should parse formula with parentheses", () => {
        const rawFormula = "=(A1+B1)*C1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
        expect(ast!.type).toBe("binary-expression");
    });

    it("should parse formula with functions", () => {
        const rawFormula = "=SUM(A1:A10)";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });

    it("should parse formula with nested functions", () => {
        const rawFormula = "=SUM(A1:A10,AVERAGE(B1:B5))";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });

    it("should parse formula with numbers", () => {
        const rawFormula = "=A1+100";

        const { formula, tokens, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toHaveLength(3);
        expect(tokens![2]?.value).toBe("100");
        expect(tokens![2]?.type).toBe("operand");
    });

    it("should parse formula with strings", () => {
        const rawFormula = `=CONCATENATE("Hello", " ", "World")`;

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });

    it("should handle empty formula", () => {
        const rawFormula = "";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error).toBeTruthy();
        expect(tokens).toBeNull();
        expect(ast).toBeNull();
    });

    it("should handle formula without equals sign", () => {
        const rawFormula = "A1+B1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error).toBeFalsy();
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });

    it("should panic with invalid formula - incomplete expression", () => {
        const rawFormula = "=A1+";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error).toBeTruthy();
        expect(error).toBeTruthy();
        expect(tokens).toBeNull();
        expect(ast).toBeNull();
    });

    it("should panic with invalid formula - mismatched parentheses", () => {
        const rawFormula = "=(A1+B1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error).toBeTruthy();
        expect(tokens).toBeNull();
        expect(ast).toBeNull();
    });

    it("should handle complex formula with multiple operations", () => {
        const rawFormula = "=SUM(A1:A10)/COUNT(B1:B10)*100";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
        expect(ast!.type).toBe("binary-expression");
    });

    it("should handle formula with cell ranges", () => {
        const rawFormula = "=SUM(A1:Z100)";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });

    it("should handle formula with absolute references", () => {
        const rawFormula = "=$A$1+$B$1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });

    it("should handle formula with mixed references", () => {
        const rawFormula = "=$A1+B$1";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(ast).toBeDefined();
    });
});
