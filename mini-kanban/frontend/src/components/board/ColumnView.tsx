import type { Column, Card, Role, Participant } from '@/types';
import { CardItem } from '@/components/board/CardItem';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Plus, Trash2, Pencil, GripVertical } from 'lucide-react';

interface ColumnViewProps {
  column: Column;
  cards: Card[];
  participants: Participant[];
  role: Role;
  currentUserId: string;
  onAddCard: (columnId: string) => void;
  onEditCard: (card: Card) => void;
  onDeleteCard: (card: Card) => void;
  onEditColumn: (column: Column) => void;
  onDeleteColumn: (column: Column) => void;
}

function SortableColumnWrapper({ column, children }: { column: Column; children: React.ReactNode }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `col_${column.id}`,
    data: { type: 'column', columnId: column.id },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex flex-col w-72 min-w-[18rem] bg-slate-100/70 rounded-xl border border-slate-200 ${isDragging ? 'opacity-50' : ''}`}
    >
      <div className="flex items-center" {...attributes} {...listeners}>
        {children}
      </div>
    </div>
  );
}

export function ColumnView({
  column,
  cards,
  participants,
  role,
  currentUserId,
  onAddCard,
  onEditCard,
  onDeleteCard,
  onEditColumn,
  onDeleteColumn,
}: ColumnViewProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: `drop_${column.id}`,
    data: { type: 'column', columnId: column.id },
  });

  const canManageColumns = role === 'owner';
  const canEditCards = true; // all participants can edit
  const canDeleteCard = (card: Card) => role === 'owner' || card.creatorId === currentUserId;

  return (
    <SortableColumnWrapper column={column}>
      <div className="flex-1 flex flex-col">
        {/* Column header */}
        <div className="flex items-center justify-between px-3 py-3 cursor-grab active:cursor-grabbing">
          <div className="flex items-center gap-2 flex-1">
            <GripVertical size={14} className="text-slate-400" />
            <h3 className="text-sm font-semibold text-slate-700">{column.name}</h3>
            <span className="text-xs text-slate-400 bg-slate-200 px-1.5 py-0.5 rounded-full">
              {cards.length}
            </span>
          </div>
          {canManageColumns && (
            <div className="flex gap-1">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEditColumn(column);
                }}
                className="p-1 rounded text-slate-400 hover:bg-slate-200 hover:text-slate-600"
              >
                <Pencil size={12} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteColumn(column);
                }}
                className="p-1 rounded text-slate-400 hover:bg-red-100 hover:text-red-600"
              >
                <Trash2 size={12} />
              </button>
            </div>
          )}
        </div>

        {/* Droppable area */}
        <div
          ref={setNodeRef}
          className={`flex-1 px-2 pb-2 space-y-2 min-h-[60px] rounded-lg transition-colors ${
            isOver ? 'bg-slate-200/80' : ''
          }`}
        >
          <SortableContext
            items={cards.map((c) => `card_${c.id}`)}
            strategy={verticalListSortingStrategy}
          >
            {cards.map((card) => (
              <SortableCardItem
                key={card.id}
                card={card}
                canEdit={canEditCards}
                canDelete={canDeleteCard(card)}
                onEdit={onEditCard}
                onDelete={onDeleteCard}
                onClick={onEditCard}
              />
            ))}
          </SortableContext>

          {cards.length === 0 && (
            <div className="text-center py-4 text-xs text-slate-400">
              No cards
            </div>
          )}
        </div>

        {/* Add card */}
        <button
          onClick={() => onAddCard(column.id)}
          className="mx-2 mb-2 flex items-center gap-1.5 px-2 py-1.5 text-sm text-slate-500 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-colors"
        >
          <Plus size={14} />
          Add card
        </button>
      </div>
    </SortableColumnWrapper>
  );
}

import { useSortable as useCardSortable } from '@dnd-kit/sortable';

function SortableCardItem({
  card,
  canEdit,
  canDelete,
  onEdit,
  onDelete,
  onClick,
}: {
  card: Card;
  canEdit: boolean;
  canDelete: boolean;
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
  onClick: (card: Card) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useCardSortable({
    id: `card_${card.id}`,
    data: { type: 'card', cardId: card.id, columnId: card.columnId },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <CardItem
        card={card}
        canEdit={canEdit}
        canDelete={canDelete}
        onEdit={onEdit}
        onDelete={onDelete}
        onClick={onClick}
        isDragging={isDragging}
      />
    </div>
  );
}
