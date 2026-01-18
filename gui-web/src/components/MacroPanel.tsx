import { useState, useEffect, useCallback } from 'react';
import { listMacros, getMacro, createMacro, deleteMacro, type MacroListItem, type Macro, type MacroStep } from '../api/g13Api';
import './MacroPanel.css';

interface MacroPanelProps {
  onAssignMacro?: (macroId: string, buttonId: string) => void;
  selectedButton?: string | null;
}

export function MacroPanel({ onAssignMacro, selectedButton }: MacroPanelProps) {
  const [macros, setMacros] = useState<MacroListItem[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedSteps, setRecordedSteps] = useState<MacroStep[]>([]);
  const [recordingName, setRecordingName] = useState('');
  const [selectedMacro, setSelectedMacro] = useState<Macro | null>(null);
  const [recordStartTime, setRecordStartTime] = useState<number>(0);

  // Load macros on mount
  useEffect(() => {
    loadMacros();
  }, []);

  const loadMacros = async () => {
    try {
      const list = await listMacros();
      setMacros(list);
    } catch (e) {
      console.error('Failed to load macros:', e);
    }
  };

  const handleStartRecording = useCallback(() => {
    setIsRecording(true);
    setRecordedSteps([]);
    setRecordStartTime(Date.now());
    setRecordingName(`Macro ${new Date().toLocaleTimeString()}`);
  }, []);

  const handleStopRecording = useCallback(async () => {
    setIsRecording(false);

    if (recordedSteps.length === 0) {
      return;
    }

    const name = prompt('Macro name:', recordingName);
    if (!name) return;

    try {
      await createMacro({
        name,
        description: `Recorded ${recordedSteps.length} steps`,
        steps: recordedSteps,
        speed_multiplier: 1.0,
        repeat_count: 1,
      });
      await loadMacros();
      setRecordedSteps([]);
    } catch (e) {
      alert(`Failed to save macro: ${e}`);
    }
  }, [recordedSteps, recordingName]);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isRecording) return;

    // Ignore modifier-only presses
    if (['Control', 'Shift', 'Alt', 'Meta'].includes(e.key)) return;

    e.preventDefault();

    const step: MacroStep = {
      type: 'key_press',
      value: e.code,
      is_press: true,
      timestamp_ms: Date.now() - recordStartTime,
    };

    setRecordedSteps((prev) => [...prev, step]);
  }, [isRecording, recordStartTime]);

  const handleKeyUp = useCallback((e: KeyboardEvent) => {
    if (!isRecording) return;
    if (['Control', 'Shift', 'Alt', 'Meta'].includes(e.key)) return;

    const step: MacroStep = {
      type: 'key_release',
      value: e.code,
      is_press: false,
      timestamp_ms: Date.now() - recordStartTime,
    };

    setRecordedSteps((prev) => [...prev, step]);
  }, [isRecording, recordStartTime]);

  useEffect(() => {
    if (isRecording) {
      window.addEventListener('keydown', handleKeyDown);
      window.addEventListener('keyup', handleKeyUp);
      return () => {
        window.removeEventListener('keydown', handleKeyDown);
        window.removeEventListener('keyup', handleKeyUp);
      };
    }
  }, [isRecording, handleKeyDown, handleKeyUp]);

  const handleViewMacro = async (id: string) => {
    try {
      const macro = await getMacro(id);
      setSelectedMacro(macro);
    } catch (e) {
      console.error('Failed to load macro:', e);
    }
  };

  const handleDeleteMacro = async (id: string) => {
    if (!confirm('Delete this macro?')) return;
    try {
      await deleteMacro(id);
      await loadMacros();
      if (selectedMacro?.id === id) {
        setSelectedMacro(null);
      }
    } catch (e) {
      alert(`Failed to delete: ${e}`);
    }
  };

  const handleAssign = (macroId: string) => {
    if (selectedButton && onAssignMacro) {
      onAssignMacro(macroId, selectedButton);
    }
  };

  return (
    <div className="macro-panel">
      <h4>Macros</h4>

      {/* Recording controls */}
      <div className="macro-record-section">
        {!isRecording ? (
          <button className="record-btn" onClick={handleStartRecording}>
            <span className="record-icon">●</span> Start Recording
          </button>
        ) : (
          <div className="recording-active">
            <div className="recording-indicator">
              <span className="record-icon recording">●</span>
              Recording... ({recordedSteps.length} steps)
            </div>
            <button className="stop-btn" onClick={handleStopRecording}>
              ■ Stop
            </button>
          </div>
        )}
      </div>

      {/* Recording preview */}
      {isRecording && recordedSteps.length > 0 && (
        <div className="recording-preview">
          <div className="steps-list">
            {recordedSteps.slice(-5).map((step, i) => (
              <div key={i} className="step-item">
                <span className={`step-type ${step.type}`}>
                  {step.type === 'key_press' ? '↓' : '↑'}
                </span>
                <span className="step-value">{String(step.value)}</span>
                <span className="step-time">{step.timestamp_ms}ms</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Macro list */}
      <div className="macro-list">
        {macros.length === 0 ? (
          <p className="empty">No macros saved</p>
        ) : (
          macros.map((m) => (
            <div
              key={m.id}
              className={`macro-item ${selectedMacro?.id === m.id ? 'selected' : ''}`}
              onClick={() => handleViewMacro(m.id)}
            >
              <div className="macro-info">
                <span className="macro-name">{m.name}</span>
                <span className="macro-steps">{m.steps_count} steps</span>
              </div>
              <div className="macro-actions">
                {selectedButton && (
                  <button
                    className="assign-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAssign(m.id);
                    }}
                    title={`Assign to ${selectedButton}`}
                  >
                    →
                  </button>
                )}
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteMacro(m.id);
                  }}
                  title="Delete"
                >
                  ×
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Macro detail view */}
      {selectedMacro && (
        <div className="macro-detail">
          <h5>{selectedMacro.name}</h5>
          <div className="steps-list">
            {selectedMacro.steps.slice(0, 10).map((step, i) => (
              <div key={i} className="step-item">
                <span className={`step-type ${step.type}`}>
                  {step.type === 'key_press' ? '↓' : step.type === 'key_release' ? '↑' : '⏱'}
                </span>
                <span className="step-value">{String(step.value)}</span>
                <span className="step-time">{step.timestamp_ms}ms</span>
              </div>
            ))}
            {selectedMacro.steps.length > 10 && (
              <div className="step-item more">
                +{selectedMacro.steps.length - 10} more steps
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
