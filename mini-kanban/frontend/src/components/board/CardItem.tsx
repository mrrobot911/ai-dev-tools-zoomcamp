import type { Card, Role } from '@/types';
import { Avatar } from '@/components/ui';
import { Trash2, Pencil } from 'lucide-react';

interface CardItemProps {
  card: Card;
  canEdit: boolean;
  canDelete: boolean;
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
  onClick: (card: Card) => void;
  isDragging?: boolean;
}

export function CardItem({
  card,
  canEdit,
  canDelete,
  onEdit,
  onDelete,
  onClick,
  isDragging,
}: CardItemProps) {
  return (
    <div
      onClick={() => onClick(card)}
      className={`group relative bg-white rounded-lg border border-slate-200 p-3 cursor-pointer hover:border-slate-300 hover:shadow-sm transition-all duration-150 ${
        isDragging ? 'opacity-40' : ''
      }`}
    >
      <p className="text-sm font-medium text-slate-800 line-clamp-2 pr-4">
        {card.title}
      </p>
      {card.description && (
        <p className="text-xs text-slate-500 mt-1 line-clamp-2">{card.description}</p>
      )}
      <div className="mt-2 flex items-center justify-between">
        {card.assigneeName ? (
          <div className="flex items-center gap-1.5">
            <Avatar name={card.assigneeName} size="sm" />
            <span className="text-xs text-slate-600">{card.assigneeName}</span>
          </div>
        ) : (
          <span className="text-xs text-slate-400">Unassigned</span>
        )}
        <span className="text-xs text-slate-400 hidden group-hover:inline">
          {card.creatorName}
        </span>
      </div>
      {canEdit && (
        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(card);
            }}
            className="p-1 rounded text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <Pencil size={12} />
          </button>
          {canDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(card);
              }}
              className="p-1 rounded text-slate-400 hover:bg-red-50 hover:text-red-600"
            >
              <Trash2 size={12} />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
