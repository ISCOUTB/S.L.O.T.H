import winston from "winston";

export const logger = winston.createLogger({
    levels: {
        info: 0,
        warn: 1,
        error: 2,
        critical: 3,
    },
    format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ level, message }) => {
            return `[server] [formula-parser] ${level}: ${message}`;
        }),
    ),
    transports: [new winston.transports.Console()],
});
