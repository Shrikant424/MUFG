export const sendChatMessage = async (message, userProfile, messageHistory) => {
  // Mock chat API - replace with actual implementation
  return new Promise((resolve) => {
    setTimeout(() => {
      let response = "I'm here to help with your superannuation questions. ";
      
      if (message.toLowerCase().includes('investment')) {
        response = "Based on your profile, I'd recommend a balanced investment approach. Your risk tolerance and time horizon suggest a mix of growth and defensive assets would be suitable.";
      } else if (message.toLowerCase().includes('retirement')) {
        response = `With ${userProfile?.retirement_age_goal - userProfile?.age || 30} years until retirement, you have time to focus on growth investments while gradually becoming more conservative as you approach retirement.`;
      } else if (message.toLowerCase().includes('risk')) {
        response = "Risk management is crucial for long-term success. Your current risk profile suggests you can handle moderate volatility for potentially higher returns.";
      } else {
        response = "I can help you with investment strategies, risk assessment, retirement planning, and superannuation advice. What specific aspect would you like to discuss?";
      }
      
      resolve({ response });
    }, 1500);
  });
};