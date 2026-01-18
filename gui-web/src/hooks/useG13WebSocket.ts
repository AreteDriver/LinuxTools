import { useEffect, useRef, useState, useCallback } from 'react';

const WS_URL = 'ws://127.0.0.1:8765/ws';

export interface G13State {
  connected: boolean;
  active_profile: string | null;
  active_mode: 'M1' | 'M2' | 'M3';
  pressed_keys: string[];
  joystick: { x: number; y: number };
  backlight: { color: string; brightness: number };
}

export interface G13WebSocketHook {
  state: G13State;
  wsConnected: boolean;
  sendMessage: (message: object) => void;
  setMode: (mode: 'M1' | 'M2' | 'M3') => void;
  setMapping: (button: string, key: string) => void;
  simulatePress: (button: string) => void;
  simulateRelease: (button: string) => void;
  setBacklight: (color: string, brightness?: number) => void;
}

const initialState: G13State = {
  connected: false,
  active_profile: null,
  active_mode: 'M1',
  pressed_keys: [],
  joystick: { x: 0, y: 0 },
  backlight: { color: '#ff6b00', brightness: 100 },
};

export function useG13WebSocket(): G13WebSocketHook {
  const [state, setState] = useState<G13State>(initialState);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
      // Request current state
      ws.send(JSON.stringify({ type: 'get_state' }));
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      // Reconnect after 2 seconds
      reconnectTimeoutRef.current = setTimeout(connect, 2000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleMessage(message);
      } catch (e) {
        console.error('Failed to parse message:', e);
      }
    };

    wsRef.current = ws;
  }, []);

  const handleMessage = useCallback((message: { type: string; [key: string]: unknown }) => {
    switch (message.type) {
      case 'state':
        setState(message.data as G13State);
        break;

      case 'button_pressed':
        setState((prev) => ({
          ...prev,
          pressed_keys: [...prev.pressed_keys, message.button as string],
        }));
        break;

      case 'button_released':
        setState((prev) => ({
          ...prev,
          pressed_keys: prev.pressed_keys.filter((k) => k !== message.button),
        }));
        break;

      case 'mode_changed':
        setState((prev) => ({
          ...prev,
          active_mode: message.mode as 'M1' | 'M2' | 'M3',
        }));
        break;

      case 'profile_activated':
        setState((prev) => ({
          ...prev,
          active_profile: message.name as string,
        }));
        break;

      case 'backlight_changed':
        setState((prev) => ({
          ...prev,
          backlight: message.backlight as { color: string; brightness: number },
        }));
        break;

      case 'device_connected':
        setState((prev) => ({ ...prev, connected: true }));
        break;

      case 'device_disconnected':
        setState((prev) => ({ ...prev, connected: false }));
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const setMode = useCallback((mode: 'M1' | 'M2' | 'M3') => {
    sendMessage({ type: 'set_mode', mode });
  }, [sendMessage]);

  const setMapping = useCallback((button: string, key: string) => {
    sendMessage({ type: 'set_mapping', button, key });
  }, [sendMessage]);

  const simulatePress = useCallback((button: string) => {
    sendMessage({ type: 'simulate_press', button });
  }, [sendMessage]);

  const simulateRelease = useCallback((button: string) => {
    sendMessage({ type: 'simulate_release', button });
  }, [sendMessage]);

  const setBacklight = useCallback((color: string, brightness?: number) => {
    sendMessage({ type: 'set_backlight', color, brightness });
  }, [sendMessage]);

  return {
    state,
    wsConnected,
    sendMessage,
    setMode,
    setMapping,
    simulatePress,
    simulateRelease,
    setBacklight,
  };
}
