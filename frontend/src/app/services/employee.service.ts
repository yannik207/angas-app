import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  Employee,
  EmployeeBase,
  EmployeePublic,
  EmployeeType,
  EmployeeTypeRequest,
} from '../models/employee.model';

@Injectable({ providedIn: 'root' })
export class EmployeeService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/employee`;

  createEmployee(employee: EmployeeBase): Observable<{ status: string; message: string }> {
    return this.http.post<{ status: string; message: string }>(this.baseUrl, employee);
  }

  getEmployee(id: string): Observable<Employee> {
    return this.http.get<Employee>(`${this.baseUrl}/${id}`);
  }

  getEmployees(): Observable<EmployeePublic[]> {
    return this.http.get<EmployeePublic[]>(`${environment.apiBaseUrl}/employees`);
  }

  getEmployeeTypes(): Observable<EmployeeType[]> {
    return this.http.get<EmployeeType[]>(`${this.baseUrl}/types`);
  }

  createEmployeeType(
    request: EmployeeTypeRequest,
  ): Observable<{ status: string; message: string }> {
    return this.http.post<{ status: string; message: string }>(
      `${this.baseUrl}/type`,
      request,
    );
  }
}
