import { createContext, useCallback, useContext, useEffect, useMemo, useReducer } from 'react'
import type { ReactNode } from 'react'
import * as authService from '@/services/auth'
import { TOKEN_KEY, USER_KEY } from '@/services/api'
import type { User } from '@/types'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

interface AuthState {
  user: User | null
  isLoading: boolean
}

type AuthAction =
  | { type: 'session'; user: User | null }
  | { type: 'ready' }

const initialState: AuthState = { user: null, isLoading: true }

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'session':
      return { user: action.user, isLoading: false }
    case 'ready':
      return { ...state, isLoading: false }
  }
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      dispatch({ type: 'ready' })
      return
    }

    let active = true
    authService
      .getMe()
      .then((me) => {
        if (!active) return
        localStorage.setItem(USER_KEY, JSON.stringify(me))
        dispatch({ type: 'session', user: me })
      })
      .catch(() => {
        if (!active) return
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
        dispatch({ type: 'session', user: null })
      })

    const onUnauthorized = () => dispatch({ type: 'session', user: null })
    window.addEventListener('auth:unauthorized', onUnauthorized)
    return () => {
      active = false
      window.removeEventListener('auth:unauthorized', onUnauthorized)
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const payload = await authService.login(email, password)
    localStorage.setItem(TOKEN_KEY, payload.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(payload.user))
    dispatch({ type: 'session', user: payload.user })
  }, [])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const payload = await authService.register(name, email, password)
    localStorage.setItem(TOKEN_KEY, payload.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(payload.user))
    dispatch({ type: 'session', user: payload.user })
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch {
      // token may already be invalid; still clear local session
    }
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    dispatch({ type: 'session', user: null })
  }, [])

  const value = useMemo(
    () => ({
      user: state.user,
      isAuthenticated: state.user !== null,
      isLoading: state.isLoading,
      login,
      register,
      logout,
    }),
    [state, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
