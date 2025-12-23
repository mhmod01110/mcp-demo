// ============================================================================
// js/config.js - Configuration
// ============================================================================

const CONFIG = {
  API_BASE_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000/ws',
  USE_WEBSOCKET: false, // Set to true to use WebSocket instead of REST
  MAX_MESSAGE_LENGTH: 4000,
  TYPING_INDICATOR_DELAY: 500,
  AUTO_SCROLL: true
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}