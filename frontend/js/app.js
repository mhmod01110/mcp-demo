// ============================================================================
// js/app.js - Main Application Logic
// ============================================================================

class MCPApp {
  constructor() {
      this.api = new MCPApi();
      this.ui = new MCPUI();
      this.tools = [];
      this.isProcessing = false;
  }

  async initialize() {
      console.log('Initializing MCP App...');
      
      // Load theme
      this.ui.loadTheme();
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Check server connection
      await this.checkConnection();
      
      // Load tools
      await this.loadTools();
      
      // Focus input
      this.ui.focusInput();
      
      console.log('MCP App initialized successfully');
  }

  setupEventListeners() {
      // Chat form submission
      this.ui.chatForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          await this.handleSendMessage();
      });

      // Enter key handling
      this.ui.messageInput.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              this.ui.chatForm.dispatchEvent(new Event('submit'));
          }
      });

      // Auto-resize textarea
      this.ui.messageInput.addEventListener('input', () => {
          this.ui.messageInput.style.height = 'auto';
          this.ui.messageInput.style.height = this.ui.messageInput.scrollHeight + 'px';
      });

      // Tools button
      document.getElementById('toolsBtn').addEventListener('click', () => {
          this.ui.toggleSidebar();
      });

      // Close sidebar
      document.getElementById('closeSidebar').addEventListener('click', () => {
          this.ui.closeSidebar();
      });

      // Reset button
      document.getElementById('resetBtn').addEventListener('click', async () => {
          await this.handleReset();
      });

      // Theme button
      document.getElementById('themeBtn').addEventListener('click', () => {
          this.ui.toggleTheme();
      });
  }

  async checkConnection() {
      try {
          this.ui.updateStatus('Checking connection...', false);
          const health = await this.api.healthCheck();
          
          if (health.status === 'healthy') {
              this.ui.updateStatus('Connected', true);
          } else {
              this.ui.updateStatus('Server unavailable', false);
              this.ui.showError('Could not connect to server. Please check if the backend is running.');
          }
      } catch (error) {
          this.ui.updateStatus('Connection failed', false);
          this.ui.showError('Failed to connect to server. Please start the backend server.');
          console.error('Connection check failed:', error);
      }
  }

  async loadTools() {
      try {
          this.tools = await this.api.listTools();
          this.ui.updateToolCount(this.tools.length);
          this.ui.displayTools(this.tools);
          console.log(`Loaded ${this.tools.length} tools`);
      } catch (error) {
          console.error('Failed to load tools:', error);
          this.ui.showError('Failed to load tools');
      }
  }

  async handleSendMessage() {
      if (this.isProcessing) {
          return;
      }

      const message = this.ui.getMessageInput();
      
      if (!message) {
          return;
      }

      if (message.length > CONFIG.MAX_MESSAGE_LENGTH) {
          this.ui.showError(`Message too long. Maximum ${CONFIG.MAX_MESSAGE_LENGTH} characters.`);
          return;
      }

      this.isProcessing = true;
      this.ui.disableInput();

      try {
          // Display user message
          this.ui.addMessage(message, 'user');
          this.ui.clearMessageInput();

          // Show typing indicator
          setTimeout(() => {
              if (this.isProcessing) {
                  this.ui.showTypingIndicator();
              }
          }, CONFIG.TYPING_INDICATOR_DELAY);

          // Send to API
          const response = await this.api.sendMessage(message);

          // Hide typing indicator
          this.ui.hideTypingIndicator();

          // Display assistant response
          this.ui.addMessage(response.response, 'assistant', {
              toolCalls: response.tool_calls
          });

      } catch (error) {
          this.ui.hideTypingIndicator();
          this.ui.showError(error.message);
          console.error('Error sending message:', error);
      } finally {
          this.isProcessing = false;
          this.ui.enableInput();
      }
  }

  async handleReset() {
      if (this.isProcessing) {
          return;
      }

      try {
          this.ui.showLoading('Resetting conversation...');
          await this.api.resetConversation();
          this.ui.clearMessages();
          this.ui.hideLoading();
      } catch (error) {
          this.ui.hideLoading();
          this.ui.showError('Failed to reset conversation');
          console.error('Reset failed:', error);
      }
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  const app = new MCPApp();
  await app.initialize();
  
  // Make app available globally for debugging
  window.mcpApp = app;
});