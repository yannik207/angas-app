/** An employee role/type as stored in the database (matches backend EmployeeType). */
export interface EmployeeType {
  id: string;
  name: string;
}

/** Payload sent to POST /employee/type (matches backend EmployeeTypeRequest). */
export interface EmployeeTypeRequest {
  name: string;
}

/** Payload sent to POST /employee (matches backend EmployeeRequest). */
export interface EmployeeBase {
  name: string;
  email: string;
  hashed_password: string;
  role: string;
}

/** A persisted employee returned by the API. */
export interface Employee extends EmployeeBase {
  id: string;
  created_ts?: string;
  updated_ts?: string;
}

/** Minimal employee shape returned by GET /employees (matches backend EmployeePublic). */
export interface EmployeePublic {
  id: string;
  name: string;
}

/**
 * An employee plus whether they can be assigned to a given shift
 * (matches backend EmployeeAvailability). `available` is false when the
 * employee is already assigned to that shift.
 */
export interface EmployeeAvailability extends EmployeePublic {
  available: boolean;
}
