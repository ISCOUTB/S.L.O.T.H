import type { CellNode } from "excel-formula-ast";
import { dtypes } from "@etl-design/packages-proto-utils-js";
import { Effect } from "effect";

export function getAstTypeEnum(type: Ast.Node["type"]) {
    const typeMap: Record<Ast.Node["type"], (typeof dtypes.AstType)[keyof typeof dtypes.AstType]> =
        {
            function: dtypes.AstType.AST_FUNCTION,
            cell: dtypes.AstType.AST_CELL,
            number: dtypes.AstType.AST_NUMBER,
            logical: dtypes.AstType.AST_LOGICAL,
            text: dtypes.AstType.AST_TEXT,
            "binary-expression": dtypes.AstType.AST_BINARY_EXPRESSION,
            "cell-range": dtypes.AstType.AST_CELL_RANGE,
            "unary-expression": dtypes.AstType.AST_UNARY_EXPRESSION,
            "reference-node": dtypes.AstType.AST_REFERENCE,
        };

    return Effect.succeed(typeMap[type] ?? dtypes.AstType.AST_UNKNOWN);
}

export function getRefTypeEnum(refType: Required<CellNode>["refType"]) {
    const refMap: Record<
        Required<CellNode>["refType"],
        (typeof dtypes.RefType)[keyof typeof dtypes.RefType]
    > = {
        relative: dtypes.RefType.REF_RELATIVE,
        absolute: dtypes.RefType.REF_ABSOLUTE,
        mixed: dtypes.RefType.REF_MIXED,
    };

    return Effect.succeed(refMap[refType] ?? dtypes.RefType.REF_UNKNOWN);
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
