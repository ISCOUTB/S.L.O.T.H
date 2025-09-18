import { Data, Effect } from "effect";
import { buildTree } from "excel-formula-ast";
import { tokenize } from "excel-formula-tokenizer";

class BuildTreeError extends Data.TaggedError("BuildTreeError")<{ error: unknown }> {}

class TokenizeError extends Data.TaggedError("TokenizeError")<{ error: unknown }> {}

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

        return { formula, tokens, ast, error: "" };
    });
}

export default parseFormula;
