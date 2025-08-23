var grpc = require('@grpc/grpc-js');
const { settings } = require('./core/config');
var services = require('./clients/formula_parser_grpc_pb');
var { parseFormulaHandler } = require('./handlers/formulaParserHandler');


function parseFormula(call, callback) {
    callback(null, parseFormulaHandler(call.request.getFormula()));
}


function getServer() {
    var server = new grpc.Server();
    server.addService(services.FormulaParserService, {
        parseFormula: parseFormula
    });
    return server;
}


if (require.main === module) {
    var routeServer = getServer();
    const { host, port, debug } = settings;

    routeServer.bindAsync(`${host}:${port}`, grpc.ServerCredentials.createInsecure(), (err, port) => {
        if (err) {
            console.error('Failed to bind server:', err);
            return;
        }
        console.log(`Formula Parser Server on ${host}:${port} -- DEBUG: ${debug}`);
    });
}
