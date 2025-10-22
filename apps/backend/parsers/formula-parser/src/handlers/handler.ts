import { formula_parser } from "@etl-design/packages-proto-utils-js";
import { Effect } from "effect";
import { settings } from "@/core/";
import { parseFormula } from "@/services/parse";
import { Convert, logger } from "@/utils/";

export function handler(formula: string) {
    return Effect.gen(function* () {
        const response = new formula_parser.FormulaParserResponse();

        const { tokens, ast, error } = yield* parseFormula(formula);

        const { DEBUG_FORMULA_PARSER } = yield* settings;

        if (DEBUG_FORMULA_PARSER) {
            logger.debug(`received formula: ${formula}`);
            logger.debug(`AST: ${JSON.stringify(ast, null, 2)}`);
        }

        response.formula = formula;

        if (error || !tokens || !ast) {
            response.error = error;
            return response;
        }

        if (tokens) {
            response.tokens = yield* Convert.TokensToProto(tokens);
        }

        if (ast) {
            response.ast = yield* Convert.AstToProto(ast);
        }

        response.error = "";
        return response;
    });
}
