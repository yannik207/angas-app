import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Shift, ShiftBase, ShiftDetails, ShiftRequest, ShiftUpdate } from '../models/shift.model';
import { EmployeeAvailability } from '../models/employee.model';

@Injectable({ providedIn: 'root' })
export class ShiftService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/shifts`;

  getShifts(): Observable<Shift[]> {
    return this.http.get<Shift[]>(this.baseUrl);
  }

  getShiftDetails(id: string): Observable<ShiftDetails> {
    return this.http.get<ShiftDetails>(`${this.baseUrl}/${id}`);
  }

  createShift(shift: ShiftBase): Observable<{ status: string; message: string }> {
    const body: ShiftRequest = { shifts: [shift] };
    return this.http.post<{ status: string; message: string }>(this.baseUrl, body);
  }

  updateShift(
    id: string,
    changes: ShiftUpdate,
  ): Observable<{ status: string; message: string }> {
    return this.http.patch<{ status: string; message: string }>(`${this.baseUrl}/${id}`, changes);
  }

  deleteShift(id: string): Observable<{ status: string; message: string }> {
    return this.http.delete<{ status: string; message: string }>(`${this.baseUrl}/${id}`);
  }

  getEmployeeAvailability(shiftId: string): Observable<EmployeeAvailability[]> {
    return this.http.get<EmployeeAvailability[]>(
      `${this.baseUrl}/${shiftId}/employees/availability`,
    );
  }

  assignEmployee(
    shiftId: string,
    employeeId: string,
  ): Observable<{ status: string; message: string }> {
    return this.http.post<{ status: string; message: string }>(
      `${this.baseUrl}/${shiftId}/employees/${employeeId}`,
      {},
    );
  }
}
