const { tokenize } = require("excel-formula-tokenizer");
const { buildTree } = require("excel-formula-ast");

function parseFormula(formula) {
    let tokens = null, ast = null;

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

module.exports.parseFormula = parseFormula;
