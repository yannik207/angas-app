import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
import { Shift } from '../../models/shift.model';
import { ShiftAction, ShiftMenu } from '../shift-menu/shift-menu';

export type CalendarView = 'month' | 'week';

export interface CalendarDay {
  date: Date;
  key: string;
  dayNumber: number;
  inCurrentMonth: boolean;
  isToday: boolean;
  shifts: Shift[];
}

export interface PositionedShift {
  shift: Shift;
  top: number;
  height: number;
  left: number;
  width: number;
  timeLabel: string;
}

export interface WeekColumn {
  day: CalendarDay;
  blocks: PositionedShift[];
}

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const MONTHS_SHORT = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

/** Pixel height of a single hour row in the week time-grid. */
const HOUR_HEIGHT = 44;
/** Minimum rendered height for a shift block so short shifts stay readable. */
const MIN_BLOCK_HEIGHT = 24;

export function dateKey(d: Date): string {
  const y = d.getFullYear();
  const m = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function minutesOfDay(d: Date): number {
  return d.getHours() * 60 + d.getMinutes();
}

function formatMinutes(min: number): string {
  const clamped = Math.max(0, Math.min(min, 1440));
  const h = Math.floor(clamped / 60) % 24;
  const m = clamped % 60;
  return `${`${h}`.padStart(2, '0')}:${`${m}`.padStart(2, '0')}`;
}

@Component({
  selector: 'app-calendar',
  templateUrl: './calendar.html',
  styleUrl: './calendar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ShiftMenu],
})
export class Calendar {
  readonly shifts = input<Shift[]>([]);
  readonly selectedKey = input<string | null>(null);
  readonly viewDate = input.required<Date>();

  readonly dayClick = output<CalendarDay>();
  readonly monthChange = output<Date>();
  readonly shiftAction = output<{ action: ShiftAction; shift: Shift }>();

  readonly weekdays = WEEKDAYS;
  readonly hours = Array.from({ length: 24 }, (_, h) => h);
  readonly hourHeight = HOUR_HEIGHT;

  readonly view = signal<CalendarView>('month');

  readonly headerLabel = computed(() => {
    if (this.view() === 'week') return this.weekRangeLabel();
    const d = this.viewDate();
    return `${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
  });

  private readonly weekRangeLabel = computed(() => {
    const days = this.weekDays();
    const start = days[0].date;
    const end = days[6].date;
    const startLabel = `${MONTHS_SHORT[start.getMonth()]} ${start.getDate()}`;
    const endLabel =
      start.getMonth() === end.getMonth()
        ? `${end.getDate()}`
        : `${MONTHS_SHORT[end.getMonth()]} ${end.getDate()}`;
    return `${startLabel} – ${endLabel}, ${end.getFullYear()}`;
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
          shifts: this.sortByStart(byDay.get(key) ?? []),
        });
      }
      weeks.push(row);
    }
    return weeks;
  });

  readonly weekDays = computed<CalendarDay[]>(() => {
    const view = this.viewDate();
    const base = new Date(view.getFullYear(), view.getMonth(), view.getDate());
    const offset = (base.getDay() + 6) % 7;
    const start = new Date(base);
    start.setDate(base.getDate() - offset);

    const byDay = this.shiftsByDay();
    const todayKey = dateKey(new Date());
    const days: CalendarDay[] = [];

    for (let d = 0; d < 7; d++) {
      const current = new Date(start);
      current.setDate(start.getDate() + d);
      const key = dateKey(current);
      days.push({
        date: current,
        key,
        dayNumber: current.getDate(),
        inCurrentMonth: current.getMonth() === view.getMonth(),
        isToday: key === todayKey,
        shifts: this.sortByStart(byDay.get(key) ?? []),
      });
    }
    return days;
  });

  readonly weekColumns = computed<WeekColumn[]>(() =>
    this.weekDays().map((day) => ({ day, blocks: this.layoutBlocks(day.shifts) })),
  );

  setView(view: CalendarView): void {
    this.view.set(view);
  }

  prev(): void {
    if (this.view() === 'week') {
      this.shiftDays(-7);
    } else {
      const d = this.viewDate();
      this.monthChange.emit(new Date(d.getFullYear(), d.getMonth() - 1, 1));
    }
  }

  next(): void {
    if (this.view() === 'week') {
      this.shiftDays(7);
    } else {
      const d = this.viewDate();
      this.monthChange.emit(new Date(d.getFullYear(), d.getMonth() + 1, 1));
    }
  }

  today(): void {
    const now = new Date();
    this.monthChange.emit(new Date(now.getFullYear(), now.getMonth(), now.getDate()));
  }

  selectDay(day: CalendarDay): void {
    this.dayClick.emit(day);
  }

  openDayInWeek(day: CalendarDay): void {
    this.dayClick.emit(day);
    this.monthChange.emit(new Date(day.date.getFullYear(), day.date.getMonth(), day.date.getDate()));
    this.view.set('week');
  }

  hourLabel(h: number): string {
    return `${`${h}`.padStart(2, '0')}:00`;
  }

  chipTime(iso: string): string {
    if (!iso) return '';
    return formatMinutes(minutesOfDay(new Date(iso)));
  }

  private shiftDays(delta: number): void {
    const d = this.viewDate();
    this.monthChange.emit(new Date(d.getFullYear(), d.getMonth(), d.getDate() + delta));
  }

  private sortByStart(shifts: Shift[]): Shift[] {
    return [...shifts].sort((a, b) => (a.start_time ?? '').localeCompare(b.start_time ?? ''));
  }

  /** Place shifts in the week time-grid, splitting overlapping ones into side-by-side lanes. */
  private layoutBlocks(shifts: Shift[]): PositionedShift[] {
    const items = shifts
      .filter((s) => s.start_time)
      .map((s) => {
        const start = new Date(s.start_time);
        const end = s.end_time ? new Date(s.end_time) : start;
        const startMin = minutesOfDay(start);
        let endMin = minutesOfDay(end);
        // Overnight or missing end -> clamp to the end of the starting day.
        if (endMin <= startMin) endMin = 1440;
        return { shift: s, startMin, endMin };
      })
      .sort((a, b) => a.startMin - b.startMin || a.endMin - b.endMin);

    const laneEnds: number[] = [];
    const laneOf: number[] = [];
    for (const it of items) {
      let lane = laneEnds.findIndex((end) => end <= it.startMin);
      if (lane === -1) {
        lane = laneEnds.length;
        laneEnds.push(it.endMin);
      } else {
        laneEnds[lane] = it.endMin;
      }
      laneOf.push(lane);
    }

    const lanes = Math.max(laneEnds.length, 1);
    const laneWidth = 100 / lanes;

    return items.map((it, i) => ({
      shift: it.shift,
      top: (it.startMin / 60) * HOUR_HEIGHT,
      height: Math.max(((it.endMin - it.startMin) / 60) * HOUR_HEIGHT, MIN_BLOCK_HEIGHT),
      left: laneOf[i] * laneWidth,
      width: laneWidth,
      timeLabel: `${formatMinutes(it.startMin)} – ${formatMinutes(it.endMin)}`,
    }));
  }
}
