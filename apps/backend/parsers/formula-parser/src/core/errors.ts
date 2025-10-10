import type { z } from "zod";
import { Data } from "effect";

export class BindPortError extends Data.TaggedError("BindPortError")<{ error: Error }> {}

export class BuildTreeError extends Data.TaggedError("BuildTreeError")<{ error: unknown }> {}

export class TokenizeError extends Data.TaggedError("TokenizeError")<{ error: unknown }> {}

export class EnvParseError extends Data.TaggedError("EnvParseError")<{ error: z.ZodError }> {}
