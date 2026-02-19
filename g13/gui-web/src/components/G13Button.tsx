import { useState } from 'react';
import type { ButtonType } from '../types';

interface G13ButtonProps {
  id: string;
  type: ButtonType;
  label?: string;
  isActive?: boolean;
  isSelected?: boolean;
  onClick?: (id: string) => void;
  onContextMenu?: (id: string, e: React.MouseEvent) => void;
}

export function G13Button({
  id,
  type,
  label,
  isActive = false,
  isSelected = false,
  onClick,
  onContextMenu,
}: G13ButtonProps) {
  const [isPressed, setIsPressed] = useState(false);

  const handleMouseDown = () => setIsPressed(true);
  const handleMouseUp = () => setIsPressed(false);
  const handleMouseLeave = () => setIsPressed(false);

  const handleClick = () => onClick?.(id);
  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    onContextMenu?.(id, e);
  };

  const classNames = [
    'g13-btn',
    `g13-btn-${type}`,
    isPressed || isActive ? 'active' : '',
    isSelected ? 'selected' : '',
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classNames}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      title={id}
    >
      {label}
    </button>
  );
}
