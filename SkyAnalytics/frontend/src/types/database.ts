export type UserRole = 'ADMIN' | 'ANALYST' | 'VIEWER'

export type FlightStatus = 'SCHEDULED' | 'ON_TIME' | 'DELAYED' | 'CANCELLED'

export interface User {
  id: number
  email: string
  full_name: string | null
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Flight {
  id: number
  flight_number: string
  origin: string
  destination: string
  departure_time: string
  arrival_time: string
  capacity: number
  booked_seats: number
  revenue: number
  status: FlightStatus
  created_at: string
  updated_at: string
}

export interface NewFlightInput {
  flight_number: string
  origin: string
  destination: string
  departure_time: string
  arrival_time: string
  capacity: number
  booked_seats: number
  revenue: number
  status: FlightStatus
}

export type FlightUpdateInput = Partial<NewFlightInput>

export interface DashboardSummary {
  flightsByDay: Array<{ date: string; flights: number }>
  totalRevenue: number
  totalCapacity: number
  totalBooked: number
  averageOccupancy: number
}

export interface LoginPayload {
  email: string
  password: string
}
