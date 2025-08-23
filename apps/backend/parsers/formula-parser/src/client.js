var messages = require('./clients/formula_parser_pb');
var services = require('./clients/formula_parser_grpc_pb');
var grpc = require('@grpc/grpc-js');

var client = new services.FormulaParserClient('localhost:50052', grpc.credentials.createInsecure());


function runParseFormula() {
    function parseFormulaCallback(error, response) {
        if (error) {
            console.error('Error:', error);
        } else {
            console.log(`Formula: ${response.getFormula()}`);
            console.log(`Tokens: ${response.getTokens()}`);
            console.log(`AST: ${response.getAst()}`);
            console.log(`Error: ${response.getError()}`);
        }
    }
    const formula1 = "=A1 > B1";
    const request = new messages.FormulaParserRequest();
    request.setFormula(formula1);
    client.parseFormula(request, parseFormulaCallback);
}

if (require.main === module) {
    runParseFormula();
}
