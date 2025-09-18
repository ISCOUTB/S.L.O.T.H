import {
    requestDeserialize,
    requestSerialize,
    responseDeserialize,
    responseSerialize,
} from "@etl-design/packages-proto-utils-js";
import { Server, ServerCredentials } from "@grpc/grpc-js";
import { Effect } from "effect";
import { BindPortError, settings } from "./core/index.js";
import { handler } from "./handlers/handler.js";
import { logger } from "./utils/index.js";

function parseFormula(call: any, callback: any) {
    callback(null, handler(call.request.getFormula()));
}

function getServer() {
    return Effect.sync(() => {
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
    });
}

function main() {
    return Effect.gen(function* () {
        const server = yield* getServer();
        const { FORMULA_PARSER_HOST, FORMULA_PARSER_PORT, DEBUG_FORMULA_PARSER } = settings;

        yield* Effect.async<void, BindPortError>((resume) => {
            server.bindAsync(
                `${FORMULA_PARSER_HOST}:${FORMULA_PARSER_PORT}`,
                ServerCredentials.createInsecure(),
                (error, port) => {
                    if (error) {
                        logger.error(`failed to bind server: ${error}`);
                        resume(Effect.fail(new BindPortError({ error })));
                        return;
                    }

                    logger.info(`formula-parser service on ${FORMULA_PARSER_HOST}:${port}`);
                    logger.info(`Debug: ${DEBUG_FORMULA_PARSER}`);
                    resume(Effect.void);
                },
            );
        });
    });
}

Effect.runPromise(
    main().pipe(
        Effect.catchTag("BindPortError", (error) => {
            logger.crit(`[main] port binding failed: ${error.error.message}`);
            return Effect.void;
        }),
    ),
);
