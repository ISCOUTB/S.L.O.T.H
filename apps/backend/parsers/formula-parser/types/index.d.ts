import type * as _ from "excel-formula-ast";

declare global {
    namespace Ast {
        interface ReferenceNode {
            type: "reference-node";
            sheetName: string;
            key: string;
            refType?: "relative" | "absolute" | "mixed";
        }

        interface BinaryExpressionNode extends _.BinaryExpressionNode {
            left: Ast.Node;
            right: Ast.Node;
        }

        interface UnaryExpressionNode extends _.UnaryExpressionNode {
            operand: Ast.Node;
        }

        interface FunctionNode extends _.FunctionNode {
            arguments: Ast.Node[];
        }

        interface CellRangeNode extends _.CellRangeNode {
            left: Ast.Node;
            right: Ast.Node;
        }

        type Node =
            | Ast.ReferenceNode
            | Ast.BinaryExpressionNode
            | Ast.CellRangeNode
            | Ast.FunctionNode
            | Ast.UnaryExpressionNode
            | _.NumberNode
            | _.TextNode
            | _.CellNode
            | _.LogicalNode;
    }
}

export {};
