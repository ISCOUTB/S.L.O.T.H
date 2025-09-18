import { formula_parser } from "@etl-design/packages-proto-utils-js";
import { credentials } from "@grpc/grpc-js";

const client = new formula_parser.FormulaParserClient(
    "localhost:50052",
    credentials.createInsecure(),
);

function runParseFormula() {
    function parseFormulaCallback(error, response) {
        if (error) {
            console.error("Error:", error);
        } else {
            // console.warn(`Formula: ${response.getFormula()}`);
            // console.warn(`Tokens: ${response.getTokens()}`);
            // console.warn(`AST: ${response.getAst()}`);
            // console.warn(`Error: ${response.getError()}`);
            console.warn(response);
        }
    }
    const formula1 = "=A1 > B1";
    const request = new formula_parser.FormulaParserRequest();

    request.formula = formula1;

    client.ParseFormula(request, parseFormulaCallback);
}

runParseFormula();
