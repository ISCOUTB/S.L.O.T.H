require('dotenv').config({ path: '../.env' });

const host = process.env.FORMULA_PARSER_HOST || 'localhost';
const port = process.env.FORMULA_PARSER_PORT || '50052';

var debug;

try {
    debug = process.env.DEBUG_FORMULA_PARSER.toLowerCase() === 'true';
} catch (e) {
    debug = false;
}

const settings = { host, port, debug };

module.exports = { settings };
