// tests/utils/proto-utils.test.ts
import { dtypes } from "@etl-design/packages-proto-utils-js";
import { Effect } from "effect";
import { describe, expect, it } from "vitest";
import { getAstTypeEnum, getRefTypeEnum } from "@/utils/proto-utils.ts";

describe("getAstTypeEnum", () => {
    it("should return AST_FUNCTION for function type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("function"));

        expect(result).toBe(dtypes.AstType.AST_FUNCTION);
    });

    it("should return AST_CELL for cell type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("cell"));

        expect(result).toBe(dtypes.AstType.AST_CELL);
    });

    it("should return AST_NUMBER for number type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("number"));

        expect(result).toBe(dtypes.AstType.AST_NUMBER);
    });

    it("should return AST_LOGICAL for logical type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("logical"));

        expect(result).toBe(dtypes.AstType.AST_LOGICAL);
    });

    it("should return AST_TEXT for text type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("text"));

        expect(result).toBe(dtypes.AstType.AST_TEXT);
    });

    it("should return AST_BINARY_EXPRESSION for binary-expression type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("binary-expression"));

        expect(result).toBe(dtypes.AstType.AST_BINARY_EXPRESSION);
    });

    it("should return AST_CELL_RANGE for cell-range type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("cell-range"));

        expect(result).toBe(dtypes.AstType.AST_CELL_RANGE);
    });

    it("should return AST_UNARY_EXPRESSION for unary-expression type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("unary-expression"));

        expect(result).toBe(dtypes.AstType.AST_UNARY_EXPRESSION);
    });

    it("should return AST_UNKNOWN for unknown type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum("unknown" as any));

        expect(result).toBe(dtypes.AstType.AST_UNKNOWN);
    });

    it("should return AST_UNKNOWN for undefined type", async () => {
        const result = await Effect.runPromise(getAstTypeEnum(undefined as any));

        expect(result).toBe(dtypes.AstType.AST_UNKNOWN);
    });
});

describe("getRefTypeEnum", () => {
    it("should return REF_RELATIVE for relative type", async () => {
        const result = await Effect.runPromise(getRefTypeEnum("relative"));

        expect(result).toBe(dtypes.RefType.REF_RELATIVE);
    });

    it("should return REF_ABSOLUTE for absolute type", async () => {
        const result = await Effect.runPromise(getRefTypeEnum("absolute"));

        expect(result).toBe(dtypes.RefType.REF_ABSOLUTE);
    });

    it("should return REF_MIXED for mixed type", async () => {
        const result = await Effect.runPromise(getRefTypeEnum("mixed"));

        expect(result).toBe(dtypes.RefType.REF_MIXED);
    });

    it("should return REF_UNKNOWN for unknown type", async () => {
        const result = await Effect.runPromise(getRefTypeEnum("unknown" as any));

        expect(result).toBe(dtypes.RefType.REF_UNKNOWN);
    });

    it("should return REF_UNKNOWN for undefined type", async () => {
        const result = await Effect.runPromise(getRefTypeEnum(undefined as any));

        expect(result).toBe(dtypes.RefType.REF_UNKNOWN);
    });

    it("should return REF_UNKNOWN for null type", async () => {
        const result = await Effect.runPromise(getRefTypeEnum(null as any));

        expect(result).toBe(dtypes.RefType.REF_UNKNOWN);
    });
});

describe("proto-utils integration", () => {
    it("should handle all AST types correctly", async () => {
        const types = [
            "function",
            "cell",
            "number",
            "logical",
            "text",
            "binary-expression",
            "cell-range",
            "unary-expression",
        ] as const;

        const results = await Promise.all(
            types.map((type) => Effect.runPromise(getAstTypeEnum(type))),
        );

        const uniqueResults = new Set(results);
        expect(uniqueResults.size).toBe(types.length);

        results.forEach((result) => {
            expect(result).not.toBe(dtypes.AstType.AST_UNKNOWN);
        });
    });

    it("should handle all RefType types correctly", async () => {
        const refTypes = ["relative", "absolute", "mixed"] as const;

        const results = await Promise.all(
            refTypes.map((type) => Effect.runPromise(getRefTypeEnum(type))),
        );

        const uniqueResults = new Set(results);
        expect(uniqueResults.size).toBe(refTypes.length);

        results.forEach((result) => {
            expect(result).not.toBe(dtypes.RefType.REF_UNKNOWN);
        });
    });

    it("should return Effect that can be composed", async () => {
        const program = Effect.gen(function* () {
            const astType = yield* getAstTypeEnum("cell");
            const refType = yield* getRefTypeEnum("relative");

            return { astType, refType };
        });

        const result = await Effect.runPromise(program);

        expect(result.astType).toBe(dtypes.AstType.AST_CELL);
        expect(result.refType).toBe(dtypes.RefType.REF_RELATIVE);
    });
});
