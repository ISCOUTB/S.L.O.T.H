import process from "node:process";
import { Effect } from "effect";
import { z } from "zod";
import { EnvParseError } from "@/core/errors";

export type Settings = z.infer<typeof EnvSchema>;

const EnvSchema = z.object({
    FORMULA_PARSER_HOST: z.string().default("localhost"),
    FORMULA_PARSER_PORT: z.coerce.number().min(1).max(65535).default(50052),
    DEBUG_FORMULA_PARSER: z
        .string()
        .refine((value) => ["true", "false"].includes(value.toLowerCase()), {
            error: "[settings] must be 'true' or 'false'",
        })
        .transform((value) => value.toLowerCase() === "true")
        .default(false),
});

export const settings: Effect.Effect<Settings, EnvParseError, never> = Effect.try({
    try: () => EnvSchema.parse(process.env),
    catch: (error) => new EnvParseError({ error: error as z.ZodError }),
});
