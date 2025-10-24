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

export function getRefType(cellRef: string): NonNullable<Ast.ReferenceNode["refType"]> {
    const colAbsolute = cellRef.startsWith("$");
    const rowAbsolute = /\$\d+$/.test(cellRef);

    if (colAbsolute && rowAbsolute) {
        return "absolute";
    }

    if (colAbsolute || rowAbsolute) {
        return "mixed";
    }

    return "relative";
}

export function extendAst(node: Ast.Node): Ast.Node {
    switch (node.type) {
        case "cell": {
            const match = /^([^!]+)!(.+)/.exec(node.key);

            if (match) {
                const [, sheetName, cellRef] = match;

                if (!sheetName || !cellRef) {
                    return node;
                }

                return {
                    type: "reference-node",
                    sheetName,
                    key: cellRef,
                    refType: getRefType(cellRef),
                };
            }

            break;
        }

        case "binary-expression": {
            return {
                ...node,
                left: extendAst(node.left),
                right: extendAst(node.right),
            };
        }

        case "unary-expression": {
            return {
                ...node,
                operand: extendAst(node.operand),
            };
        }

        case "function": {
            return {
                ...node,
                arguments: node.arguments.map((_node) => extendAst(_node)),
            };
        }

        case "cell-range": {
            return {
                ...node,
                left: extendAst(node.left),
                right: extendAst(node.right),
            };
        }

        default: {
            return node;
        }
    }

    return node;
}
