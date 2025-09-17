import { buildTree } from "excel-formula-ast";
import { tokenize } from "excel-formula-tokenizer";

export function parseFormula(formula: string) {
    let tokens = null;
    let ast = null;

    try {
        tokens = tokenize(formula);
    } catch (e) {
        return {
            formula,
            tokens,
            ast,
            error: `Could not tokenise: ${e}`,
        };
    }

    try {
        ast = buildTree(tokens);
    } catch (e) {
        return {
            formula,
            tokens,
            ast,
            error: `Could not build tree: ${e}`,
        };
    }

    return { formula, tokens, ast, error: "" };
}

export default parseFormula;
