import type { Node } from "excel-formula-ast";
import type { Token } from "excel-formula-tokenizer";
import { Effect } from "effect";
import { buildTree } from "excel-formula-ast";
import { tokenize } from "excel-formula-tokenizer";
import { BuildTreeError, TokenizeError } from "@/core/index.ts";

interface ParseFormulaReturnType {
    formula: string;
    tokens: Token[] | null;
    ast: Node | null;
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

        return { formula, tokens, ast, error: "" } as ParseFormulaReturnType;
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
