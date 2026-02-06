/**
 * System Logger
 * Standardized logging for all Thalos Prime modules.
 */

const chalk = require('chalk');

const Logger = {
    info: (msg) => console.log(chalk.blue(`[INFO] ${msg}`)),
    success: (msg) => console.log(chalk.green(`[SUCCESS] ${msg}`)),
    warn: (msg) => console.log(chalk.yellow(`[WARN] ${msg}`)),
    error: (msg) => console.log(chalk.red(`[ERROR] ${msg}`)),
};

module.exports = { Logger };
