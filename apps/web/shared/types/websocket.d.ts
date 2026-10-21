import type { WebSocketMessageSchema } from "#shared/utils/websocket";
import type { z } from "zod";

declare global {
    namespace WebSocket {
        type Message = z.infer<typeof WebSocketMessageSchema>;

        type MessageKey = WebSocket.Message["key"];

        type MessageByKey<K extends WebSocket.MessageKey> = Extract<WebSocket.Message, { key: K }>;

        type MessageFields<K extends WebSocket.MessageKey> = Omit<WebSocket.MessageByKey<K>, "key">;

        type RequiredFields<T> = {
            [K in keyof T as undefined extends T[K] ? never : K]: T[K];
        };

        type CanBuild<K extends WSMessageKey, Collected> =
            RequiredFields<MessageFields<K>> extends Collected ? true : false;
    }
}
