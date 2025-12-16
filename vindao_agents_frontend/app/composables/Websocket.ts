

export const useWebsocket = (onmessage) => {
  const ws = new WebSocket('ws://localhost:8000/ws');

  ws.onopen = () => {
    console.log('WebSocket connection established');
  };

ws.onmessage = onmessage

  ws.onclose = () => {
    console.log('WebSocket connection closed');
  };

  ws.onerror = (error) => {
    console.error('WebSocket error: ', error);
  };

  const sendMessage = (message: string) => {
    ws.send(message);
  };

  return {
    sendMessage,
  };
}