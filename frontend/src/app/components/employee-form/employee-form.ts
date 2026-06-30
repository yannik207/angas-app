import {
  ChangeDetectionStrategy,
  Component,
  inject,
  input,
  output,
} from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { EmployeeBase } from '../../models/employee.model';

@Component({
  selector: 'app-employee-form',
  imports: [ReactiveFormsModule],
  templateUrl: './employee-form.html',
  styleUrl: './employee-form.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EmployeeForm {
  /** Available roles, loaded from the database by the parent page. */
  readonly roles = input<string[]>([]);
  readonly submitting = input<boolean>(false);

  readonly create = output<EmployeeBase>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    role: ['', Validators.required],
  });

  submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }

    const v = this.form.getRawValue();
    const employee: EmployeeBase = {
      name: v.name.trim(),
      email: v.email.trim(),
      hashed_password: v.password,
      role: v.role,
    };

    this.create.emit(employee);
    this.form.reset();
  }
}
