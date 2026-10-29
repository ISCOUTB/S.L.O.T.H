import { WebSocketMessage } from "#shared/utils/websocket";

export default defineNuxtPlugin({
    name: "websocket",
    parallel: true,
    setup() {
        const auth = useAuth();
        const config = useAppConfig();
        const socket = useWebSocket<WebSocket.Message>(config.handlers.websocket.url, {
            autoReconnect: true,
            heartbeat: {
                message: WebSocketMessage.builder("ping")
                    .set("userId", auth.data.value?.user.id)
                    .build
                    .serialize(),
                pongTimeout: config.handlers.websocket.pongTimeout,
                scheduler: (callback) =>
                    useIntervalFn(callback, config.handlers.websocket.pingInterval),
            },
        });

        watch(
            [socket.status, auth.status],
            ([socketStatus, authStatus]) => {
                if (
                    socketStatus === "OPEN" &&
                    authStatus === "authenticated" &&
                    auth.data.value?.user
                ) {
                    socket.send(
                        WebSocketMessage.builder("user-logged")
                            .set("userId", auth.data.value.user.id)
                            .build.serialize(),
                    );
                }
            },
            { immediate: true },
        );

        return {
            provide: {
                socket,
            },
        };
    },
});
