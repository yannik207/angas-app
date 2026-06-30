import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { EmployeeForm } from '../../components/employee-form/employee-form';
import { RoleForm } from '../../components/role-form/role-form';
import { EmployeeService } from '../../services/employee.service';
import { EmployeeBase, EmployeeType } from '../../models/employee.model';

@Component({
  selector: 'app-team-management',
  imports: [EmployeeForm, RoleForm],
  templateUrl: './team.html',
  styleUrl: './team.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TeamManagement {
  private readonly employeeService = inject(EmployeeService);

  readonly roles = signal<EmployeeType[]>([]);
  readonly roleNames = computed(() => this.roles().map((r) => r.name));

  readonly creatingEmployee = signal(false);
  readonly creatingRole = signal(false);
  readonly error = signal<string | null>(null);
  readonly toast = signal<string | null>(null);

  constructor() {
    this.loadRoles();
  }

  loadRoles(): void {
    this.error.set(null);
    this.employeeService.getEmployeeTypes().subscribe({
      next: (roles) => this.roles.set(roles ?? []),
      error: () => this.error.set('Could not load roles. Is the backend running?'),
    });
  }

  onCreateRole(name: string): void {
    this.creatingRole.set(true);
    this.error.set(null);
    this.employeeService.createEmployeeType({ name }).subscribe({
      next: () => {
        this.creatingRole.set(false);
        this.showToast(`Role "${name}" added`);
        this.loadRoles();
      },
      error: (err) => {
        this.creatingRole.set(false);
        this.error.set(err?.error?.detail ?? 'Failed to create the role. Please try again.');
      },
    });
  }

  onCreateEmployee(employee: EmployeeBase): void {
    this.creatingEmployee.set(true);
    this.error.set(null);
    this.employeeService.createEmployee(employee).subscribe({
      next: () => {
        this.creatingEmployee.set(false);
        this.showToast(`${employee.name} added`);
      },
      error: (err) => {
        this.creatingEmployee.set(false);
        this.error.set(err?.error?.detail ?? 'Failed to create the employee. Please try again.');
      },
    });
  }

  private showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 2600);
  }
}
