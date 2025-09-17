import process from "node:process";
import { z } from "zod";

const EnvSchema = z.object({
    FORMULA_PARSER_HOST: z.string().default("localhost"),
    FORMULA_PARSER_PORT: z.coerce.number().default(50052),
    DEBUG_FORMULA_PARSER: z
        .string()
        .transform((value) => value.toLowerCase() === "true")
        .default(false),
});

export const settings = EnvSchema.parse(process.env);

declare global {
    // eslint-disable-next-line ts/no-namespace
    namespace NodeJS {
        interface ProcessEnv extends z.infer<typeof EnvSchema> {}
    }
}
