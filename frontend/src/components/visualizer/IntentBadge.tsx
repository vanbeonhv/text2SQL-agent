import { Tag } from 'lucide-react';
import { cn } from '../../lib/utils';

interface IntentBadgeProps {
  intent: string;
}

const intentBadgeClass =
  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border bg-primary/20 text-primary border-primary/30';

const INTENT_LABELS_VI: Record<string, string> = {
  data_retrieval: 'Truy vấn dữ liệu',
  aggregation: 'Tổng hợp',
  filtering: 'Lọc',
  sorting: 'Sắp xếp',
  joining: 'Kết bảng',
  greeting: 'Chào hỏi',
  goodbye: 'Tạm biệt',
  schema_request: 'Yêu cầu schema',
  unknown: 'Không xác định',
};

function formatIntentLabel(intent: string): string {
  return INTENT_LABELS_VI[intent] ?? intent.replaceAll('_', ' ');
}

export const IntentBadge = ({ intent }: IntentBadgeProps) => {
  return (
    <div className="surface elevated rounded-lg p-4 border border-default">
      <div className="flex items-center gap-2 mb-2">
        <Tag className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-medium">Ý định nhận diện</h3>
      </div>
      <div className={cn(intentBadgeClass)}>
        {formatIntentLabel(intent)}
      </div>
    </div>
  );
};
