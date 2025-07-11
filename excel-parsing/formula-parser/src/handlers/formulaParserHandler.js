require('dotenv').config({ path: '../.env' });

var { parseFormula } = require('../services/formulaParser');
var messages = require('../clients/formula_parser_pb');
var dtypes = require('../clients/dtypes_pb');

function parseFormulaHandler(formula) {
    var response = new messages.FormulaParserResponse();
    const { tokens, ast, error } = parseFormula(formula);

    if (process.env.DEBUG_FORMULA_PARSER) {
        console.log(`Parsing formula: ${formula}`);
        console.log(`Tokens: ${JSON.stringify(tokens, null, 2)}`);
        console.log(`AST: ${JSON.stringify(ast, null, 2)}`);
        console.log(`Error: ${error}`);
    }

    response.setFormula(formula);

    if (!tokens || !ast || error) {
        response.setError(error);
        return response;
    }

    if (tokens) {
        response.setTokens(convertTokensToProto(tokens));
    }

    if (ast) {
        response.setAst(convertAstToProto(ast));
    }

    response.setError(""); // Sin errores
    return response;
}

/**
 * Convierte tokens de JavaScript a formato Protocol Buffers
 */
function convertTokensToProto(tokens) {
    const tokensProto = new dtypes.Tokens();

    tokens.forEach(token => {
        const tokenProto = new dtypes.Tokens.Token();
        tokenProto.setValue(token.value);
        tokenProto.setType(token.type);
        tokenProto.setSubtype(token.subtype);
        tokensProto.addTokens(tokenProto);
    });

    return tokensProto;
}

/**
 * Convierte AST de JavaScript a formato Protocol Buffers
 */
function convertAstToProto(ast) {
    if (!ast) return null;

    const astProto = new dtypes.AST();

    // Establecer tipo de AST
    astProto.setType(getAstTypeEnum(ast.type));

    // Manejar diferentes tipos de nodos
    if (ast.operator) {
        astProto.setOperator(ast.operator);
    }

    if (ast.left) {
        astProto.setLeft(convertAstToProto(ast.left));
    }

    if (ast.right) {
        astProto.setRight(convertAstToProto(ast.right));
    }

    if (ast.arguments && Array.isArray(ast.arguments)) {
        ast.arguments.forEach(arg => {
            astProto.addArguments(convertAstToProto(arg));
        });
    }

    if (ast.name) {
        astProto.setName(ast.name);
    }

    if (ast.refType) {
        astProto.setReftype(getRefTypeEnum(ast.refType));
    }

    if (ast.key) {
        astProto.setKey(ast.key);
    }

    if (ast.operand) {
        astProto.setOperand(convertAstToProto(ast.operand));
    }

    if (ast.value !== undefined && ast.value !== null) {
        if (typeof ast.value === 'number') {
            astProto.setNumberValue(ast.value);
        } else if (typeof ast.value === 'string') {
            astProto.setTextValue(ast.value);
        } else {
            astProto.setLogicalValue(ast.value === true);
        }
    }

    return astProto;
}

/**
 * Mapea tipos de AST a enums de Protocol Buffers
 */
function getAstTypeEnum(type) {
    const dtypesEnum = dtypes.AstType;
    const typeMap = {
        'binary-expression': dtypesEnum.AST_BINARY_EXPRESSION,
        'cell-range': dtypesEnum.AST_CELL_RANGE,
        'function': dtypesEnum.AST_FUNCTION,
        'cell': dtypesEnum.AST_CELL,
        'number': dtypesEnum.AST_NUMBER,
        'logical': dtypesEnum.AST_LOGICAL,
        'text': dtypesEnum.AST_TEXT
    };
    return typeMap[type] || dtypesEnum.AST_UNKNOWN;
}

/**
 * Mapea tipos de referencia a enums de Protocol Buffers
 */
function getRefTypeEnum(refType) {
    const dtypesEnum = dtypes.RefType;
    const refMap = {
        'relative': dtypesEnum.REF_RELATIVE,
        'absolute': dtypesEnum.REF_ABSOLUTE,
        'mixed': dtypesEnum.REF_MIXED
    };
    return refMap[refType] || dtypesEnum.REF_UNKNOWN;
}

exports.parseFormulaHandler = parseFormulaHandler;
