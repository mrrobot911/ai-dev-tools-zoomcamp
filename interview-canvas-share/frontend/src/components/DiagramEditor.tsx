import { useRef, useState, useCallback, useEffect } from 'react';
import type { DiagramElement, DiagramState } from '../types';

interface DiagramEditorProps {
  state: DiagramState;
  onAddElement: (element: Omit<DiagramElement, 'id'>) => void;
  onUpdateElement: (elementId: string, updates: Partial<DiagramElement>) => void;
  onRemoveElement: (elementId: string) => void;
  readonly?: boolean;
}

type DragState =
  | { kind: 'move'; elementId: string; offsetX: number; offsetY: number }
  | { kind: 'resize'; elementId: string; handle: string; startX: number; startY: number; origW: number; origH: number; origX: number; origY: number }
  | { kind: 'connect'; fromId: string; mouseX: number; mouseY: number }
  | null;

const BOX_W = 140;
const BOX_H = 60;

export default function DiagramEditor({
  state,
  onAddElement,
  onUpdateElement,
  onRemoveElement,
  readonly = false,
}: DiagramEditorProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [drag, setDrag] = useState<DragState>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editingLabelId, setEditingLabelId] = useState<string | null>(null);
  const [editingTextId, setEditingTextId] = useState<string | null>(null);

  const getSvgPoint = useCallback((clientX: number, clientY: number) => {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const rect = svg.getBoundingClientRect();
    return { x: clientX - rect.left, y: clientY - rect.top };
  }, []);

  function handleCanvasDoubleClick(e: React.MouseEvent) {
    if (readonly) return;
    const pt = getSvgPoint(e.clientX, e.clientY);
    onAddElement({
      type: 'box',
      x: pt.x - BOX_W / 2,
      y: pt.y - BOX_H / 2,
      width: BOX_W,
      height: BOX_H,
      label: 'New Box',
    });
  }

  function handleBoxMouseDown(e: React.MouseEvent, element: DiagramElement) {
    if (readonly) return;
    e.stopPropagation();
    setSelectedId(element.id);
    if (drag?.kind === 'connect') {
      onAddElement({
        type: 'arrow',
        fromId: drag.fromId,
        toId: element.id,
      });
      setDrag(null);
      return;
    }
    const pt = getSvgPoint(e.clientX, e.clientY);
    setDrag({
      kind: 'move',
      elementId: element.id,
      offsetX: pt.x - (element.x ?? 0),
      offsetY: pt.y - (element.y ?? 0),
    });
  }

  function handleResizeMouseDown(e: React.MouseEvent, element: DiagramElement) {
    if (readonly) return;
    e.stopPropagation();
    setDrag({
      kind: 'resize',
      elementId: element.id,
      handle: 'br',
      startX: e.clientX,
      startY: e.clientY,
      origW: element.width ?? BOX_W,
      origH: element.height ?? BOX_H,
      origX: element.x ?? 0,
      origY: element.y ?? 0,
    });
  }

  function handleConnectMouseDown(e: React.MouseEvent, element: DiagramElement) {
    if (readonly) return;
    e.stopPropagation();
    const pt = getSvgPoint(e.clientX, e.clientY);
    setDrag({ kind: 'connect', fromId: element.id, mouseX: pt.x, mouseY: pt.y });
  }

  useEffect(() => {
    if (!drag) return;
    const currentDrag = drag;

    function handleMove(e: MouseEvent) {
      const pt = getSvgPoint(e.clientX, e.clientY);
      if (currentDrag.kind === 'move') {
        onUpdateElement(currentDrag.elementId, {
          x: pt.x - currentDrag.offsetX,
          y: pt.y - currentDrag.offsetY,
        });
      } else if (currentDrag.kind === 'resize') {
        const newW = Math.max(40, currentDrag.origW + (e.clientX - currentDrag.startX));
        const newH = Math.max(30, currentDrag.origH + (e.clientY - currentDrag.startY));
        onUpdateElement(currentDrag.elementId, { width: newW, height: newH });
      } else if (currentDrag.kind === 'connect') {
        setDrag({ ...currentDrag, mouseX: pt.x, mouseY: pt.y });
      }
    }

    function handleUp() {
      setDrag(null);
    }


    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [drag, getSvgPoint, onUpdateElement]);


  function handleSvgClick(_e: React.MouseEvent) {
    if (drag?.kind === 'connect') {
      setDrag(null);
      return;
    }
    setSelectedId(null);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId && !readonly) {
      const active = document.activeElement;
      if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return;
      e.preventDefault();
      onRemoveElement(selectedId);
      setSelectedId(null);
    }
  }

  const boxes = state.elements.filter((el) => el.type === 'box');
  const arrows = state.elements.filter((el) => el.type === 'arrow');
  const texts = state.elements.filter((el) => el.type === 'text');

  function getBoxCenter(el: DiagramElement) {
    return {
      x: (el.x ?? 0) + (el.width ?? BOX_W) / 2,
      y: (el.y ?? 0) + (el.height ?? BOX_H) / 2,
    };
  }

  function getBoxById(id: string): DiagramElement | undefined {
    return boxes.find((b) => b.id === id);
  }

  return (
    <div
      style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ background: 'var(--color-bg)', cursor: readonly ? 'default' : 'crosshair', display: 'block' }}
        onDoubleClick={handleCanvasDoubleClick}
        onClick={handleSvgClick}
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="var(--color-text-muted)" />
          </marker>
        </defs>

        {/* Grid pattern */}
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <circle cx="10" cy="10" r="0.5" fill="var(--color-border)" />
        </pattern>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Arrows */}
        {arrows.map((arrow) => {
          const from = getBoxById(arrow.fromId ?? '');
          const to = getBoxById(arrow.toId ?? '');
          if (!from || !to) return null;
          const fromCenter = getBoxCenter(from);
          const toCenter = getBoxCenter(to);
          return (
            <g key={arrow.id} onClick={(e) => { e.stopPropagation(); setSelectedId(arrow.id); }}>
              <line
                x1={fromCenter.x}
                y1={fromCenter.y}
                x2={toCenter.x}
                y2={toCenter.y}
                stroke={selectedId === arrow.id ? 'var(--color-primary)' : 'var(--color-text-muted)'}
                strokeWidth={selectedId === arrow.id ? 2.5 : 2}
                markerEnd="url(#arrowhead)"
              />
            </g>
          );
        })}

        {/* Temp arrow while connecting */}
        {drag?.kind === 'connect' && (() => {
          const from = getBoxById(drag.fromId);
          if (!from) return null;
          const fromCenter = getBoxCenter(from);
          return (
            <line
              x1={fromCenter.x}
              y1={fromCenter.y}
              x2={drag.mouseX}
              y2={drag.mouseY}
              stroke="var(--color-primary-light)"
              strokeWidth={2}
              strokeDasharray="4 4"
              pointerEvents="none"
            />
          );
        })()}

        {/* Boxes */}
        {boxes.map((el) => {
          const isSelected = selectedId === el.id;
          const isEditing = editingLabelId === el.id;
          return (
            <g
              key={el.id}
              transform={`translate(${el.x ?? 0}, ${el.y ?? 0})`}
              onMouseDown={(e) => handleBoxMouseDown(e, el)}
              onClick={(e) => { e.stopPropagation(); setSelectedId(el.id); }}
              style={{ cursor: readonly ? 'default' : 'move' }}
            >
              <rect
                width={el.width ?? BOX_W}
                height={el.height ?? BOX_H}
                rx={8}
                fill="var(--color-surface)"
                stroke={isSelected ? 'var(--color-primary)' : 'var(--color-border)'}
                strokeWidth={isSelected ? 2.5 : 1.5}
              />
              {isEditing && !readonly ? (
                <foreignObject x={4} y={4} width={(el.width ?? BOX_W) - 8} height={(el.height ?? BOX_H) - 8}>
                  <input
                    autoFocus
                    value={el.label ?? ''}
                    onChange={(e) => onUpdateElement(el.id, { label: e.target.value })}
                    onBlur={() => setEditingLabelId(null)}
                    onKeyDown={(e) => { if (e.key === 'Enter') setEditingLabelId(null); }}
                    style={{
                      width: '100%',
                      height: '100%',
                      border: 'none',
                      background: 'transparent',
                      color: 'var(--color-text)',
                      textAlign: 'center',
                      fontSize: 13,
                      fontWeight: 600,
                      outline: 'none',
                    }}
                  />
                </foreignObject>
              ) : (
                <text
                  x={(el.width ?? BOX_W) / 2}
                  y={(el.height ?? BOX_H) / 2}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="var(--color-text)"
                  fontSize={13}
                  fontWeight={600}
                  onDoubleClick={(e) => { if (!readonly) { e.stopPropagation(); setEditingLabelId(el.id); } }}
                  style={{ pointerEvents: 'none', userSelect: 'none' }}
                >
                  {el.label ?? 'Box'}
                </text>
              )}

              {/* Connection point */}
              {!readonly && (
                <circle
                  cx={(el.width ?? BOX_W) + 8}
                  cy={(el.height ?? BOX_H) / 2}
                  r={5}
                  fill="var(--color-primary-light)"
                  onMouseDown={(e) => handleConnectMouseDown(e, el)}
                  style={{ cursor: 'crosshair', opacity: isSelected ? 1 : 0.4 }}
                />
              )}

              {/* Resize handle */}
              {!readonly && isSelected && (
                <rect
                  x={(el.width ?? BOX_W) - 8}
                  y={(el.height ?? BOX_H) - 8}
                  width={12}
                  height={12}
                  rx={2}
                  fill="var(--color-primary)"
                  onMouseDown={(e) => handleResizeMouseDown(e, el)}
                  style={{ cursor: 'nwse-resize' }}
                />
              )}
            </g>
          );
        })}

        {/* Text elements */}
        {texts.map((el) => {
          const isEditing = editingTextId === el.id;
          if (isEditing && !readonly) {
            return (
              <foreignObject
                key={el.id}
                x={el.x ?? 0}
                y={el.y ?? 0}
                width={200}
                height={40}
              >
                <input
                  autoFocus
                  value={el.text ?? ''}
                  onChange={(e) => onUpdateElement(el.id, { text: e.target.value })}
                  onBlur={() => setEditingTextId(null)}
                  onKeyDown={(e) => { if (e.key === 'Enter') setEditingTextId(null); }}
                  style={{
                    width: '100%',
                    border: '1px solid var(--color-primary)',
                    background: 'var(--color-surface)',
                    color: 'var(--color-text)',
                    fontSize: 13,
                    padding: '4px 8px',
                    borderRadius: 4,
                    outline: 'none',
                  }}
                />
              </foreignObject>
            );
          }
          return (
            <text
              key={el.id}
              x={el.x ?? 0}
              y={el.y ?? 0}
              fill="var(--color-text-muted)"
              fontSize={13}
              onClick={(e) => { e.stopPropagation(); setSelectedId(el.id); }}
              onDoubleClick={(e) => { if (!readonly) { e.stopPropagation(); setEditingTextId(el.id); } }}
              style={{ userSelect: 'none', cursor: readonly ? 'default' : 'pointer' }}
            >
              {el.text ?? ''}
            </text>
          );
        })}
      </svg>

      {/* Toolbar */}
      {!readonly && (
        <div
          style={{
            position: 'absolute',
            top: 12,
            left: 12,
            display: 'flex',
            gap: 8,
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            padding: 6,
          }}
        >
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => {
              const svg = svgRef.current;
              if (!svg) return;
              const rect = svg.getBoundingClientRect();
              onAddElement({
                type: 'box',
                x: rect.width / 2 - BOX_W / 2,
                y: rect.height / 2 - BOX_H / 2,
                width: BOX_W,
                height: BOX_H,
                label: 'New Box',
              });
            }}
          >
            + Box
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => {
              const svg = svgRef.current;
              if (!svg) return;
              const rect = svg.getBoundingClientRect();
              onAddElement({
                type: 'text',
                x: rect.width / 2,
                y: rect.height / 2,
                text: 'New Text',
              });
            }}
          >
            + Text
          </button>
          {selectedId && (
            <button
              className="btn btn-danger btn-sm"
              onClick={() => {
                onRemoveElement(selectedId);
                setSelectedId(null);
              }}
            >
              Delete
            </button>
          )}
        </div>
      )}

      {/* Hint */}
      {state.elements.length === 0 && !readonly && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: 'var(--color-text-muted)',
            fontSize: 15,
            pointerEvents: 'none',
            textAlign: 'center',
          }}
        >
          Double-click anywhere to add a box
          <br />
          <span style={{ fontSize: 13 }}>Drag the blue dot on a box to connect</span>
        </div>
      )}
    </div>
  );
}
