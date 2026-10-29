import { WebSocketMessage } from "#shared/utils/websocket";

export default defineWebSocketHandler({
    async message(peer, message) {
        const logger = Logger.getInstance();

        try {
            const parsedMessage = WebSocketMessage.deserialize(message.toString());

            if (parsedMessage.error || !parsedMessage.success) {
                peer.send(WebSocketMessage.new({ key: "socket:bad-payload" }).serialize());
                return;
            }

            switch (parsedMessage.data.key) {
                case "ping": {
                    const { userId } = parsedMessage.data;

                    if (userId) {
                        await RedisService.Execute((redis) => {
                            return redis.expire(WebSocketKeys.User.Connected(userId), 300);
                        });
                    }
                    peer.send(WebSocketMessage.new({ key: "pong" }).serialize());
                    break;
                }

                case "pong": {
                    peer.send(WebSocketMessage.new({ key: "ping" }).serialize());
                    break;
                }

                case "user-logged": {
                    const { userId } = parsedMessage.data;

                    await RedisService.Execute((redis) => {
                        return redis.set(WebSocketKeys.User.Connected(userId), peer.id, "EX", 300);
                    });

                    break;
                }

                default: {
                    peer.send(WebSocketMessage.new({ key: "socket:bad-payload" }).serialize());
                }
            }
        } catch (e) {
            logger.error(`socket: ${e}`);
        }
    },
});
