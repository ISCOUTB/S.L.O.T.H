/* eslint-disable dot-notation */
import { formula_parser } from "@etl-design/packages-proto-utils-js";
import { credentials } from "@grpc/grpc-js";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {} from "@/server";

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

describe("gRPC Server Integration", () => {
    beforeEach<{ client: formula_parser.FormulaParserClient }>(async (context) => {
        vi.mock("@/server", () => ({
            main: vi.fn().mockResolvedValue(undefined),
        }));

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
    }>("should parse a simple formula - server running", (context) => {
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
