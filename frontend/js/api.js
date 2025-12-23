// ============================================================================
// js/api.js - API Communication Layer
// ============================================================================

class MCPApi {
  constructor(baseUrl = CONFIG.API_BASE_URL) {
      this.baseUrl = baseUrl;
      this.conversationId = null;
  }

  async healthCheck() {
      try {
          const response = await fetch(`${this.baseUrl}/health`);
          return await response.json();
      } catch (error) {
          console.error('Health check failed:', error);
          return { status: 'error', error: error.message };
      }
  }

  async listTools() {
      try {
          const response = await fetch(`${this.baseUrl}/tools`);
          if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
          }
          return await response.json();
      } catch (error) {
          console.error('Failed to list tools:', error);
          throw error;
      }
  }

  async sendMessage(message) {
      try {
          const response = await fetch(`${this.baseUrl}/chat`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  message: message,
                  conversation_id: this.conversationId
              })
          });

          if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to send message');
          }

          const data = await response.json();
          this.conversationId = data.conversation_id;
          return data;
      } catch (error) {
          console.error('Failed to send message:', error);
          throw error;
      }
  }

  async resetConversation() {
      try {
          const response = await fetch(`${this.baseUrl}/reset`, {
              method: 'POST'
          });
          
          if (!response.ok) {
              throw new Error('Failed to reset conversation');
          }
          
          this.conversationId = null;
          return await response.json();
      } catch (error) {
          console.error('Failed to reset conversation:', error);
          throw error;
      }
  }
}

// WebSocket API (alternative implementation)
class MCPWebSocketApi {
  constructor(wsUrl = CONFIG.WS_URL) {
      this.wsUrl = wsUrl;
      this.ws = null;
      this.messageCallbacks = [];
      this.connected = false;
  }

  connect() {
      return new Promise((resolve, reject) => {
          this.ws = new WebSocket(this.wsUrl);

          this.ws.onopen = () => {
              this.connected = true;
              console.log('WebSocket connected');
              resolve();
          };

          this.ws.onerror = (error) => {
              console.error('WebSocket error:', error);
              reject(error);
          };

          this.ws.onclose = () => {
              this.connected = false;
              console.log('WebSocket disconnected');
          };

          this.ws.onmessage = (event) => {
              this.messageCallbacks.forEach(callback => callback(event.data));
          };
      });
  }

  sendMessage(message) {
      if (!this.connected) {
          throw new Error('WebSocket not connected');
      }
      this.ws.send(message);
  }

  onMessage(callback) {
      this.messageCallbacks.push(callback);
  }

  disconnect() {
      if (this.ws) {
          this.ws.close();
          this.ws = null;
      }
  }
}