import winston from "winston";

export const logger = winston.createLogger({
    levels: {
        error: 0,
        warn: 1,
        info: 2,
        debug: 3,
    },
    format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ level, message }) => {
            return `[server] [formula-parser] ${level}: ${message}`;
        }),
    ),
    transports: [new winston.transports.Console()],
});
