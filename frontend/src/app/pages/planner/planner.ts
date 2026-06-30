import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { TitleCasePipe } from '@angular/common';
import { Calendar, CalendarDay, dateKey } from '../../components/calendar/calendar';
import { ShiftForm } from '../../components/shift-form/shift-form';
import { ShiftAction } from '../../components/shift-menu/shift-menu';
import { ShiftService } from '../../services/shift.service';
import { Shift, ShiftBase, ShiftDetails } from '../../models/shift.model';
import { EmployeeAvailability } from '../../models/employee.model';

@Component({
  selector: 'app-planner',
  imports: [Calendar, ShiftForm, TitleCasePipe],
  templateUrl: './planner.html',
  styleUrl: './planner.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Planner {
  private readonly shiftService = inject(ShiftService);

  readonly viewDate = signal(new Date());
  readonly selectedKey = signal<string | null>(dateKey(new Date()));
  readonly shifts = signal<Shift[]>([]);
  readonly editingShift = signal<Shift | null>(null);

  readonly detailsTarget = signal<Shift | null>(null);
  readonly detailsShift = signal<ShiftDetails | null>(null);
  readonly detailsLoading = signal(false);
  readonly detailsError = signal<string | null>(null);

  readonly assignTarget = signal<Shift | null>(null);
  readonly employees = signal<EmployeeAvailability[]>([]);
  readonly employeesLoading = signal(false);
  readonly selectedEmployeeId = signal<string>('');
  readonly assigning = signal(false);
  readonly assignError = signal<string | null>(null);

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
      case 'details':
        this.showDetails(event.shift);
        break;
      case 'delete':
        this.deleteShift(event.shift);
        break;
      case 'edit':
        this.editingShift.set(event.shift);
        this.selectedKey.set(dateKey(new Date(event.shift.start_time)));
        break;
      case 'assign':
        this.assignStaff(event.shift);
        break;
    }
  }

  private assignStaff(shift: Shift): void {
    this.assignTarget.set(shift);
    this.selectedEmployeeId.set('');
    this.assignError.set(null);
    this.employeesLoading.set(true);
    this.shiftService.getEmployeeAvailability(shift.id).subscribe({
      next: (employees) => {
        this.employees.set(employees ?? []);
        this.employeesLoading.set(false);
      },
      error: () => {
        this.assignError.set('Could not load employees. Please try again.');
        this.employeesLoading.set(false);
      },
    });
  }

  confirmAssign(): void {
    const shift = this.assignTarget();
    const employeeId = this.selectedEmployeeId();
    if (!shift || !employeeId) return;

    this.assigning.set(true);
    this.assignError.set(null);
    this.shiftService.assignEmployee(shift.id, employeeId).subscribe({
      next: () => {
        this.assigning.set(false);
        this.showToast('Staff assigned');
        if (this.detailsTarget()?.id === shift.id) this.showDetails(shift);
        this.closeAssign();
        this.loadShifts();
      },
      error: () => {
        this.assigning.set(false);
        this.assignError.set('Failed to assign staff. Please try again.');
      },
    });
  }

  closeAssign(): void {
    this.assignTarget.set(null);
    this.employees.set([]);
    this.selectedEmployeeId.set('');
    this.assignError.set(null);
    this.employeesLoading.set(false);
    this.assigning.set(false);
  }

  private showDetails(shift: Shift): void {
    this.detailsTarget.set(shift);
    this.detailsShift.set(null);
    this.detailsError.set(null);
    this.detailsLoading.set(true);
    this.shiftService.getShiftDetails(shift.id).subscribe({
      next: (details) => {
        this.detailsShift.set(details);
        this.detailsLoading.set(false);
      },
      error: () => {
        this.detailsError.set('Could not load shift details. Please try again.');
        this.detailsLoading.set(false);
      },
    });
  }

  closeDetails(): void {
    this.detailsTarget.set(null);
    this.detailsShift.set(null);
    this.detailsError.set(null);
    this.detailsLoading.set(false);
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
        if (this.editingShift()?.id === shift.id) this.editingShift.set(null);
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

  onUpdate(event: { id: string; changes: ShiftBase }): void {
    this.submitting.set(true);
    this.error.set(null);
    this.shiftService.updateShift(event.id, event.changes).subscribe({
      next: () => {
        this.submitting.set(false);
        this.editingShift.set(null);
        this.selectedKey.set(dateKey(new Date(event.changes.start_time)));
        this.showToast('Shift updated');
        this.loadShifts();
      },
      error: () => {
        this.submitting.set(false);
        this.error.set('Failed to update the shift. Please try again.');
      },
    });
  }

  cancelEdit(): void {
    this.editingShift.set(null);
  }

  formatDateTime(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString(undefined, {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  private showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 2600);
  }
}
