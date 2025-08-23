// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var formula_parser_pb = require('./formula_parser_pb.js');
var dtypes_pb = require('./dtypes_pb.js');

function serialize_formula_parser_FormulaParserRequest(arg) {
  if (!(arg instanceof formula_parser_pb.FormulaParserRequest)) {
    throw new Error('Expected argument of type formula_parser.FormulaParserRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_formula_parser_FormulaParserRequest(buffer_arg) {
  return formula_parser_pb.FormulaParserRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_formula_parser_FormulaParserResponse(arg) {
  if (!(arg instanceof formula_parser_pb.FormulaParserResponse)) {
    throw new Error('Expected argument of type formula_parser.FormulaParserResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_formula_parser_FormulaParserResponse(buffer_arg) {
  return formula_parser_pb.FormulaParserResponse.deserializeBinary(new Uint8Array(buffer_arg));
}


var FormulaParserService = exports.FormulaParserService = {
  parseFormula: {
    path: '/formula_parser.FormulaParser/ParseFormula',
    requestStream: false,
    responseStream: false,
    requestType: formula_parser_pb.FormulaParserRequest,
    responseType: formula_parser_pb.FormulaParserResponse,
    requestSerialize: serialize_formula_parser_FormulaParserRequest,
    requestDeserialize: deserialize_formula_parser_FormulaParserRequest,
    responseSerialize: serialize_formula_parser_FormulaParserResponse,
    responseDeserialize: deserialize_formula_parser_FormulaParserResponse,
  },
};

exports.FormulaParserClient = grpc.makeGenericClientConstructor(FormulaParserService, 'FormulaParser');
