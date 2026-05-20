import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url) {
  const [data, setData]     = useState(null);
  const [status, setStatus] = useState('connecting');
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(url);
    ws.current.onopen    = () => setStatus('connected');
    ws.current.onclose   = () => setStatus('disconnected');
    ws.current.onerror   = () => setStatus('error');
    ws.current.onmessage = e  => setData(JSON.parse(e.data));
    return () => ws.current?.close();
  }, [url]);

  return { data, status };
}
