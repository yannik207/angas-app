import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { Calendar, CalendarDay, dateKey } from './components/calendar/calendar';
import { ShiftForm } from './components/shift-form/shift-form';
import { ShiftService } from './services/shift.service';
import { Shift, ShiftBase } from './models/shift.model';

@Component({
  selector: 'app-root',
  imports: [Calendar, ShiftForm],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  private readonly shiftService = inject(ShiftService);

  readonly viewDate = signal(new Date());
  readonly selectedKey = signal<string | null>(dateKey(new Date()));
  readonly shifts = signal<Shift[]>([]);

  readonly loading = signal(false);
  readonly submitting = signal(false);
  readonly error = signal<string | null>(null);
  readonly toast = signal<string | null>(null);

  readonly selectedShifts = computed(() => {
    const key = this.selectedKey();
    if (!key) return [];
    return this.shifts()
      .filter((s) => s.start_time && dateKey(new Date(s.start_time)) === key)
      .sort((a, b) => a.start_time.localeCompare(b.start_time));
  });

  readonly selectedLabel = computed(() => {
    const key = this.selectedKey();
    if (!key) return 'No date selected';
    return new Date(`${key}T00:00:00`).toLocaleDateString(undefined, {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  });

  readonly totalShifts = computed(() => this.shifts().length);
  readonly openShifts = computed(
    () => this.shifts().filter((s) => s.shift_status === 'open').length,
  );

  constructor() {
    this.loadShifts();
  }

  loadShifts(): void {
    this.loading.set(true);
    this.error.set(null);
    this.shiftService.getShifts().subscribe({
      next: (shifts) => {
        this.shifts.set(shifts ?? []);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not reach the API. Is the backend running on port 8000?');
        this.loading.set(false);
      },
    });
  }

  onDayClick(day: CalendarDay): void {
    this.selectedKey.set(day.key);
  }

  onMonthChange(date: Date): void {
    this.viewDate.set(date);
  }

  onCreate(shift: ShiftBase): void {
    this.submitting.set(true);
    this.error.set(null);
    this.shiftService.createShift(shift).subscribe({
      next: () => {
        this.submitting.set(false);
        this.selectedKey.set(dateKey(new Date(shift.start_time)));
        this.showToast('Shift created');
        this.loadShifts();
      },
      error: () => {
        this.submitting.set(false);
        this.error.set('Failed to create the shift. Please try again.');
      },
    });
  }

  formatTime(iso: string): string {
    if (!iso) return '';
    return new Date(iso).toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  private showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 2600);
  }
}
