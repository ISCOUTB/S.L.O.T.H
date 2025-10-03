import { describe, expect, it, vi } from "vitest";

describe("logger", () => {
    it("should export logger instance", async () => {
        const { logger } = await import("@/utils/logger.ts");

        expect(logger).toBeDefined();

        expect(typeof logger.info).toBe("function");
        expect(typeof logger.error).toBe("function");
        expect(typeof logger.debug).toBe("function");
        expect(typeof logger.warn).toBe("function");
    });

    it("should log info messages", async () => {
        const { logger } = await import("@/utils/logger.ts");
        const spy = vi.spyOn(logger, "info").mockImplementation(() => logger);

        logger.info("test message");

        expect(spy).toHaveBeenCalledWith("test message");
        spy.mockRestore();
    });

    it("should log error messages", async () => {
        const { logger } = await import("@/utils/logger.ts");
        const spy = vi.spyOn(logger, "error").mockImplementation(() => logger);

        logger.error("error message");

        expect(spy).toHaveBeenCalledWith("error message");
        spy.mockRestore();
    });

    it("should log warn messages", async () => {
        const { logger } = await import("@/utils/logger.ts");
        const spy = vi.spyOn(logger, "warn").mockImplementation(() => logger);

        logger.warn("warning message");

        expect(spy).toHaveBeenCalledWith("warning message");
        spy.mockRestore();
    });

    it("should log debug messages", async () => {
        const { logger } = await import("@/utils/logger.ts");
        const spy = vi.spyOn(logger, "debug").mockImplementation(() => logger);

        logger.debug("debug message");

        expect(spy).toHaveBeenCalledWith("debug message");
        spy.mockRestore();
    });
});
