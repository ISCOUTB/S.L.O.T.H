import type { Node } from "excel-formula-ast";
import { dtypes } from "@etl-design/packages-proto-utils-js";
import { Effect } from "effect";
import { describe, expect, it, vi } from "vitest";

// Mock del logger
vi.mock("@/utils/index.ts", async () => {
    const actual = await vi.importActual("@/utils/index.ts");
    return {
        ...actual,
        logger: {
            info: vi.fn(),
            error: vi.fn(),
            warn: vi.fn(),
            debug: vi.fn(),
        },
    };
});

describe("convert.TokensToProto", () => {
    it("should convert tokens array to proto Tokens", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const tokens = [
            { value: "A1", type: "operand", subtype: "range" },
            { value: "+", type: "operator-infix", subtype: "math" },
            { value: "B1", type: "operand", subtype: "range" },
        ];

        const result = await Effect.runPromise(Convert.TokensToProto(tokens));

        expect(result).toBeInstanceOf(dtypes.Tokens);
        expect(result.tokens).toHaveLength(3);
        expect(result.tokens?.[0]?.value).toBe("A1");
        expect(result.tokens?.[0]?.type).toBe("operand");
        expect(result.tokens?.[0]?.subtype).toBe("range");
        expect(result.tokens?.[1]?.value).toBe("+");
        expect(result.tokens?.[1]?.type).toBe("operator-infix");
        expect(result.tokens?.[2]?.value).toBe("B1");
    });

    it("should handle empty tokens array", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const tokens: any[] = [];

        const result = await Effect.runPromise(Convert.TokensToProto(tokens));

        expect(result).toBeInstanceOf(dtypes.Tokens);
        expect(result.tokens).toHaveLength(0);
    });

    it("should handle tokens with all subtypes", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const tokens = [
            { value: "SUM", type: "function", subtype: "start" },
            { value: "(", type: "subexpression", subtype: "start" },
            { value: "A1:A10", type: "operand", subtype: "range" },
            { value: ")", type: "subexpression", subtype: "stop" },
        ];

        const result = await Effect.runPromise(Convert.TokensToProto(tokens));

        expect(result).toBeInstanceOf(dtypes.Tokens);
        expect(result.tokens).toHaveLength(4);
        expect(result.tokens?.[0]?.type).toBe("function");
        expect(result.tokens?.[0]?.subtype).toBe("start");
        expect(result.tokens?.[1]?.type).toBe("subexpression");
        expect(result.tokens?.[2]?.subtype).toBe("range");
    });

    it("should preserve token values exactly", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const tokens = [
            { value: "123.456", type: "operand", subtype: "number" },
            { value: "'hello'", type: "operand", subtype: "text" },
            { value: "TRUE", type: "operand", subtype: "logical" },
        ];

        const result = await Effect.runPromise(Convert.TokensToProto(tokens));

        expect(result.tokens?.[0]?.value).toBe("123.456");
        expect(result.tokens?.[1]?.value).toBe("'hello'");
        expect(result.tokens?.[2]?.value).toBe("TRUE");
    });
});

describe("convert.AstToProto", () => {
    it("should convert cell node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "cell" as const,
            key: "A1",
            refType: "relative" as const,
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_CELL);
        expect(result.key).toBe("A1");
        expect(result.refType).toBe(dtypes.RefType.REF_RELATIVE);
    });

    it("should convert number node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "number" as const,
            value: 42,
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_NUMBER);
        expect(result.number_value).toBe(42);
    });

    it("should convert text node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "text" as const,
            value: "Hello World",
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_TEXT);
        expect(result.text_value).toBe("Hello World");
    });

    it("should convert logical node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "logical" as const,
            value: true,
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_LOGICAL);
        expect(result.logical_value).toBe(true);
    });

    it("should convert binary-expression node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "binary-expression" as const,
            operator: "+",
            left: { type: "cell" as const, key: "A1", refType: "relative" as const },
            right: { type: "number" as const, value: 10 },
        } satisfies Node;

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_BINARY_EXPRESSION);
        expect(result.operator).toBe("+");
        expect(result.left).toBeDefined();
        expect(result.right).toBeDefined();
        expect(result.left?.type).toBe(dtypes.AstType.AST_CELL);
        expect(result.right?.type).toBe(dtypes.AstType.AST_NUMBER);
    });

    it("should convert unary-expression node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "unary-expression" as const,
            operator: "-",
            operand: { type: "number" as const, value: 5 },
        } satisfies Node;

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_UNARY_EXPRESSION);
        expect(result.operator).toBe("-");
        expect(result.operand).toBeDefined();
        expect(result.operand?.type).toBe(dtypes.AstType.AST_NUMBER);
    });

    it("should convert function node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "function" as const,
            name: "SUM",
            arguments: [
                {
                    type: "cell-range" as const,
                    left: { type: "cell" as const, key: "A1", refType: "relative" as const },
                    right: { type: "cell" as const, key: "A10", refType: "relative" as const },
                },
            ],
        } satisfies Node;

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_FUNCTION);
        expect(result.name).toBe("SUM");
        expect(result.arguments).toHaveLength(1);
        expect(result.arguments?.[0]?.type).toBe(dtypes.AstType.AST_CELL_RANGE);
    });

    it("should convert cell-range node to proto AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "cell-range" as const,
            left: { type: "cell" as const, key: "A1", refType: "relative" as const },
            right: { type: "cell" as const, key: "A10", refType: "relative" as const },
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_CELL_RANGE);
        expect(result.left).toBeDefined();
        expect(result.right).toBeDefined();
        expect(result.left?.key).toBe("A1");
        expect(result.right?.key).toBe("A10");
    });

    it("should handle complex nested AST", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "binary-expression" as const,
            operator: "+",
            left: {
                type: "function" as const,
                name: "SUM",
                arguments: [
                    {
                        type: "cell-range" as const,
                        left: { type: "cell" as const, key: "A1", refType: "relative" as const },
                        right: { type: "cell" as const, key: "A10", refType: "relative" as const },
                    },
                ],
            },
            right: { type: "number" as const, value: 2 },
        } satisfies Node;

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_BINARY_EXPRESSION);
        expect(result.left?.type).toBe(dtypes.AstType.AST_FUNCTION);
        expect(result.left?.name).toBe("SUM");
        expect(result.right?.type).toBe(dtypes.AstType.AST_NUMBER);
        expect(result.right?.number_value).toBe(2);
    });

    it("should handle function with multiple arguments", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "function" as const,
            name: "IF",
            arguments: [
                {
                    type: "binary-expression" as const,
                    operator: ">",
                    left: { type: "cell" as const, key: "A1", refType: "relative" as const },
                    right: { type: "number" as const, value: 10 },
                },
                { type: "text" as const, value: "Yes" },
                { type: "text" as const, value: "No" },
            ],
        } satisfies Node;

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(result.type).toBe(dtypes.AstType.AST_FUNCTION);
        expect(result.name).toBe("IF");
        expect(result.arguments).toHaveLength(3);
        expect(result.arguments?.[0]?.type).toBe(dtypes.AstType.AST_BINARY_EXPRESSION);
        expect(result.arguments?.[1]?.type).toBe(dtypes.AstType.AST_TEXT);
        expect(result.arguments?.[2]?.type).toBe(dtypes.AstType.AST_TEXT);
    });

    it("should warn on unknown AST type", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");
        const { logger } = await import("@/utils/index.ts");

        const ast = {
            type: "unknown-type" as any,
        } as Node;

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result).toBeInstanceOf(dtypes.AST);
        expect(logger.warn).toHaveBeenCalledWith(
            expect.stringContaining("unknown type: unknown-type"),
        );
    });

    it("should handle different reference types", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const astRelative = {
            type: "cell" as const,
            key: "A1",
            refType: "relative" as const,
        };

        const astAbsolute = {
            type: "cell" as const,
            key: "$A$1",
            refType: "absolute" as const,
        };

        const astMixed = {
            type: "cell" as const,
            key: "$A1",
            refType: "mixed" as const,
        };

        const resultRelative = await Effect.runPromise(Convert.AstToProto(astRelative));
        const resultAbsolute = await Effect.runPromise(Convert.AstToProto(astAbsolute));
        const resultMixed = await Effect.runPromise(Convert.AstToProto(astMixed));

        expect(resultRelative.refType).toBe(dtypes.RefType.REF_RELATIVE);
        expect(resultAbsolute.refType).toBe(dtypes.RefType.REF_ABSOLUTE);
        expect(resultMixed.refType).toBe(dtypes.RefType.REF_MIXED);
    });

    it("should handle zero and negative numbers", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "number" as const,
            value: -42.5,
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result.number_value).toBe(-42.5);
    });

    it("should handle empty strings in text nodes", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "text" as const,
            value: "",
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result.text_value).toBe("");
    });

    it("should handle false in logical nodes", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        const ast = {
            type: "logical" as const,
            value: false,
        };

        const result = await Effect.runPromise(Convert.AstToProto(ast));

        expect(result.logical_value).toBe(false);
    });
});

describe("convert exports", () => {
    it("should export Convert object with TokensToProto and AstToProto", async () => {
        const { Convert } = await import("@/utils/to-proto.ts");

        expect(Convert).toBeDefined();
        expect(typeof Convert.TokensToProto).toBe("function");
        expect(typeof Convert.AstToProto).toBe("function");
    });

    it("should export as default", async () => {
        const defaultExport = await import("@/utils/to-proto.ts");

        expect(defaultExport.default).toBeDefined();
        expect(typeof defaultExport.Convert.AstToProto).toBe("function");
        expect(typeof defaultExport.Convert.TokensToProto).toBe("function");
    });
});
