export default defineNitroPlugin(() => {
    const logger = Logger.getInstance();

    logger.warn(useRuntimeConfig());

    const redis = RedisService.getInstance();
    redis.ping()
        .then((response) => logger.warn(response))
        .catch((error) => logger.error(error));
});
