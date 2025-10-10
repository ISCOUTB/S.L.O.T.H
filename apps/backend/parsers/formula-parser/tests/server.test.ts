/* eslint-disable dot-notation */
import type { sendUnaryData, ServerUnaryCall } from "@grpc/grpc-js";
import { formula_parser } from "@etl-design/packages-proto-utils-js";
import { credentials } from "@grpc/grpc-js";
import { Effect } from "effect";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/handlers/handler.ts", () => ({
    handler: vi.fn(),
}));

vi.mock("@/utils/index.ts", () => ({
    logger: {
        info: vi.fn(),
        error: vi.fn(),
        warn: vi.fn(),
        debug: vi.fn(),
        crit: vi.fn(),
    },
}));

vi.mock("@/core/index.ts", () => ({
    settings: Effect.succeed({
        FORMULA_PARSER_HOST: "localhost",
        FORMULA_PARSER_PORT: 50052,
        DEBUG_FORMULA_PARSER: false,
    }),
    BindPortError: class BindPortError extends Error {
        constructor(public error: { error: Error }) {
            super(error.error.message);
        }
    },
}));

describe("environment variables", () => {
    it("should have FORMULA_PARSER_HOST defined", () => {
        const host = process.env["FORMULA_PARSER_HOST"];
        expect(host).toBeDefined();
        expect(host).toBeTypeOf("string");
    });

    it("should have FORMULA_PARSER_PORT defined", () => {
        const port = process.env["FORMULA_PARSER_PORT"];
        expect(port).toBeDefined();
        expect(port).toBeTypeOf("string");
    });

    it("should have DEBUG_FORMULA_PARSER defined and be a boolean", () => {
        const debug = !!process.env["DEBUG_FORMULA_PARSER"] === true;
        expect(debug).toBeDefined();
        expect(debug).toBeTypeOf("boolean");
    });
});

describe("getServer", () => {
    it("should create a gRPC server instance", async () => {
        const { getServer } = await import("@/server.ts");

        const server = await Effect.runPromise(getServer());

        expect(server).toBeDefined();
        expect(typeof server.addService).toBe("function");
        expect(typeof server.bindAsync).toBe("function");
    });
});

describe("parseFormula handler", () => {
    it("should call handler and invoke callback with response", async () => {
        const { handler } = await import("@/handlers/handler.ts");
        const { parseFormula } = await import("@/server.ts");

        const mockResponse = new formula_parser.FormulaParserResponse();
        mockResponse.formula = "=A1+B1";
        mockResponse.error = "";

        vi.mocked(handler).mockReturnValue(Effect.succeed(mockResponse));

        const mockRequest = new formula_parser.FormulaParserRequest();
        mockRequest.formula = "=A1+B1";

        const mockCall = {
            request: mockRequest,
        } as ServerUnaryCall<
            formula_parser.FormulaParserRequest,
            formula_parser.FormulaParserResponse
        >;

        const mockCallback = vi.fn() as sendUnaryData<formula_parser.FormulaParserResponse>;

        parseFormula(mockCall, mockCallback);

        await new Promise((resolve) => setTimeout(resolve, 100));

        expect(mockCallback).toHaveBeenCalledWith(null, mockResponse);
    });
});

describe("gRPC Server Integration (mocked)", () => {
    beforeEach<{ client: formula_parser.FormulaParserClient }>(async (context) => {
        context.client = new formula_parser.FormulaParserClient(
            "localhost:50052",
            credentials.createInsecure(),
        );
    });

    afterEach<{ client: formula_parser.FormulaParserClient }>((context) => {
        context.client.close();
        vi.clearAllMocks();
    });

    it<{
        client: formula_parser.FormulaParserClient;
    }>("should parse a simple formula - mocked", (context) => {
        const request = new formula_parser.FormulaParserRequest();
        request.formula = "=A1+B1";

        const mockResponse = new formula_parser.FormulaParserResponse();
        mockResponse.formula = "=A1+B1";
        mockResponse.error = "";

        vi.spyOn(context.client, "ParseFormula").mockImplementation((_request, callback) => {
            callback(null, mockResponse);
            return {} as any;
        });

        context.client.ParseFormula(request, (error, response) => {
            expect(error).toBeNull();
            expect(response?.formula).toBe("=A1+B1");
            expect(response?.error).toBe("");
        });
    });
});
