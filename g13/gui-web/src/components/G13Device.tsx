import { useState, useCallback } from 'react';
import { G13Button } from './G13Button';
import './G13Device.css';

interface G13DeviceProps {
  selectedButton?: string | null;
  activeMode?: 'M1' | 'M2' | 'M3';
  pressedKeys?: Set<string>;
  onButtonClick?: (buttonId: string) => void;
  onButtonRightClick?: (buttonId: string, e: React.MouseEvent) => void;
  onModeChange?: (mode: 'M1' | 'M2' | 'M3') => void;
  onJoystickMove?: (x: number, y: number) => void;
  lcdContent?: React.ReactNode;
}

export function G13Device({
  selectedButton = null,
  activeMode = 'M1',
  pressedKeys = new Set(),
  onButtonClick,
  onButtonRightClick,
  onModeChange,
  onJoystickMove,
  lcdContent,
}: G13DeviceProps) {
  const [joystickPos, setJoystickPos] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);

  const handleModeClick = useCallback((id: string) => {
    if (id === 'M1' || id === 'M2' || id === 'M3') {
      onModeChange?.(id);
    }
    onButtonClick?.(id);
  }, [onModeChange, onButtonClick]);

  const handleJoystickMouseDown = () => setIsDragging(true);

  const handleJoystickMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const maxOffset = rect.width / 3;

    let x = e.clientX - rect.left - centerX;
    let y = e.clientY - rect.top - centerY;

    const distance = Math.sqrt(x * x + y * y);
    if (distance > maxOffset) {
      x = (x / distance) * maxOffset;
      y = (y / distance) * maxOffset;
    }

    setJoystickPos({ x, y });
    onJoystickMove?.(x / maxOffset, y / maxOffset);
  }, [isDragging, onJoystickMove]);

  const handleJoystickMouseUp = useCallback(() => {
    setIsDragging(false);
    setJoystickPos({ x: 0, y: 0 });
    onJoystickMove?.(0, 0);
  }, [onJoystickMove]);

  const renderButton = (id: string, type: 'g-key' | 'm-key' | 'thumb' = 'g-key') => (
    <G13Button
      key={id}
      id={id}
      type={type}
      label={id}
      isActive={type === 'm-key' ? id === activeMode : pressedKeys.has(id)}
      isSelected={selectedButton === id}
      onClick={type === 'm-key' ? handleModeClick : onButtonClick}
      onContextMenu={onButtonRightClick}
    />
  );

  return (
    <div className="g13-device">
      {/* Top section with LCD */}
      <div className="g13-top">
        <div className="g13-lcd">
          {lcdContent || <span>G13 READY</span>}
        </div>
      </div>

      {/* M-keys row */}
      <div className="g13-mkeys">
        {renderButton('M1', 'm-key')}
        {renderButton('M2', 'm-key')}
        {renderButton('M3', 'm-key')}
        {renderButton('MR', 'm-key')}
      </div>

      {/* Main key grid */}
      <div className="g13-main">
        <div className="g13-keys">
          {/* Row 1: G1-G7 */}
          <div className="g13-row">
            {['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7'].map(id => renderButton(id))}
          </div>

          {/* Row 2: G8-G14 */}
          <div className="g13-row">
            {['G8', 'G9', 'G10', 'G11', 'G12', 'G13', 'G14'].map(id => renderButton(id))}
          </div>

          {/* Row 3: G15-G19 (offset) */}
          <div className="g13-row g13-row-offset">
            {['G15', 'G16', 'G17', 'G18', 'G19'].map(id => renderButton(id))}
          </div>

          {/* Row 4: G20-G22 (centered, wider) */}
          <div className="g13-row g13-row-bottom">
            {['G20', 'G21', 'G22'].map(id => renderButton(id))}
          </div>
        </div>

        {/* Thumb area */}
        <div className="g13-thumb">
          <div
            className="g13-joystick-area"
            onMouseDown={handleJoystickMouseDown}
            onMouseMove={handleJoystickMouseMove}
            onMouseUp={handleJoystickMouseUp}
            onMouseLeave={handleJoystickMouseUp}
          >
            <div
              className={`g13-joystick ${isDragging ? 'active' : ''}`}
              style={{ transform: `translate(${joystickPos.x}px, ${joystickPos.y}px)` }}
            />
          </div>
          <div className="g13-thumb-buttons">
            {renderButton('LEFT', 'thumb')}
            {renderButton('DOWN', 'thumb')}
          </div>
        </div>
      </div>

      {/* Base/palm rest visual */}
      <div className="g13-base" />
    </div>
  );
}
