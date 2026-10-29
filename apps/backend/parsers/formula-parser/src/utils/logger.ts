import process from "node:process";
import { trace } from "@opentelemetry/api";
import winston from "winston";

const serviceName = "formula-parser";
const serviceVersion = process.env["OTEL_SERVICE_VERSION"] ?? "1.0.0";
const isDebugEnabled =
    process.env["DEBUG_FORMULA_PARSER"]?.toLowerCase() === "true" ||
    process.env["FORMULA_PARSER_DEBUG"]?.toLowerCase() === "true";
const environment = isDebugEnabled ? "debug" : "production";
const loggerName = "FormulaParserServer";

const defaultTraceId = "00000000000000000000000000000000";
const defaultSpanId = "0000000000000000";

const productionFormat = winston.format.combine(
    winston.format.errors({ stack: true }),
    winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss,SSS" }),
    winston.format((info) => {
        const record = info as Record<string, unknown>;
        const {
            timestamp,
            level,
            message,
            trace_id,
            span_id,
            trace_flags,
            module,
            funcName,
            ...meta
        } = record;
        const activeSpanContext = trace.getActiveSpan()?.spanContext();

        return {
            asctime: timestamp,
            level: typeof level === "string" ? level : "info",
            levelname: typeof level === "string" ? level.toUpperCase() : level,
            name: loggerName,
            message,
            service_name: serviceName,
            service_version: serviceVersion,
            environment,
            trace_id:
                typeof trace_id === "string"
                    ? trace_id
                    : activeSpanContext
                      ? activeSpanContext.traceId
                      : defaultTraceId,
            span_id:
                typeof span_id === "string"
                    ? span_id
                    : activeSpanContext
                      ? activeSpanContext.spanId
                      : defaultSpanId,
            trace_flags:
                typeof trace_flags === "string"
                    ? trace_flags
                    : activeSpanContext
                      ? activeSpanContext.traceFlags.toString(16).padStart(2, "0")
                      : "00",
            module: typeof module === "string" ? module : "server",
            funcName: typeof funcName === "string" ? funcName : "unknown",
            ...meta,
        };
    })(),
    winston.format.json(),
);

export const logger = winston.createLogger({
    level: isDebugEnabled ? "debug" : "info",
    format: productionFormat,
    defaultMeta: {
        name: loggerName,
        service_name: serviceName,
        service_version: serviceVersion,
        environment,
        trace_id: defaultTraceId,
        span_id: defaultSpanId,
        trace_flags: "00",
    },
    transports: [
        new winston.transports.Console(),
        ...(isDebugEnabled
            ? [new winston.transports.File({ filename: "formula-parser.log" })]
            : []),
    ],
});
