import { create } from "zustand";
import { persist } from "zustand/middleware";

// Persisted auth state: tokens + current user.
export const useAuthStore = create(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,

      setTokens: ({ access_token, refresh_token }) =>
        set({ accessToken: access_token, refreshToken: refresh_token }),
      setUser: (user) => set({ user }),
      logout: () => set({ accessToken: null, refreshToken: null, user: null }),
    }),
    { name: "bayan.auth" }
  )
);

export const isAuthenticated = () => !!useAuthStore.getState().accessToken;
