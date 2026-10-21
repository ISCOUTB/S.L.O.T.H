/* eslint-disable style/indent-binary-ops */
import { ResponseCodesRecord } from "#shared/utils/response-codes";
import { z } from "zod";

function defineMessage<T extends string>(key: T): z.ZodObject<{ key: z.ZodLiteral<T> }>;
function defineMessage<T extends string, S extends z.ZodRawShape>(
    key: T,
    schema: S,
): z.ZodObject<
    {
        key: z.ZodLiteral<T>;
    } & S
>;
function defineMessage<T extends string>(key: T, schema?: z.ZodRawShape) {
    if (schema) {
        return z.object({ key: z.literal(key) }).extend(schema);
    }

    return z.object({ key: z.literal(key) });
}

export const WebSocketMessageSchema = z.discriminatedUnion("key", [
    defineMessage("ping", { userId: z.string().optional() }),
    defineMessage("pong"),
    defineMessage(ResponseCodesRecord.WebSocket.BadPayload),
    defineMessage("user-logged", { userId: z.string() }),
]);

class WebSocketMessageBuilder<
    K extends WebSocket.MessageKey,
    Collected extends Partial<WebSocket.MessageFields<K>> = Record<never, never>,
> {
    readonly #key: K;
    #fields: Collected;

    constructor(key: K, fields: Collected = {} as Collected) {
        this.#key = key;
        this.#fields = fields;
    }

    set<
        F extends Exclude<keyof WebSocket.MessageFields<K>, keyof Collected> &
            keyof WebSocket.MessageFields<K>,
    >(
        field: F,
        value: WebSocket.MessageFields<K>[F],
    ): WebSocketMessageBuilder<K, Collected & Pick<WebSocket.MessageFields<K>, F>> {
        return new WebSocketMessageBuilder(this.#key, {
            ...this.#fields,
            [field]: value,
        } as Collected & Pick<WebSocket.MessageFields<K>, F>);
    }

    get build(): WebSocket.CanBuild<K, Collected> extends true
        ? WebSocketMessage<K>
        : "Missing required fields — use .set() first" {
        if (!this.#hasAllRequired()) {
            throw new Error("WSMessageBuilder: missing required fields before .build");
        }
        const message = { key: this.#key, ...this.#fields } as unknown as WebSocket.MessageByKey<K>;
        return WebSocketMessage.new(message) as never;
    }

    #hasAllRequired(): boolean {
        const parsed = WebSocketMessageSchema.safeParse({ key: this.#key, ...this.#fields });
        return parsed.success;
    }
}

export class WebSocketMessage<K extends WebSocket.MessageKey = WebSocket.MessageKey> {
    #data: WebSocket.MessageByKey<K>;

    private constructor(data: WebSocket.MessageByKey<K>) {
        this.#data = data;
    }

    static new<M extends WebSocket.Message>(message: M): WebSocketMessage<M["key"]> {
        return new WebSocketMessage(message);
    }

    static builder<K extends WebSocket.MessageKey>(key: K): WebSocketMessageBuilder<K> {
        return new WebSocketMessageBuilder(key);
    }

    get data() {
        return this.#data;
    }

    serialize(): string {
        return JSON.stringify(this.#data);
    }

    static deserialize(content: string) {
        return WebSocketMessageSchema.safeParse(JSON.parse(content.toString()));
    }
}
