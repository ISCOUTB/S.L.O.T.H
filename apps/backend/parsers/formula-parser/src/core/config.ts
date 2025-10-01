import process from "node:process";
import { Data, Effect } from "effect";
import { z } from "zod";
import { logger } from "@/utils/logger.ts";

export class EnvParseError extends Data.TaggedError("EnvParseError")<{ error: z.ZodError }> {}

const EnvSchema = z.object({
    FORMULA_PARSER_HOST: z.string().default("localhost"),
    FORMULA_PARSER_PORT: z.coerce.number().default(50052),
    DEBUG_FORMULA_PARSER: z
        .string()
        .transform((value) => value.toLowerCase() === "true")
        .default(false),
});

export const settings = Effect.try({
    try: () => EnvSchema.parse(process.env),
    catch: (error) => new EnvParseError({ error: error as z.ZodError }),
}).pipe(
    // eslint-disable-next-line antfu/consistent-list-newline
    Effect.catchTag("EnvParseError", (error) =>
        Effect.sync(() => {
            logger.crit(`[settings] failed to parse .env variables: ${error}`);
            process.exit(1);
        }),
    ),
);

declare global {
    // eslint-disable-next-line ts/no-namespace
    namespace NodeJS {
        interface ProcessEnv extends z.infer<typeof EnvSchema> {}
    }
}
