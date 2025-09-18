import { Data } from "effect";

export class BindPortError extends Data.TaggedError("BindPortError")<{ error: Error }> {}
