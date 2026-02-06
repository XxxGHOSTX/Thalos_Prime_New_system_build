/**
 * Thalos Prime - Main Entry Point
 * Orchestrates the decentralized data streams and automation engine.
 */

const { AutomationEngine } = require('./core/automation');
const { DataStreamManager } = require('./network/streams');
const { Logger } = require('./utils/logger');
require('dotenv').config();

async function bootstrap() {
    Logger.info("Initializing Thalos Prime System...");

    try {
        // Initialize Data Streams
        const streams = new DataStreamManager();
        await streams.connect();
        Logger.success("Decentralized data streams active.");

        // Start Automation Engine
        const engine = new AutomationEngine(streams);
        engine.start();
        Logger.success("Automation engine running.");

        // Keep process alive
        process.on('SIGINT', async () => {
            Logger.warn("Shutting down Thalos Prime...");
            await streams.disconnect();
            process.exit(0);
        });

    } catch (error) {
        Logger.error(`Bootstrap Failed: ${error.message}`);
        process.exit(1);
    }
}

bootstrap();
