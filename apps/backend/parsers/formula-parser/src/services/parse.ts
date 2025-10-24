import type { Token } from "excel-formula-tokenizer";
import { Effect } from "effect";
import { buildTree } from "excel-formula-ast";
import { tokenize } from "excel-formula-tokenizer";
import { BuildTreeError, TokenizeError } from "@/core/";

interface ParseFormulaReturnType {
    formula: string;
    tokens: Token[] | null;
    ast: Ast.Node | null;
    error: string;
}

function getRefType(cellRef: string): NonNullable<Ast.ReferenceNode["refType"]> {
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

function extendAst(node: Ast.Node): Ast.Node {
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

export function parseFormula(formula: string) {
    return Effect.gen(function* () {
        const tokens = yield* Effect.try({
            try: () => tokenize(formula),
            catch: (error) => new TokenizeError({ error }),
        });

        const ast = yield* Effect.try({
            try: () => buildTree(tokens),
            catch: (error) => new BuildTreeError({ error }),
        });

        const extendedAst = extendAst(ast as Ast.Node);

        return { formula, tokens, ast: extendedAst, error: "" } satisfies ParseFormulaReturnType;
    }).pipe(
        Effect.catchTags({
            BuildTreeError: (error) =>
                Effect.succeed<ParseFormulaReturnType>({
                    formula,
                    tokens: null,
                    ast: null,
                    error: `tokenization failed: ${error.error}`,
                }),
            TokenizeError: (error) =>
                Effect.succeed<ParseFormulaReturnType>({
                    formula,
                    tokens: null,
                    ast: null,
                    error: `tree building failed: ${error.error}`,
                }),
        }),
    );
}

export default parseFormula;
