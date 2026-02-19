const API_BASE = 'http://127.0.0.1:8765/api';

export interface Profile {
  name: string;
  description?: string;
  mappings: Record<string, string | { keys: string[]; label: string }>;
  backlight?: { color: string; brightness: number };
  joystick?: { mode: string; deadzone: number };
}

export interface ProfileListItem {
  name: string;
  filename: string;
  description: string;
}

export interface Macro {
  id: string;
  name: string;
  description?: string;
  steps: MacroStep[];
  speed_multiplier?: number;
  repeat_count?: number;
}

export interface MacroStep {
  type: 'key_press' | 'key_release' | 'delay';
  value: string | number;
  is_press?: boolean;
  timestamp_ms?: number;
}

export interface MacroListItem {
  id: string;
  name: string;
  description: string;
  steps_count: number;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Profile API

export async function listProfiles(): Promise<ProfileListItem[]> {
  const data = await fetchJson<{ profiles: ProfileListItem[] }>(`${API_BASE}/profiles`);
  return data.profiles;
}

export async function getProfile(name: string): Promise<Profile> {
  return fetchJson<Profile>(`${API_BASE}/profiles/${encodeURIComponent(name)}`);
}

export async function saveProfile(name: string, profile: Partial<Profile>): Promise<void> {
  await fetchJson(`${API_BASE}/profiles/${encodeURIComponent(name)}`, {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

export async function deleteProfile(name: string): Promise<void> {
  await fetchJson(`${API_BASE}/profiles/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  });
}

export async function activateProfile(name: string): Promise<void> {
  await fetchJson(`${API_BASE}/profiles/${encodeURIComponent(name)}/activate`, {
    method: 'POST',
  });
}

// Macro API

export async function listMacros(): Promise<MacroListItem[]> {
  const data = await fetchJson<{ macros: MacroListItem[] }>(`${API_BASE}/macros`);
  return data.macros;
}

export async function getMacro(id: string): Promise<Macro> {
  return fetchJson<Macro>(`${API_BASE}/macros/${encodeURIComponent(id)}`);
}

export async function createMacro(macro: Omit<Macro, 'id'>): Promise<{ id: string }> {
  return fetchJson<{ id: string }>(`${API_BASE}/macros`, {
    method: 'POST',
    body: JSON.stringify(macro),
  });
}

export async function deleteMacro(id: string): Promise<void> {
  await fetchJson(`${API_BASE}/macros/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}

// Status API

export async function getDeviceStatus(): Promise<{
  connected: boolean;
  active_profile: string | null;
  active_mode: string;
}> {
  return fetchJson(`${API_BASE}/status`);
}
