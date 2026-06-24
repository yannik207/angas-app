import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Shift, ShiftBase, ShiftRequest } from '../models/shift.model';

@Injectable({ providedIn: 'root' })
export class ShiftService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/shifts`;

  getShifts(): Observable<Shift[]> {
    return this.http.get<Shift[]>(this.baseUrl);
  }

  createShift(shift: ShiftBase): Observable<{ status: string; message: string }> {
    const body: ShiftRequest = { shifts: [shift] };
    return this.http.post<{ status: string; message: string }>(this.baseUrl, body);
  }
}
