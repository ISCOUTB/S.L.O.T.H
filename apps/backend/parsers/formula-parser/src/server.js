const grpc = require("@grpc/grpc-js");
const services = require("./clients/formula_parser_grpc_pb");
const { settings } = require("./core/config");
const { parseFormulaHandler } = require("./handlers/formulaParserHandler");

function parseFormula(call, callback) {
    callback(null, parseFormulaHandler(call.request.getFormula()));
}

function getServer() {
    const server = new grpc.Server();
    server.addService(services.FormulaParserService, {
        parseFormula,
    });
    return server;
}

if (require.main === module) {
    const routeServer = getServer();
    const { host, port, debug } = settings;
    routeServer.bindAsync(
        `${host}:${port}`,
        grpc.ServerCredentials.createInsecure(),
        (err, port) => {
            if (err) {
                console.error("Failed to bind server:", err);
                return;
            }
            console.warn(
                `Formula Parser Server on ${host}:${port} -- DEBUG: ${debug}`,
            );
        },
    );
}
