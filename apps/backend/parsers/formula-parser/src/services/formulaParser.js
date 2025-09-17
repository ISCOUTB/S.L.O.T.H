const { buildTree } = require("excel-formula-ast");
const { tokenize } = require("excel-formula-tokenizer");

function parseFormula(formula) {
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

module.exports.parseFormula = parseFormula;
