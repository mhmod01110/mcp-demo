// ============================================================================
// js/ui.js - UI Components and Helpers
// ============================================================================

class MCPUI {
  constructor() {
      this.chatMessages = document.getElementById('chatMessages');
      this.messageInput = document.getElementById('messageInput');
      this.chatForm = document.getElementById('chatForm');
      this.loadingOverlay = document.getElementById('loadingOverlay');
      this.sidebar = document.getElementById('sidebar');
      this.toolsList = document.getElementById('toolsList');
      this.statusText = document.getElementById('statusText');
      this.connectionStatus = document.getElementById('connectionStatus');
      this.toolCount = document.getElementById('toolCount');
  }

  // Message Display
  addMessage(content, type = 'assistant', metadata = {}) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message message-${type}`;
      
      if (type === 'user') {
          messageDiv.textContent = content;
      } else if (type === 'assistant') {
          // Support markdown-like formatting
          messageDiv.innerHTML = this.formatMessage(content);
      } else if (type === 'system') {
          messageDiv.textContent = content;
      }

      // Add tool calls if present
      if (metadata.toolCalls && metadata.toolCalls.length > 0) {
          metadata.toolCalls.forEach(toolCall => {
              const toolDiv = this.createToolCallElement(toolCall);
              messageDiv.appendChild(toolDiv);
          });
      }

      this.chatMessages.appendChild(messageDiv);
      
      if (CONFIG.AUTO_SCROLL) {
          this.scrollToBottom();
      }

      return messageDiv;
  }

  formatMessage(text) {
      if (!text) return '';
      
      // Basic formatting
      return text
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/`(.*?)`/g, '<code>$1</code>')
          .replace(/\n/g, '<br>');
  }

  createToolCallElement(toolCall) {
      const toolDiv = document.createElement('div');
      toolDiv.className = 'tool-call';
      
      const header = document.createElement('div');
      header.className = 'tool-call-header';
      header.textContent = `🔧 Tool: ${toolCall.name}`;
      
      const args = document.createElement('div');
      args.className = 'tool-call-args';
      args.textContent = JSON.stringify(toolCall.arguments, null, 2);
      
      toolDiv.appendChild(header);
      toolDiv.appendChild(args);
      
      return toolDiv;
  }

  showTypingIndicator() {
      const indicator = document.createElement('div');
      indicator.className = 'message message-assistant typing-indicator';
      indicator.id = 'typingIndicator';
      indicator.innerHTML = `
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
      `;
      this.chatMessages.appendChild(indicator);
      this.scrollToBottom();
  }

  hideTypingIndicator() {
      const indicator = document.getElementById('typingIndicator');
      if (indicator) {
          indicator.remove();
      }
  }

  clearMessages() {
      this.chatMessages.innerHTML = '';
      this.addMessage('Conversation reset. Start a new chat!', 'system');
  }

  scrollToBottom() {
      this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  // Loading States
  showLoading(message = 'Processing...') {
      this.loadingOverlay.querySelector('p').textContent = message;
      this.loadingOverlay.classList.remove('hidden');
  }

  hideLoading() {
      this.loadingOverlay.classList.add('hidden');
  }

  // Sidebar
  toggleSidebar() {
      this.sidebar.classList.toggle('hidden');
  }

  closeSidebar() {
      this.sidebar.classList.add('hidden');
  }

  displayTools(tools) {
      this.toolsList.innerHTML = '';
      
      if (tools.length === 0) {
          this.toolsList.innerHTML = '<p>No tools available</p>';
          return;
      }

      tools.forEach(tool => {
          const toolCard = document.createElement('div');
          toolCard.className = 'tool-card';
          
          const title = document.createElement('h4');
          title.textContent = tool.name;
          
          const description = document.createElement('p');
          description.textContent = tool.description;
          
          const params = document.createElement('div');
          params.className = 'tool-params';
          params.textContent = JSON.stringify(tool.input_schema, null, 2);
          
          toolCard.appendChild(title);
          toolCard.appendChild(description);
          toolCard.appendChild(params);
          
          this.toolsList.appendChild(toolCard);
      });
  }

  // Status Updates
  updateStatus(text, connected = false) {
      this.statusText.textContent = text;
      
      if (connected) {
          this.connectionStatus.classList.add('connected');
      } else {
          this.connectionStatus.classList.remove('connected');
      }
  }

  updateToolCount(count) {
      this.toolCount.textContent = `${count} tool${count !== 1 ? 's' : ''} available`;
  }

  // Input Handling
  getMessageInput() {
      return this.messageInput.value.trim();
  }

  clearMessageInput() {
      this.messageInput.value = '';
      this.messageInput.style.height = 'auto';
  }

  focusInput() {
      this.messageInput.focus();
  }

  disableInput() {
      this.messageInput.disabled = true;
      this.chatForm.querySelector('button').disabled = true;
  }

  enableInput() {
      this.messageInput.disabled = false;
      this.chatForm.querySelector('button').disabled = false;
      this.focusInput();
  }

  // Theme
  toggleTheme() {
      document.body.classList.toggle('dark-theme');
      const isDark = document.body.classList.contains('dark-theme');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  loadTheme() {
      const theme = localStorage.getItem('theme');
      if (theme === 'dark') {
          document.body.classList.add('dark-theme');
      }
  }

  // Error Display
  showError(message) {
      this.addMessage(`Error: ${message}`, 'system');
  }
}

