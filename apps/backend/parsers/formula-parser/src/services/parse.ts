import type { Token } from "excel-formula-tokenizer";
import { Effect } from "effect";
import { buildTree } from "excel-formula-ast";
import { tokenize } from "excel-formula-tokenizer";
import { BuildTreeError, TokenizeError } from "@/core/";
import { extendAst } from "@/utils/";

interface ParseFormulaReturnType {
    formula: string;
    tokens: Token[] | null;
    ast: Ast.Node | null;
    error: string;
}

export function parseFormula(formula: string) {
    return Effect.gen(function* () {
        const tokens = yield* Effect.try({
            try: () => tokenize(formula),
            catch: (error) => new TokenizeError({ error }),
        });

        const ast = yield* Effect.try({
            try: () => buildTree(tokens),
            catch: (error) => new BuildTreeError({ error }),
        });

        const extendedAst = extendAst(ast as Ast.Node);

        return { formula, tokens, ast: extendedAst, error: "" } satisfies ParseFormulaReturnType;
    }).pipe(
        Effect.catchTags({
            BuildTreeError: (error) =>
                Effect.succeed<ParseFormulaReturnType>({
                    formula,
                    tokens: null,
                    ast: null,
                    error: `tokenization failed: ${error.error}`,
                }),
            TokenizeError: (error) =>
                Effect.succeed<ParseFormulaReturnType>({
                    formula,
                    tokens: null,
                    ast: null,
                    error: `tree building failed: ${error.error}`,
                }),
        }),
    );
}

export default parseFormula;
