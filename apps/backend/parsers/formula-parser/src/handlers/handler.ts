import { formula_parser } from "@etl-design/packages-proto-utils-js";
import { settings } from "@/core/config";
import { parseFormula } from "@/services/parse";
import { Convert, logger } from "@/utils";

export function handler(formula: string) {
    const response = new formula_parser.FormulaParserResponse();
    const { tokens, ast, error } = parseFormula(formula);

    if (settings.DEBUG_FORMULA_PARSER) {
        logger.info(`received formula: ${formula}`);
        logger.info(`AST: ${JSON.stringify(ast, null, 2)}`);
    }

    response.formula = formula;

    if (error || !tokens || !ast) {
        response.error = error;
        return response;
    }

    if (tokens) {
        response.tokens = Convert.TokensToProto(tokens);
    }

    if (ast) {
        response.ast = Convert.AstToProto(ast);
    }

    response.error = "";
    return response;
}
