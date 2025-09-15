
import { createChatBotMessage } from "react-chatbot-kit";
import { callLLM1, callLLM2,callLLM3 } from "./LLMService";

class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }

  // Add or update user info in global state
  updateUserInfo(newInfo) {
    this.setState((prev) => ({
      ...prev,
      userData: { ...prev.userData, ...newInfo },
    }));
    this.addMessage(this.createChatBotMessage("✅ User info updated."));
  }
  
  addMessage(message) {
    this.setState((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }));
  }


async extractStockSymbolsFromText(text, userData = {}) {
  try {
    // Call LLM3 for dynamic detection with correct parameters
    const symbol = await callLLM3(text, userData);

    // Check if the response is valid and not an error message
    if (symbol && symbol !== "NONE" && !symbol.includes("Sorry") && !symbol.includes("⚠️")) {
      return symbol;
    }

    // Fallback to static mapping + regex
    const stockMappings = {
      'apple': 'AAPL',
      'google': 'GOOGL',
      'alphabet': 'GOOGL',
      'microsoft': 'MSFT',
      'tesla': 'TSLA',
      'amazon': 'AMZN',
      'meta': 'META',
      'facebook': 'META',
      'nvidia': 'NVDA',
      'netflix': 'NFLX'
    };

    for (const [name, mappedSymbol] of Object.entries(stockMappings)) {
      if (text.toLowerCase().includes(name)) {
        return mappedSymbol;
      }
    }

    const matches = text.match(/\b([A-Z]{2,5})\b/g);
    if (matches) {
      return matches[0];
    }

    return null;
  } catch (error) {
    console.error("LLM3 stock extraction failed:", error);
    return null;
  }
}

  async handleStockPredictionFromAPI(stockSymbol, years = 2) {
    try {
      const response = await fetch('http://localhost:8000/predict-stock', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: stockSymbol.toUpperCase(),
          years: years
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch predictions');
      }

      const predictionData = await response.json();
      
      // Check if there's an error in the response
      if (predictionData.error) {
        const errorMessage = this.createChatBotMessage(`📊 ${predictionData.message || predictionData.error}`);
        this.addMessage(errorMessage);
        return;
      }
      
      // Add stock chart widget message
      const stockMessage = this.createChatBotMessage(`📈 Stock Analysis for ${stockSymbol}`, {
        widget: "stockChart",
        payload: { 
          stockSymbol: stockSymbol.toUpperCase(),
          predictionData: predictionData,
          years: years
        }
      });
      
      this.addMessage(stockMessage);

    } catch (error) {
      console.error("Stock prediction error:", error);
      const errorMessage = this.createChatBotMessage(`📊 I found ${stockSymbol} in my analysis but couldn't get live prediction data. Please ensure the backend is running.`);
      this.addMessage(errorMessage);
    }
  }

  async handleStockPrediction(stockSymbol, years = 2) {
    // Add a simple test message with widget
    const message = this.createChatBotMessage(`📈 Stock Analysis for ${stockSymbol}`, {
      widget: "stockChart",
      payload: { 
        stockSymbol: stockSymbol.toUpperCase(),
        years: years
      }
    });
    
    this.addMessage(message);
  }

  async handleRiskAnalysis(userMessage) {
    // Add loading message
    this.setState((prev) => ({
      ...prev,
      messages: [...prev.messages, this.createChatBotMessage("🔍 Analyzing...")],
    }));

    // Get latest userData from state before making API call
    let userData = {};
    await new Promise((resolve) => {
      this.setState((prev) => {
        userData = prev.userData || {};
        resolve();
        return prev;
      });
    });

    try {
      const data = await callLLM1(userMessage, userData);
      
      // Update the loading message with LLM1 response
      let currentMessages = [];
      this.setState((prev) => {
        const messages = [...prev.messages];
        messages[messages.length - 1] = this.createChatBotMessage("", {
          widget: "markdownMessage",
          payload: { message: data }
        });
        currentMessages = messages; // Store messages for use outside setState
        return { ...prev, messages };
      });

      // Check if LLM1 response contains stock symbols
      const stockSymbol = await this.extractStockSymbolsFromText(data, userData);
      if (stockSymbol) {
        console.log(`Found stock symbol ${stockSymbol}, generating prediction...`);
        setTimeout(() => {
          this.handleStockPredictionFromAPI(stockSymbol, 2);
        }, 1000);
      }


    } catch (error) {
      console.error("Error:", error);
      this.setState((prev) => {
        const messages = [...prev.messages];
        messages[messages.length - 1] = this.createChatBotMessage("Sorry, I'm having trouble connecting to my backend. Please try again later.");
        return { ...prev, messages };
      });
    }
  }

  async handleExplanation(userMessage) {
    this.setState((prev) => ({
      ...prev,
      messages: [...prev.messages, this.createChatBotMessage("🔍 Analyzing...")],
    }));

    // Get latest userData from state before making API call
    let userData = {};
    await new Promise((resolve) => {
      this.setState((prev) => {
        userData = prev.userData || {};
        resolve();
        return prev;
      });
    });

    try {
      const data = await callLLM2(userMessage, userData);
      
      // Update the loading message with LLM2 response
      this.setState((prev) => {
        const messages = [...prev.messages];
        messages[messages.length - 1] = this.createChatBotMessage("", {
          widget: "markdownMessage",
          payload: { message: data }
        });
        return { ...prev, messages };
      });

      // Check if LLM2 response contains stock symbols
      const stockSymbol = await this.extractStockSymbolsFromText(data, userData);
      if (stockSymbol) {
        console.log(`Found stock symbol ${stockSymbol} in LLM2 response, generating prediction...`);
        
        // Add a brief delay to let the LLM2 response render first
        setTimeout(() => {
          this.handleStockPredictionFromAPI(stockSymbol, 2);
        }, 1000);
      }

    } catch (error) {
      console.error("Error:", error);
      this.setState((prev) => {
        const messages = [...prev.messages];
        messages[messages.length - 1] = this.createChatBotMessage("Sorry, I'm having trouble connecting to my backend. Please try again later.");
        return { ...prev, messages };
      });
    }
  }

    helloChat(){
        this.addMessage(this.createChatBotMessage("👋 Hello! How can i assist you?"));

    }
  exitChat(){
  const message = this.createChatBotMessage("👋 Goodbye! It was nice chatting with you.Feel free to ask me whatever you want!");
  this.addMessage(message);

  }

  async handleDefault(userMessage) {
    // 1. Always extract user info with LLM2
    let userData = {};
    await new Promise((resolve) => {
      this.setState((prev) => {
        userData = prev.userData || {};
        resolve();
        return prev;
      });
    });
    const extractionPrompt = `Extract all user profile information as JSON from: "${userMessage}". If nothing relevant, return an empty JSON object.`;
    let extractedObj = {};
    try {
      const llmExtracted = await callLLM2(extractionPrompt, userData);
      try {
        extractedObj = JSON.parse(llmExtracted);
      } catch (e) {
        // Not a valid JSON, skip
      }
      if (Object.keys(extractedObj).length > 0) {
        this.updateUserInfo(extractedObj);
        // Merge new fields into userData for next step
        userData = { ...userData, ...extractedObj };
      }
    } catch (e) {
      // Ignore extraction errors
    }

    // 2. If the message is a query (not just info update), call LLM1
    // Simple intent check: if message is exactly 'profile', 'show my data', or 'show my profile', skip LLM1
    const msg = userMessage.toLowerCase().trim();
    if (["profile", "show my data", "show my profile"].includes(msg)) {
      // Already handled by backend, do nothing here
      return;
    }

    // Otherwise, call LLM1 for advice
    this.setState((prev) => ({
      ...prev,
      messages: [...prev.messages, this.createChatBotMessage("🔍 Analyzing...")],
    }));
    try {
      const data = await callLLM1(userMessage, userData);
      this.setState((prev) => {
        const messages = [...prev.messages];
        messages[messages.length - 1] = this.createChatBotMessage("", {
          widget: "markdownMessage",
          payload: { message: data }
        });
        return { ...prev, messages };
      });
    } catch (error) {
      console.error("Error:", error);
      this.setState((prev) => {
        const messages = [...prev.messages];
        messages[messages.length - 1] = this.createChatBotMessage("Sorry, I'm having trouble connecting to my backend. Please try again later.");
        return { ...prev, messages };
      });
    }
  }
}

export default ActionProvider;
