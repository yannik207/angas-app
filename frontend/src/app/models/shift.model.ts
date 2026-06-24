export type ShiftType = 'morning' | 'afternoon' | 'evening' | 'night';
export type ShiftStatus = 'open' | 'filled' | 'cancelled';

/** Payload sent to POST /shifts (matches backend ShiftBase). */
export interface ShiftBase {
  start_time: string;
  end_time: string;
  shift_type: ShiftType;
  shift_status: ShiftStatus;
  shift_notes: string;
  necessary_employees: number;
}

/** A persisted shift returned by GET /shifts. */
export interface Shift extends ShiftBase {
  id: string;
  created_ts?: string;
  updated_ts?: string;
}

export interface ShiftRequest {
  shifts: ShiftBase[];
}

export const SHIFT_TYPES: ShiftType[] = ['morning', 'afternoon', 'evening', 'night'];
export const SHIFT_STATUSES: ShiftStatus[] = ['open', 'filled', 'cancelled'];
