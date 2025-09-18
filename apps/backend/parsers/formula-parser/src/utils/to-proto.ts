import type { Node } from "excel-formula-ast";
import type { Token } from "excel-formula-tokenizer";
import { dtypes } from "@etl-design/packages-proto-utils-js";
import { getAstTypeEnum, getRefTypeEnum, logger } from "../utils/index.ts";

export function convertTokensToProto(tokens: Token[]) {
    const protoTokens = new dtypes.Tokens();

    tokens.forEach((token) => {
        const protoToken = new dtypes.Tokens.Token();

        protoToken.value = token.value;
        protoToken.type = token.type;
        protoToken.subtype = token.subtype;

        protoTokens.tokens.push(protoToken);
    });

    return protoTokens;
}

export function convertAstToProto(ast: Node) {
    const astProto = new dtypes.AST();
    astProto.type = getAstTypeEnum(ast.type);

    const astType = ast.type;

    switch (astType) {
        case "binary-expression": {
            if (ast.operator) {
                astProto.operator = ast.operator;
            }

            if (ast.left) {
                astProto.left = convertAstToProto(ast.left);
            }

            if (ast.right) {
                astProto.right = convertAstToProto(ast.right);
            }

            break;
        }

        case "unary-expression": {
            if (ast.operator) {
                astProto.operator = ast.operator;
            }

            if (ast.operand) {
                astProto.operand = convertAstToProto(ast.operand);
            }

            break;
        }

        case "function": {
            if (ast.name) {
                astProto.name = ast.name;
            }

            if (ast.arguments && Array.isArray(ast.arguments)) {
                ast.arguments.forEach((argument) => {
                    if (astProto.arguments) {
                        astProto.arguments.push(convertAstToProto(argument));
                    }
                });
            }

            break;
        }

        case "cell": {
            if (ast.key) {
                astProto.key = ast.key;
            }

            if (ast.refType) {
                astProto.refType = getRefTypeEnum(ast.refType);
            }

            break;
        }

        case "cell-range": {
            if (ast.left) {
                astProto.left = convertAstToProto(ast.left);
            }

            if (ast.right) {
                astProto.right = convertAstToProto(ast.right);
            }

            break;
        }

        case "number": {
            if (ast.value !== undefined) {
                astProto.number_value = ast.value;
            }

            break;
        }

        case "text": {
            if (ast.value !== undefined) {
                astProto.text_value = ast.value;
            }

            break;
        }

        case "logical": {
            if (ast.value !== undefined) {
                astProto.logical_value = ast.value;
            }

            break;
        }

        default: {
            logger.warn(`[convertAstToProto] unknown type: ${astType}`);
            break;
        }
    }

    return astProto;
}

export const Convert = {
    TokensToProto: convertTokensToProto,
    AstToProto: convertAstToProto,
};

export default Convert;
