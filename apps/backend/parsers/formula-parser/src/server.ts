import type { formula_parser } from "@etl-design/packages-proto-utils-js";
import type { sendUnaryData, ServerUnaryCall } from "@grpc/grpc-js";
import process from "node:process";
import {
    requestDeserialize,
    requestSerialize,
    responseDeserialize,
    responseSerialize,
} from "@etl-design/packages-proto-utils-js";
import { Server, ServerCredentials } from "@grpc/grpc-js";
import { Effect } from "effect";
import { BindPortError, settings } from "@/core/";
import { handler } from "@/handlers/handler";
import { logger } from "@/utils/index.ts";

export function parseFormula(
    call: ServerUnaryCall<
        formula_parser.FormulaParserRequest,
        formula_parser.FormulaParserResponse
    >,
    callback: sendUnaryData<formula_parser.FormulaParserResponse>,
) {
    Effect.runPromise(handler(call.request.formula))
        .then((response) => callback(null, response))
        .catch((error) => {
            logger.error(`[parseFormula] failed to handle formula: ${error}`);
            callback(error, null);
        });
}

export function getServer() {
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

        const { FORMULA_PARSER_HOST, FORMULA_PARSER_PORT, DEBUG_FORMULA_PARSER } =
            yield* settings.pipe(
                // eslint-disable-next-line antfu/consistent-list-newline
                Effect.catchTag("EnvParseError", (error) =>
                    Effect.gen(function* () {
                        yield* Effect.sync(() => {
                            logger.crit(`[server] failed to parse .env variables: ${error.error}`);
                            process.exit(1);
                        });

                        return yield* Effect.die("Failed to parse environment");
                    }),
                ),
            );

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
