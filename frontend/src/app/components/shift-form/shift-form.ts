import {
  ChangeDetectionStrategy,
  Component,
  effect,
  inject,
  input,
  output,
} from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import {
  ShiftBase,
  SHIFT_STATUSES,
  SHIFT_TYPES,
  ShiftStatus,
  ShiftType,
} from '../../models/shift.model';

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
  readonly submitting = input<boolean>(false);

  readonly create = output<ShiftBase>();

  private readonly fb = inject(FormBuilder);

  readonly shiftTypes = SHIFT_TYPES;
  readonly shiftStatuses = SHIFT_STATUSES;

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

    this.create.emit(shift);
  }
}
