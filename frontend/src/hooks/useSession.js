import { useState, useCallback } from "react";
import {
  useSessionCallbackBootstrap,
  useSessionProfile,
  getOAuthStartUrl,
  confirmAuthFlow,
  logoutSession
} from "./useAuth.js";

export function useSession(sessionKey, setPhase) {
  const [sessionToken, setSessionToken] = useState(() => localStorage.getItem(sessionKey) || null);
  const [user, setUser] = useState(null);

  useSessionCallbackBootstrap(setSessionToken, sessionKey);
  useSessionProfile(sessionToken, setSessionToken, setUser, sessionKey);

  const startOAuth = useCallback(() => {
    window.location.href = getOAuthStartUrl();
  }, []);

  const confirmAuth = useCallback(() => {
    confirmAuthFlow(sessionToken, setPhase);
  }, [sessionToken, setPhase]);

  const clearSession = useCallback((reset) => {
    logoutSession(sessionToken, sessionKey, setSessionToken, setUser, reset);
  }, [sessionToken, setSessionToken, setUser]);

  return { sessionToken, setSessionToken, user, startOAuth, confirmAuth, clearSession };
}
