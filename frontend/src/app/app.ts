import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { Calendar, CalendarDay, dateKey } from './components/calendar/calendar';
import { ShiftForm } from './components/shift-form/shift-form';
import { ShiftAction } from './components/shift-menu/shift-menu';
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

  onShiftAction(event: { action: ShiftAction; shift: Shift }): void {
    switch (event.action) {
      case 'delete':
        this.deleteShift(event.shift);
        break;
      case 'edit':
        // Editing is not wired to a backend endpoint yet.
        this.showToast('Editing shifts is coming soon');
        break;
    }
  }

  private deleteShift(shift: Shift): void {
    const when = new Date(shift.start_time).toLocaleString(undefined, {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
    if (!confirm(`Delete the ${shift.shift_type} shift on ${when}?`)) return;

    this.error.set(null);
    this.shiftService.deleteShift(shift.id).subscribe({
      next: () => {
        this.showToast('Shift deleted');
        this.loadShifts();
      },
      error: () => this.error.set('Failed to delete the shift. Please try again.'),
    });
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

  private showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 2600);
  }
}
