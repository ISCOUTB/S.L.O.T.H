import {
    requestDeserialize,
    requestSerialize,
    responseDeserialize,
    responseSerialize,
} from "@etl-design/packages-proto-utils-js";
import { Server, ServerCredentials } from "@grpc/grpc-js";
import { settings } from "@/core/config";
import { handler } from "@/handlers/handler";
import { logger } from "@/utils";

function parseFormula(call: any, callback: any) {
    callback(null, handler(call.request.getFormula()));
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

    const { FORMULA_PARSER_HOST, FORMULA_PARSER_PORT, DEBUG_FORMULA_PARSER } =
        settings;

    server.bindAsync(
        `${FORMULA_PARSER_HOST}:${FORMULA_PARSER_PORT}`,
        ServerCredentials.createInsecure(),
        (error, port) => {
            if (error) {
                logger.error(`failed to bind server: ${error}`);
                return;
            }

            logger.info(
                `formula-parser service on ${FORMULA_PARSER_HOST}:${port} | Debug: ${DEBUG_FORMULA_PARSER}`,
            );
        },
    );
}

main();
