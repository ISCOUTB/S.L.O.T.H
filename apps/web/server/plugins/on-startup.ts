export default defineNitroPlugin(async () => {
    if (import.meta.prerender) {
        return;
    }

    const logger = Logger.getInstance();

    logger.warn(useRuntimeConfig());

    try {
        const redis = await RedisService.getInstance();
        logger.warn(await redis.ping());
    } catch (error) {
        logger.error(error);
    }
});
