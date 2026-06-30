export type ShiftType = 'morning' | 'afternoon' | 'evening' | 'night';
export type ShiftStatus = 'open' | 'filled' | 'cancelled';

/** Staffing level for a shift, used to colour-code it on the calendar. */
export type StaffingStatus = 'full' | 'partial' | 'empty';

/** Payload sent to POST /shifts (matches backend ShiftBase). */
export interface ShiftBase {
  start_time: string;
  end_time: string;
  shift_type: ShiftType;
  shift_status: ShiftStatus;
  shift_notes: string;
  necessary_employees: number;
}

/** An employee assigned to a shift (matches backend EmployeePublic). */
export interface ShiftEmployee {
  id: string;
  name: string;
}

/** A persisted shift returned by GET /shifts (matches backend ShiftSummary). */
export interface Shift extends ShiftBase {
  id: string;
  created_ts?: string;
  updated_ts?: string;
  /** Number of employees currently assigned to this shift. */
  assigned_employees: number;
  /** necessary_employees - assigned_employees (clamped at 0). */
  missing_employees: number;
  /** Derived staffing level: 'full' | 'partial' | 'empty'. */
  staffing_status: StaffingStatus;
}

/** Detailed shift returned by GET /shifts/{id} (matches backend ShiftEmployeeDetails). */
export interface ShiftDetails extends ShiftBase {
  id: string;
  created_ts?: string;
  updated_ts?: string;
  /** Employees currently assigned to this shift. */
  employees: ShiftEmployee[];
  /** Number of employees assigned (employees.length). */
  assigned_employees: number;
  /** necessary_employees - assigned_employees. */
  missing_employees: number;
}

export interface ShiftRequest {
  shifts: ShiftBase[];
}

/** Partial payload sent to PATCH /shifts/{id} (matches backend ShiftUpdateAttributes). */
export type ShiftUpdate = Partial<ShiftBase>;

export const SHIFT_TYPES: ShiftType[] = ['morning', 'afternoon', 'evening', 'night'];
export const SHIFT_STATUSES: ShiftStatus[] = ['open', 'filled', 'cancelled'];
