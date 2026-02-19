import { useState, useCallback, useEffect } from 'react';
import { G13Device } from './components/G13Device';
import { KeyMappingPanel } from './components/KeyMappingPanel';
import { MacroPanel } from './components/MacroPanel';
import { useG13WebSocket } from './hooks/useG13WebSocket';
import { listProfiles, saveProfile, activateProfile, type ProfileListItem } from './api/g13Api';
import type { KeyMapping } from './types';
import './App.css';

function App() {
  const { state, wsConnected, setMode, simulatePress, simulateRelease, setBacklight } = useG13WebSocket();

  const [selectedButton, setSelectedButton] = useState<string | null>(null);
  const [keyMappings, setKeyMappings] = useState<Record<string, KeyMapping>>({});
  const [profiles, setProfiles] = useState<ProfileListItem[]>([]);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  // Load profiles on mount
  useEffect(() => {
    listProfiles()
      .then(setProfiles)
      .catch((e) => console.error('Failed to load profiles:', e));
  }, []);

  const handleButtonClick = useCallback((buttonId: string) => {
    setSelectedButton(buttonId);
  }, []);

  const handleButtonRightClick = useCallback((buttonId: string) => {
    // Toggle simulated press via WebSocket
    if (state.pressed_keys.includes(buttonId)) {
      simulateRelease(buttonId);
    } else {
      simulatePress(buttonId);
    }
  }, [state.pressed_keys, simulatePress, simulateRelease]);

  const handleModeChange = useCallback((mode: 'M1' | 'M2' | 'M3') => {
    setMode(mode);
  }, [setMode]);

  const handleMappingChange = useCallback((buttonId: string, mapping: KeyMapping) => {
    setKeyMappings((prev) => ({
      ...prev,
      [buttonId]: mapping,
    }));
  }, []);

  const handleClosePanel = useCallback(() => {
    setSelectedButton(null);
  }, []);

  const handleSaveProfile = useCallback(async () => {
    const name = prompt('Profile name:', state.active_profile || 'My Profile');
    if (!name) return;

    try {
      await saveProfile(name, {
        name,
        description: 'Created from Web GUI',
        mappings: Object.fromEntries(
          Object.entries(keyMappings).map(([btn, m]) => [btn, m.key || 'KEY_RESERVED'])
        ),
      });
      const updated = await listProfiles();
      setProfiles(updated);
      alert(`Profile "${name}" saved!`);
    } catch (e) {
      alert(`Failed to save: ${e}`);
    }
  }, [keyMappings, state.active_profile]);

  const handleLoadProfile = useCallback(async (name: string) => {
    try {
      await activateProfile(name);
      setShowProfileMenu(false);
    } catch (e) {
      alert(`Failed to load: ${e}`);
    }
  }, []);

  const lcdContent = (
    <div style={{ textAlign: 'center', padding: '4px' }}>
      <div style={{ fontSize: '9px' }}>
        {state.active_profile || 'No Profile'}
      </div>
      <div style={{ fontSize: '8px', marginTop: '2px' }}>
        Mode: {state.active_mode}
      </div>
    </div>
  );

  const pressedKeysSet = new Set(state.pressed_keys);

  return (
    <div className="app">
      <header className="header">
        <h1>G13 Linux - Key Mapper</h1>
        <div className="header-status">
          <span className={`status-dot ${wsConnected ? 'connected' : 'disconnected'}`} />
          <span className="status-text">
            {wsConnected ? (state.connected ? 'Device Connected' : 'Simulated') : 'Offline'}
          </span>
        </div>
        <div className="header-actions">
          <div className="profile-dropdown">
            <button
              className="header-btn"
              onClick={() => setShowProfileMenu(!showProfileMenu)}
            >
              Load Profile
            </button>
            {showProfileMenu && (
              <div className="profile-menu">
                {profiles.length === 0 ? (
                  <div className="profile-menu-item empty">No profiles</div>
                ) : (
                  profiles.map((p) => (
                    <button
                      key={p.name}
                      className="profile-menu-item"
                      onClick={() => handleLoadProfile(p.name)}
                    >
                      {p.name}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
          <button className="header-btn" onClick={handleSaveProfile}>
            Save Profile
          </button>
        </div>
      </header>

      <main className="main">
        <section className="device-section">
          <G13Device
            selectedButton={selectedButton}
            activeMode={state.active_mode}
            pressedKeys={pressedKeysSet}
            onButtonClick={handleButtonClick}
            onButtonRightClick={handleButtonRightClick}
            onModeChange={handleModeChange}
            lcdContent={lcdContent}
          />
          <p className="hint">
            Click a button to configure • Right-click to test press
          </p>
        </section>

        <aside className="panel-section">
          <KeyMappingPanel
            selectedButton={selectedButton}
            mapping={selectedButton ? keyMappings[selectedButton] : undefined}
            onMappingChange={handleMappingChange}
            onClose={handleClosePanel}
          />

          <div className="mappings-preview">
            <h4>Current Mappings ({state.active_mode})</h4>
            {Object.entries(keyMappings).length === 0 ? (
              <p className="empty">No mappings configured</p>
            ) : (
              <ul>
                {Object.entries(keyMappings).map(([btn, mapping]) => (
                  <li key={btn}>
                    <strong>{btn}</strong>: {mapping.key || mapping.action}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Macro panel */}
          <MacroPanel
            selectedButton={selectedButton}
            onAssignMacro={(macroId, buttonId) => {
              setKeyMappings((prev) => ({
                ...prev,
                [buttonId]: { key: `MACRO:${macroId}`, action: 'macro' },
              }));
            }}
          />

          {/* Backlight control */}
          <div className="backlight-control">
            <h4>Backlight</h4>
            <div className="backlight-row">
              <input
                type="color"
                value={state.backlight.color}
                onChange={(e) => setBacklight(e.target.value, state.backlight.brightness)}
                title="Backlight Color"
              />
              <input
                type="range"
                min="0"
                max="100"
                value={state.backlight.brightness}
                onChange={(e) => setBacklight(state.backlight.color, Number(e.target.value))}
                title="Brightness"
              />
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;
