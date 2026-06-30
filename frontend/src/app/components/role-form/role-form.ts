import { ChangeDetectionStrategy, Component, inject, input, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-role-form',
  imports: [ReactiveFormsModule],
  templateUrl: './role-form.html',
  styleUrl: './role-form.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RoleForm {
  readonly submitting = input<boolean>(false);

  readonly create = output<string>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
  });

  submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }

    this.create.emit(this.form.getRawValue().name.trim());
    this.form.reset();
  }
}
