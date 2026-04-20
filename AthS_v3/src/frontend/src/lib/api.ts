import axios, { type AxiosInstance, type AxiosError } from 'axios'

const API_BASE_URL = '/api'

export interface ApiResponse<T> {
  data: T
  count?: number
}

export interface ApiError {
  error: string
  message: string
  request_id: string
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response) {
          console.error('API Error:', error.response.data)
        } else if (error.request) {
          console.error('No response received:', error.request)
        } else {
          console.error('Request error:', error.message)
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await this.client.get<ApiResponse<T>>(endpoint)
    return response.data
  }

  async post<T, D = unknown>(endpoint: string, data?: D): Promise<ApiResponse<T>> {
    const response = await this.client.post<ApiResponse<T>>(endpoint, data)
    return response.data
  }

  async put<T, D = unknown>(endpoint: string, data?: D): Promise<ApiResponse<T>> {
    const response = await this.client.put<ApiResponse<T>>(endpoint, data)
    return response.data
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await this.client.delete<ApiResponse<T>>(endpoint)
    return response.data
  }
}

export const api = new ApiClient()

export default api
