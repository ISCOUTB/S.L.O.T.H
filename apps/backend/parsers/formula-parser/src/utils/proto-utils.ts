import type { CellNode, Node } from "excel-formula-ast";
import { dtypes } from "@etl-design/packages-proto-utils-js";
import { Effect } from "effect";

export function getAstTypeEnum(type: Node["type"]) {
    const dtypesEnum = dtypes.AstType;

    const typeMap = {
        function: dtypesEnum.AST_FUNCTION,
        cell: dtypesEnum.AST_CELL,
        number: dtypesEnum.AST_NUMBER,
        logical: dtypesEnum.AST_LOGICAL,
        text: dtypesEnum.AST_TEXT,
        "binary-expression": dtypesEnum.AST_BINARY_EXPRESSION,
        "cell-range": dtypesEnum.AST_CELL_RANGE,
        "unary-expression": dtypesEnum.AST_UNARY_EXPRESSION,
    };

    return Effect.succeed(typeMap[type] ?? dtypesEnum.AST_UNKNOWN);
}

export function getRefTypeEnum(refType: Required<CellNode>["refType"]) {
    const dtypesEnum = dtypes.RefType;

    const refMap = {
        relative: dtypesEnum.REF_RELATIVE,
        absolute: dtypesEnum.REF_ABSOLUTE,
        mixed: dtypesEnum.REF_MIXED,
    };

    return Effect.succeed(refMap[refType as keyof typeof refMap] ?? dtypesEnum.REF_UNKNOWN);
}
