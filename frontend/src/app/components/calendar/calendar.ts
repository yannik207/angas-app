import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';
import { Shift } from '../../models/shift.model';

export interface CalendarDay {
  date: Date;
  key: string;
  dayNumber: number;
  inCurrentMonth: boolean;
  isToday: boolean;
  shifts: Shift[];
}

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

export function dateKey(d: Date): string {
  const y = d.getFullYear();
  const m = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${y}-${m}-${day}`;
}

@Component({
  selector: 'app-calendar',
  templateUrl: './calendar.html',
  styleUrl: './calendar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Calendar {
  readonly shifts = input<Shift[]>([]);
  readonly selectedKey = input<string | null>(null);
  readonly viewDate = input.required<Date>();

  readonly dayClick = output<CalendarDay>();
  readonly monthChange = output<Date>();

  readonly weekdays = WEEKDAYS;

  readonly monthLabel = computed(() => {
    const d = this.viewDate();
    return `${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
  });

  private readonly shiftsByDay = computed(() => {
    const map = new Map<string, Shift[]>();
    for (const shift of this.shifts()) {
      if (!shift.start_time) continue;
      const key = dateKey(new Date(shift.start_time));
      const bucket = map.get(key);
      if (bucket) {
        bucket.push(shift);
      } else {
        map.set(key, [shift]);
      }
    }
    return map;
  });

  readonly weeks = computed<CalendarDay[][]>(() => {
    const view = this.viewDate();
    const year = view.getFullYear();
    const month = view.getMonth();
    const byDay = this.shiftsByDay();

    const firstOfMonth = new Date(year, month, 1);
    // JS: 0=Sun..6=Sat -> shift so Monday is the first column.
    const offset = (firstOfMonth.getDay() + 6) % 7;
    const start = new Date(year, month, 1 - offset);

    const todayKey = dateKey(new Date());
    const weeks: CalendarDay[][] = [];

    for (let w = 0; w < 6; w++) {
      const row: CalendarDay[] = [];
      for (let d = 0; d < 7; d++) {
        const current = new Date(start);
        current.setDate(start.getDate() + w * 7 + d);
        const key = dateKey(current);
        row.push({
          date: current,
          key,
          dayNumber: current.getDate(),
          inCurrentMonth: current.getMonth() === month,
          isToday: key === todayKey,
          shifts: byDay.get(key) ?? [],
        });
      }
      weeks.push(row);
    }
    return weeks;
  });

  prevMonth(): void {
    const d = this.viewDate();
    this.monthChange.emit(new Date(d.getFullYear(), d.getMonth() - 1, 1));
  }

  nextMonth(): void {
    const d = this.viewDate();
    this.monthChange.emit(new Date(d.getFullYear(), d.getMonth() + 1, 1));
  }

  today(): void {
    const now = new Date();
    this.monthChange.emit(new Date(now.getFullYear(), now.getMonth(), 1));
  }

  selectDay(day: CalendarDay): void {
    this.dayClick.emit(day);
  }
}
