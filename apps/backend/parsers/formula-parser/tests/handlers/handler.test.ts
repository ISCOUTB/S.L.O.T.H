import { dtypes, formula_parser } from "@etl-design/packages-proto-utils-js";
import { Effect } from "effect";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/services/parse.ts", () => ({
    parseFormula: vi.fn(),
}));

vi.mock("@/core/index.ts", () => ({
    settings: Effect.succeed({
        FORMULA_PARSER_HOST: "localhost",
        FORMULA_PARSER_PORT: 50052,
        DEBUG_FORMULA_PARSER: false,
    }),
}));

vi.mock("@/utils/index.ts", () => ({
    logger: {
        info: vi.fn(),
        error: vi.fn(),
        warn: vi.fn(),
        debug: vi.fn(),
    },
    Convert: {
        TokensToProto: vi.fn(),
        AstToProto: vi.fn(),
    },
}));

describe("parseFormula Handler", () => {
    it("should handle successful parsing", async () => {
        const { parseFormula } = await import("@/services/parse.ts");
        const { Convert } = await import("@/utils/index.ts");
        const { handler } = await import("@/handlers/handler.ts");

        vi.mocked(parseFormula).mockReturnValue(
            Effect.succeed({
                formula: "=A1+B1",
                tokens: [
                    { value: "A1", type: "operand", subtype: "range" },
                    { value: "+", type: "operator-infix", subtype: "math" },
                    { value: "B1", type: "operand", subtype: "range" },
                ],
                ast: {
                    type: "binary-expression",
                    operator: "+",
                    left: { type: "cell", refType: "relative", key: "A1" },
                    right: { type: "cell", refType: "relative", key: "B1" },
                },
                error: "",
            }),
        );

        const mockTokens = new dtypes.Tokens();
        mockTokens.tokens = [
            (() => {
                const token = new dtypes.Tokens.Token();

                token.value = "A1";
                token.type = "operand";
                token.subtype = "range";

                return token;
            })(),
        ];

        const mockAst = new dtypes.AST();
        mockAst.type = dtypes.AstType.AST_BINARY_EXPRESSION;

        vi.mocked(Convert.TokensToProto).mockReturnValue(Effect.succeed(mockTokens));
        vi.mocked(Convert.AstToProto).mockReturnValue(Effect.succeed(mockAst));

        const response = await Effect.runPromise(handler("=A1+B1"));

        expect(response).toBeInstanceOf(formula_parser.FormulaParserResponse);
        expect(response.formula).toBe("=A1+B1");
        expect(response.error).toBe("");
    });

    it("should handle parsing error", async () => {
        const { parseFormula } = await import("@/services/parse.ts");
        const { Convert } = await import("@/utils/index.ts");
        const { handler } = await import("@/handlers/handler.ts");

        vi.mocked(parseFormula).mockReturnValue(
            Effect.succeed({
                formula: "=A1+",
                tokens: null,
                ast: null,
                error: "Syntax error",
            }),
        );

        vi.mocked(Convert.TokensToProto).mockReturnValue(Effect.succeed(null as any));
        vi.mocked(Convert.AstToProto).mockReturnValue(Effect.succeed(null as any));

        const response = await Effect.runPromise(handler("=A1+"));

        expect(response).toBeInstanceOf(formula_parser.FormulaParserResponse);
        expect(response.formula).toBe("=A1+");
        expect(response.error).toBe("Syntax error");
    });

    it("should handle empty formula", async () => {
        const { parseFormula } = await import("@/services/parse.ts");
        const { Convert } = await import("@/utils/index.ts");
        const { handler } = await import("@/handlers/handler.ts");

        vi.mocked(parseFormula).mockReturnValue(
            Effect.succeed({
                formula: "",
                tokens: [],
                ast: null,
                error: "Empty formula",
            }),
        );

        const mockTokens = new dtypes.Tokens();
        mockTokens.tokens = [];

        vi.mocked(Convert.TokensToProto).mockReturnValue(Effect.succeed(mockTokens));
        vi.mocked(Convert.AstToProto).mockReturnValue(Effect.succeed(null as any));

        const response = await Effect.runPromise(handler(""));

        expect(response).toBeInstanceOf(formula_parser.FormulaParserResponse);
        expect(response.formula).toBe("");
        expect(response.error).toBe("Empty formula");
    });

    it("should log debug info when DEBUG_FORMULA_PARSER is true", async () => {
        vi.resetModules();

        const mockLogger = {
            info: vi.fn(),
            error: vi.fn(),
            warn: vi.fn(),
            debug: vi.fn(),
        };

        vi.spyOn(mockLogger, "debug");

        vi.doMock("@/core/index.ts", () => ({
            settings: Effect.succeed({
                FORMULA_PARSER_HOST: "localhost",
                FORMULA_PARSER_PORT: 50052,
                DEBUG_FORMULA_PARSER: true,
            }),
        }));

        vi.doMock("@/utils/index.ts", () => ({
            logger: mockLogger,
            Convert: {
                TokensToProto: vi.fn(),
                AstToProto: vi.fn(),
            },
        }));

        vi.doMock("@/services/parse.ts", () => ({
            parseFormula: vi.fn().mockReturnValue(
                Effect.succeed({
                    formula: "=A1+B1",
                    tokens: [{ value: "A1", type: "operand", subtype: "range" }],
                    ast: { type: "cell", refType: "relative", key: "A1" },
                    error: "",
                }),
            ),
        }));

        const { Convert } = await import("@/utils/index.ts");
        const { handler } = await import("@/handlers/handler.ts");

        const mockTokens = new dtypes.Tokens();
        mockTokens.tokens = [
            (() => {
                const token = new dtypes.Tokens.Token();
                token.value = "A1";
                token.type = "operand";
                token.subtype = "range";
                return token;
            })(),
        ];

        const mockAst = new dtypes.AST();
        mockAst.type = dtypes.AstType.AST_CELL;

        vi.mocked(Convert.TokensToProto).mockReturnValue(Effect.succeed(mockTokens));
        vi.mocked(Convert.AstToProto).mockReturnValue(Effect.succeed(mockAst));

        await Effect.runPromise(handler("=A1+B1"));

        expect(mockLogger.debug).toHaveBeenCalled();
    });
});
