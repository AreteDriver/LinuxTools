export interface ButtonPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface KeyMapping {
  key: string;
  action: string;
  macro?: string[];
}

export interface G13State {
  activeProfile: string;
  modeKey: 'M1' | 'M2' | 'M3';
  pressedKeys: Set<string>;
  joystickPosition: { x: number; y: number };
  keyMappings: Record<string, KeyMapping>;
}

export type ButtonType = 'g-key' | 'm-key' | 'thumb';
