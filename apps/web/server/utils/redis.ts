import {
    circuitBreaker,
    ConsecutiveBreaker,
    ExponentialBackoff,
    handleAll,
    retry,
    wrap,
} from "cockatiel";
import Redis from "ioredis";

export class RedisService {
    private static instance: Redis | null = null;
    private static policy = RedisService.createExecutionPolicy();

    private static createClient(): Redis {
        const {
            database: { redis },
        } = useRuntimeConfig();
        const logger = Logger.getInstance();

        const client = new Redis({
            host: redis.HOST,
            port: Number(redis.PORT),
            password: redis.PASSWORD,
            db: Number(redis.DB),
            lazyConnect: true,
            enableOfflineQueue: false,
            maxRetriesPerRequest: 0,
        });

        client.on("error", (error) => logger.error(error));

        return client;
    }

    @Singleton()
    static async getInstance(): Promise<Redis> {
        if (!RedisService.instance) {
            const client = RedisService.createClient();

            try {
                await RedisService.policy.execute(() => client.connect());
                RedisService.instance = client;
            } catch (error) {
                const logger = Logger.getInstance();
                logger.error(`redis: ${error}`);
                throw error;
            }
        }

        return RedisService.instance;
    }

    static async Execute<T>(operation: (client: Redis) => Promise<T>): Promise<T> {
        const client = await RedisService.getInstance();
        return RedisService.policy.execute(() => operation(client));
    }

    private static createExecutionPolicy() {
        const {
            database: { redis },
        } = useRuntimeConfig();

        const RetryPolicy = retry(handleAll, {
            maxAttempts: Number(redis.MAX_RETRIES),
            backoff: new ExponentialBackoff({
                exponent: Number(redis.BACKOFF_FACTOR),
            }),
        });

        const BreakerPolicy = circuitBreaker(handleAll, {
            halfOpenAfter: 10_000,
            breaker: new ConsecutiveBreaker(Number(redis.MAX_RETRIES)),
        });

        return wrap(RetryPolicy, BreakerPolicy);
    }
}
