const extractTextAndSend = async () => {
    const textElements = document.querySelectorAll('.LC20lb.MBeuO.DKV0Md');
  
    for (let el of textElements) {
      const text = el.innerText;
  
      try {
        console.log("[DEBUG] Sending text:", text);
  
        const response = await fetch('http://localhost:5000/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text })
        });
  
        const result = await response.json();
        console.log("[DEBUG] Response from server:", result);
  
        if (result.predicted_class === 1) {
          el.style.setProperty('color', 'red', 'important');
        }
      } catch (error) {
        console.error('[ERROR] Failed to send to prediction API:', error);
      }
    }
  };
  
  extractTextAndSend();
