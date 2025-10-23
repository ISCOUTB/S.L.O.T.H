import { Buffer } from "node:buffer";
import { formula_parser } from "../generated/parsers/formula_parser";

export function requestSerialize(arg: formula_parser.FormulaParserRequest): Buffer {
    if (!(arg instanceof formula_parser.FormulaParserRequest)) {
        throw new TypeError("Expected argument of type FormulaParserRequest");
    }

    return Buffer.from(arg.serializeBinary());
}

export function requestDeserialize(buffer: Buffer): formula_parser.FormulaParserRequest {
    return formula_parser.FormulaParserRequest.deserializeBinary(new Uint8Array(buffer));
}

export function responseSerialize(arg: formula_parser.FormulaParserResponse): Buffer {
    if (!(arg instanceof formula_parser.FormulaParserResponse)) {
        throw new TypeError("Expected argument of type FormulaParserResponse");
    }

    return Buffer.from(arg.serializeBinary());
}

export function responseDeserialize(buffer: Buffer): formula_parser.FormulaParserResponse {
    return formula_parser.FormulaParserResponse.deserializeBinary(new Uint8Array(buffer));
}
