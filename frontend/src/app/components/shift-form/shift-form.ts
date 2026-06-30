import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  input,
  output,
} from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import {
  Shift,
  ShiftBase,
  SHIFT_STATUSES,
  SHIFT_TYPES,
  ShiftStatus,
  ShiftType,
} from '../../models/shift.model';

/** yyyy-mm-dd in local time. */
function toDateInput(iso: string): string {
  const d = new Date(iso);
  const y = d.getFullYear();
  const m = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** HH:mm in local time. */
function toTimeInput(iso: string): string {
  const d = new Date(iso);
  return `${`${d.getHours()}`.padStart(2, '0')}:${`${d.getMinutes()}`.padStart(2, '0')}`;
}

@Component({
  selector: 'app-shift-form',
  imports: [ReactiveFormsModule],
  templateUrl: './shift-form.html',
  styleUrl: './shift-form.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ShiftForm {
  /** Pre-selected date (yyyy-mm-dd) coming from the calendar. */
  readonly selectedDate = input<string | null>(null);
  /** When set the form switches to edit mode for this shift. */
  readonly editing = input<Shift | null>(null);
  readonly submitting = input<boolean>(false);

  readonly create = output<ShiftBase>();
  readonly update = output<{ id: string; changes: ShiftBase }>();
  readonly cancel = output<void>();

  private readonly fb = inject(FormBuilder);

  readonly shiftTypes = SHIFT_TYPES;
  readonly shiftStatuses = SHIFT_STATUSES;

  readonly isEditing = computed(() => this.editing() !== null);

  readonly form = this.fb.nonNullable.group({
    date: ['', Validators.required],
    startTime: ['09:00', Validators.required],
    endTime: ['17:00', Validators.required],
    shiftType: ['morning' as ShiftType, Validators.required],
    shiftStatus: ['open' as ShiftStatus, Validators.required],
    necessaryEmployees: [1, [Validators.required, Validators.min(1)]],
    notes: [''],
  });

  constructor() {
    effect(() => {
      const shift = this.editing();
      if (shift) {
        this.form.setValue({
          date: toDateInput(shift.start_time),
          startTime: toTimeInput(shift.start_time),
          endTime: toTimeInput(shift.end_time),
          shiftType: shift.shift_type,
          shiftStatus: shift.shift_status,
          necessaryEmployees: shift.necessary_employees,
          notes: shift.shift_notes ?? '',
        });
        return;
      }

      const date = this.selectedDate();
      if (date) {
        this.form.controls.date.setValue(date);
      }
    });
  }

  submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }

    const v = this.form.getRawValue();
    const start = new Date(`${v.date}T${v.startTime}`);
    let end = new Date(`${v.date}T${v.endTime}`);
    // Overnight shift: end time earlier than start -> next day.
    if (end <= start) {
      end = new Date(end.getTime() + 24 * 60 * 60 * 1000);
    }

    const shift: ShiftBase = {
      start_time: start.toISOString(),
      end_time: end.toISOString(),
      shift_type: v.shiftType,
      shift_status: v.shiftStatus,
      shift_notes: v.notes ?? '',
      necessary_employees: Number(v.necessaryEmployees),
    };

    const editing = this.editing();
    if (editing) {
      this.update.emit({ id: editing.id, changes: shift });
    } else {
      this.create.emit(shift);
    }
  }

  cancelEdit(): void {
    this.cancel.emit();
  }
}
