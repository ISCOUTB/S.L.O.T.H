import { Effect } from "effect";
import { isEqual } from "lodash";
import { describe, expect, it } from "vitest";
import { parseFormula } from "@/services/parse";

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

describe("parseFormula - sheet references and advanced cases", () => {
    it("should parse formulas with sheet references", () => {
        const rawFormula = "Sheet1!A1+Sheet2!B2";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(tokens!.some((token) => token.value === "Sheet1!A1")).toBe(true);
        expect(tokens!.some((token) => token.value === "Sheet2!B2")).toBe(true);
        expect(ast).toBeDefined();
    });

    it("should parse formula with mixed sheet and cell references", () => {
        const rawFormula = "=A1+Sheet3!C5";

        const { formula, tokens, ast, error } = Effect.runSync(parseFormula(rawFormula));

        expect(formula).toBe(rawFormula);
        expect(error.length).toBe(0);
        expect(tokens).toBeDefined();
        expect(tokens!.some((t) => t.value === "A1")).toBe(true);
        expect(tokens!.some((t) => t.value === "Sheet3!C5")).toBe(true);
        expect(ast).toBeDefined();
    });

    it("should parse formula with sheet reference and absolute cell", () => {
        const rawFormula = "=Sheet1!$A$1+Sheet2!B2";
        const { ast } = Effect.runSync(parseFormula(rawFormula));

        expect(ast).toBeDefined();

        if (!ast || ast.type !== "binary-expression") {
            throw new Error("expected ast.type to be of type 'binary-expression'");
        }

        expect(ast.left.type).toBe("reference-node");
        if (ast.left.type !== "reference-node") {
            throw new Error("expected ast.left.type to be of type 'reference-node'");
        }
        expect(ast.left.sheetName).toBe("Sheet1");
        expect(ast.left.key).toBe("$A$1");
        expect(ast.left.refType).toBe("absolute");
        expect(ast.right.type).toBe("reference-node");

        if (ast.right.type !== "reference-node") {
            throw new Error("expected ast.right.type to be of type 'reference-node'");
        }
        expect(ast.right.sheetName).toBe("Sheet2");
        expect(ast.right.key).toBe("B2");
        expect(ast.right.refType).toBe("relative");
    });

    it("should parse formula with sheet reference and mixed cell", () => {
        const rawFormula = "=Sheet1!$A1+Sheet2!B$2";
        const { ast } = Effect.runSync(parseFormula(rawFormula));

        expect(ast).toBeDefined();

        if (!ast || ast.type !== "binary-expression") {
            throw new Error("expected ast.type to be of type 'binary-expression'");
        }

        expect(ast.left.type).toBe("reference-node");
        if (ast.left.type !== "reference-node") {
            throw new Error("expected ast.left.type to be of type 'reference-node'");
        }

        expect(ast.right.type).toBe("reference-node");
        if (ast.right.type !== "reference-node") {
            throw new Error("expected ast.right.type to be of type 'reference-node'");
        }

        expect(ast.left.sheetName).toBe("Sheet1");
        expect(ast.left.key).toBe("$A1");
        expect(ast.left.refType).toBe("mixed");

        expect(ast.right.sheetName).toBe("Sheet2");
        expect(ast.right.key).toBe("B$2");
        expect(ast.right.refType).toBe("mixed");
    });

    it("should parse formula with sheet reference in a function argument", () => {
        const rawFormula = "SUM(Sheet1!A1,Sheet2!B2)";
        const { ast } = Effect.runSync(parseFormula(rawFormula));

        expect(ast).toBeDefined();
        if (!ast || ast.type !== "function") {
            throw new Error("expected ast.type to be of type 'function'");
        }

        expect(ast.type).toBe("function");

        expect(ast.arguments[0]?.type).toBe("reference-node");
        expect(ast.arguments[1]?.type).toBe("reference-node");

        if (
            ast.arguments[0]?.type !== "reference-node" ||
            ast.arguments[1]?.type !== "reference-node"
        ) {
            throw new Error("expected both arguments to be of type 'reference-node'");
        }

        expect(ast.arguments[0].sheetName).toBe("Sheet1");
        expect(ast.arguments[0].key).toBe("A1");
        expect(ast.arguments[1].sheetName).toBe("Sheet2");
        expect(ast.arguments[1].key).toBe("B2");
    });

    it("should parse formula with sheet reference in a cell range", () => {
        const rawFormula = "SUM(Sheet1!A1:Sheet1!A10)";
        const { ast } = Effect.runSync(parseFormula(rawFormula));

        expect(ast).toBeDefined();
        if (!ast || ast.type !== "function") {
            throw new Error("expected ast.type to be of type 'function'");
        }

        expect(ast.type).toBe("function");

        const range = ast.arguments[0];
        if (!range || range.type !== "cell-range") {
            throw new Error("expected range.type to be of type 'cell-range'");
        }
        expect(range.type).toBe("cell-range");

        if (range.left.type !== "reference-node" || range.right.type !== "reference-node") {
            throw new Error("expected both nodes to be of type 'reference-node'");
        }
        expect(range.left.type).toBe("reference-node");
        expect(range.right.type).toBe("reference-node");

        expect(range.left.sheetName).toBe("Sheet1");
        expect(range.left.key).toBe("A1");
        expect(range.right.sheetName).toBe("Sheet1");
        expect(range.right.key).toBe("A10");
    });

    it("should parse formula with sheet reference and unary minus", () => {
        const rawFormula = "=-Sheet1!A1";
        const { ast } = Effect.runSync(parseFormula(rawFormula));

        expect(ast).toBeDefined();
        if (!ast || ast.type !== "unary-expression") {
            throw new Error("expected ast.type to be of type 'unary-expression'");
        }
        expect(ast.type).toBe("unary-expression");

        expect(ast.operand.type).toBe("reference-node");
        if (ast.operand.type !== "reference-node") {
            throw new Error("expected ast.operand.type to be of type 'reference-node'");
        }

        expect(ast.operand.sheetName).toBe("Sheet1");
        expect(ast.operand.key).toBe("A1");
    });

    it("should parse formula with multiple sheet references in range", () => {
        const rawFormula = "=SUM(Sheet1!A1:Sheet2!B2)";

        const { ast } = Effect.runSync(parseFormula(rawFormula));

        expect(ast).toBeDefined();
        if (!ast || ast.type !== "function") {
            throw new Error("expected ast.type to be of type 'function'");
        }
        expect(ast.type).toBe("function");

        const range = ast.arguments[0];
        if (!range || range.type !== "cell-range") {
            throw new Error("expected range.type to be of type 'cell-range'");
        }
        expect(range.type).toBe("cell-range");

        expect(range.left.type).toBe("reference-node");
        if (range.left.type !== "reference-node") {
            throw new Error("expected range.left.type to be of type 'reference-node'");
        }
        expect(range.left.sheetName).toBe("Sheet1");
        expect(range.left.key).toBe("A1");

        expect(range.right.type).toBe("reference-node");
        if (range.right.type !== "reference-node") {
            throw new Error("expected range.right.type to be of type 'reference-node'");
        }
        expect(range.right.sheetName).toBe("Sheet2");
        expect(range.right.key).toBe("B2");
    });
});
