import {
    requestDeserialize,
    requestSerialize,
    responseDeserialize,
    responseSerialize,
} from "@etl-design/packages-proto-utils-js";
import { Server, ServerCredentials } from "@grpc/grpc-js";
import { settings } from "@/core/config";
import { parseFormulaHandler } from "@/handlers/formulaParserHandler";
import { logger } from "@/utils";

function parseFormula(call: any, callback: any) {
    callback(null, parseFormulaHandler(call.request.getFormula()));
}

function getServer() {
    const server = new Server();

    server.addService(
        {
            parseFormula: {
                path: "/formula_parser.FormulaParser/ParseFormula",
                requestStream: false,
                responseStream: false,
                requestDeserialize,
                requestSerialize,
                responseDeserialize,
                responseSerialize,
            },
        },
        { parseFormula },
    );

    return server;
}

async function main(): Promise<void> {
    const server = getServer();

    const { host, port, debug } = settings;

    server.bindAsync(
        `${host}:${port}`,
        ServerCredentials.createInsecure(),
        (error, port) => {
            if (error) {
                logger.error(`failed to bind server: ${error}`);
                return;
            }

            logger.info(
                `formula-parser service on ${host}:${port} | Debug: ${debug}`,
            );
        },
    );
}

main();
