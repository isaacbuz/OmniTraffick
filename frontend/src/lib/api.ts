const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = "ApiError"
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }))
    throw new ApiError(response.status, error.detail || response.statusText)
  }

  return response.json()
}

// Markets
export const marketsApi = {
  list: () => fetchApi<any[]>("/api/v1/markets"),
  get: (id: string) => fetchApi<any>(`/api/v1/markets/${id}`),
  create: (data: any) => fetchApi<any>("/api/v1/markets", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => fetchApi<any>(`/api/v1/markets/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: string) => fetchApi<void>(`/api/v1/markets/${id}`, {
    method: "DELETE",
  }),
}

// Brands
export const brandsApi = {
  list: () => fetchApi<any[]>("/api/v1/brands"),
  get: (id: string) => fetchApi<any>(`/api/v1/brands/${id}`),
  create: (data: any) => fetchApi<any>("/api/v1/brands", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => fetchApi<any>(`/api/v1/brands/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: string) => fetchApi<void>(`/api/v1/brands/${id}`, {
    method: "DELETE",
  }),
}

// Channels
export const channelsApi = {
  list: () => fetchApi<any[]>("/api/v1/channels"),
  get: (id: string) => fetchApi<any>(`/api/v1/channels/${id}`),
  create: (data: any) => fetchApi<any>("/api/v1/channels", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => fetchApi<any>(`/api/v1/channels/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: string) => fetchApi<void>(`/api/v1/channels/${id}`, {
    method: "DELETE",
  }),
}

// Campaigns
export const campaignsApi = {
  list: () => fetchApi<any[]>("/api/v1/campaigns"),
  get: (id: string) => fetchApi<any>(`/api/v1/campaigns/${id}`),
  create: (data: any) => fetchApi<any>("/api/v1/campaigns", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => fetchApi<any>(`/api/v1/campaigns/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: string) => fetchApi<void>(`/api/v1/campaigns/${id}`, {
    method: "DELETE",
  }),
}

// Tickets
export const ticketsApi = {
  list: () => fetchApi<any[]>("/api/v1/tickets"),
  get: (id: string) => fetchApi<any>(`/api/v1/tickets/${id}`),
  create: (data: any) => fetchApi<any>("/api/v1/tickets", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => fetchApi<any>(`/api/v1/tickets/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: string) => fetchApi<void>(`/api/v1/tickets/${id}`, {
    method: "DELETE",
  }),
}

// Deployment
export const deployApi = {
  deploy: (ticketId: string) => fetchApi<any>("/api/v1/deploy", {
    method: "POST",
    body: JSON.stringify({ ticket_id: ticketId }),
  }),
  status: (taskId: string) => fetchApi<any>(`/api/v1/deploy/status/${taskId}`),
}
