import { useState, useEffect, useCallback } from 'react';
import type { KeyMapping } from '../types';

interface KeyMappingPanelProps {
  selectedButton: string | null;
  mapping?: KeyMapping;
  onMappingChange?: (buttonId: string, mapping: KeyMapping) => void;
  onClose?: () => void;
}

const COMMON_KEYS = [
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
  'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
  'Escape', 'Tab', 'Space', 'Enter', 'Backspace', 'Delete',
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  'Shift', 'Control', 'Alt', 'Meta',
];

const ACTION_TYPES = [
  { value: 'key', label: 'Single Key' },
  { value: 'combo', label: 'Key Combo' },
  { value: 'macro', label: 'Macro Sequence' },
  { value: 'none', label: 'Disabled' },
];

export function KeyMappingPanel({
  selectedButton,
  mapping,
  onMappingChange,
  onClose,
}: KeyMappingPanelProps) {
  const [actionType, setActionType] = useState<string>(mapping?.action || 'key');
  const [selectedKey, setSelectedKey] = useState<string>(mapping?.key || '');
  const [macroText, setMacroText] = useState<string>(mapping?.macro?.join(', ') || '');
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    if (mapping) {
      setActionType(mapping.action || 'key');
      setSelectedKey(mapping.key || '');
      setMacroText(mapping.macro?.join(', ') || '');
    } else {
      setActionType('key');
      setSelectedKey('');
      setMacroText('');
    }
  }, [mapping, selectedButton]);

  const handleKeyCapture = useCallback((e: KeyboardEvent) => {
    e.preventDefault();
    setSelectedKey(e.key);
    setIsListening(false);
  }, []);

  useEffect(() => {
    if (isListening) {
      window.addEventListener('keydown', handleKeyCapture);
      return () => window.removeEventListener('keydown', handleKeyCapture);
    }
  }, [isListening, handleKeyCapture]);

  const handleSave = () => {
    if (!selectedButton) return;

    const newMapping: KeyMapping = {
      key: selectedKey,
      action: actionType,
      macro: actionType === 'macro' ? macroText.split(',').map(s => s.trim()) : undefined,
    };

    onMappingChange?.(selectedButton, newMapping);
  };

  if (!selectedButton) {
    return (
      <div style={panelStyle}>
        <h3 style={titleStyle}>Key Mapping</h3>
        <p style={emptyStyle}>Click a button on the device to configure its mapping.</p>
      </div>
    );
  }

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <h3 style={titleStyle}>Configure {selectedButton}</h3>
        {onClose && (
          <button onClick={onClose} style={closeButtonStyle}>×</button>
        )}
      </div>

      <div style={fieldStyle}>
        <label style={labelStyle}>Action Type</label>
        <select
          value={actionType}
          onChange={(e) => setActionType(e.target.value)}
          style={selectStyle}
        >
          {ACTION_TYPES.map(({ value, label }) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {actionType !== 'none' && actionType !== 'macro' && (
        <div style={fieldStyle}>
          <label style={labelStyle}>Key</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              value={selectedKey}
              readOnly
              placeholder="Press a key or select below"
              style={{ ...inputStyle, flex: 1 }}
            />
            <button
              onClick={() => setIsListening(!isListening)}
              style={{
                ...buttonStyle,
                backgroundColor: isListening ? '#ff6b00' : '#444',
              }}
            >
              {isListening ? 'Listening...' : 'Capture'}
            </button>
          </div>

          <div style={keyGridStyle}>
            {COMMON_KEYS.slice(0, 26).map((key) => (
              <button
                key={key}
                onClick={() => setSelectedKey(key)}
                style={{
                  ...keyButtonStyle,
                  backgroundColor: selectedKey === key ? '#ff6b00' : '#333',
                }}
              >
                {key.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      )}

      {actionType === 'macro' && (
        <div style={fieldStyle}>
          <label style={labelStyle}>Macro Sequence (comma-separated)</label>
          <textarea
            value={macroText}
            onChange={(e) => setMacroText(e.target.value)}
            placeholder="e.g., Ctrl, c, delay:100, Ctrl, v"
            style={textareaStyle}
          />
        </div>
      )}

      <div style={buttonRowStyle}>
        <button onClick={handleSave} style={{ ...buttonStyle, backgroundColor: '#ff6b00' }}>
          Save Mapping
        </button>
        <button onClick={onClose} style={buttonStyle}>
          Cancel
        </button>
      </div>
    </div>
  );
}

// Styles
const panelStyle: React.CSSProperties = {
  backgroundColor: '#1e1e1e',
  border: '1px solid #333',
  borderRadius: '8px',
  padding: '16px',
  minWidth: '300px',
  color: '#eee',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '16px',
};

const titleStyle: React.CSSProperties = {
  margin: 0,
  color: '#ff6b00',
  fontSize: '18px',
};

const closeButtonStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: '#888',
  fontSize: '24px',
  cursor: 'pointer',
  padding: '0 4px',
};

const emptyStyle: React.CSSProperties = {
  color: '#888',
  fontStyle: 'italic',
};

const fieldStyle: React.CSSProperties = {
  marginBottom: '16px',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: '6px',
  color: '#aaa',
  fontSize: '13px',
};

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px',
  backgroundColor: '#2a2a2a',
  border: '1px solid #444',
  borderRadius: '4px',
  color: '#eee',
  fontSize: '14px',
};

const inputStyle: React.CSSProperties = {
  padding: '8px',
  backgroundColor: '#2a2a2a',
  border: '1px solid #444',
  borderRadius: '4px',
  color: '#eee',
  fontSize: '14px',
};

const textareaStyle: React.CSSProperties = {
  width: '100%',
  minHeight: '80px',
  padding: '8px',
  backgroundColor: '#2a2a2a',
  border: '1px solid #444',
  borderRadius: '4px',
  color: '#eee',
  fontSize: '14px',
  fontFamily: 'monospace',
  resize: 'vertical',
};

const buttonStyle: React.CSSProperties = {
  padding: '8px 16px',
  backgroundColor: '#444',
  border: 'none',
  borderRadius: '4px',
  color: '#eee',
  fontSize: '14px',
  cursor: 'pointer',
};

const buttonRowStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
  marginTop: '16px',
};

const keyGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(13, 1fr)',
  gap: '4px',
  marginTop: '8px',
};

const keyButtonStyle: React.CSSProperties = {
  padding: '6px',
  backgroundColor: '#333',
  border: '1px solid #444',
  borderRadius: '3px',
  color: '#eee',
  fontSize: '11px',
  cursor: 'pointer',
  minWidth: '20px',
};
