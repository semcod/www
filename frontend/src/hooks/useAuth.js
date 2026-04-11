import { useEffect } from "react";
import { fetchMe, logout as logoutRequest } from "../api.js";
import { API } from "../constants.js";

export function useSessionCallbackBootstrap(setSessionToken, sessionKey) {
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const session = searchParams.get("session");

    if (!session) {
      return;
    }

    setSessionToken(session);
    localStorage.setItem(sessionKey, session);
    window.history.replaceState({}, "", window.location.pathname + window.location.hash);
  }, [sessionKey, setSessionToken]);
}

export function useSessionProfile(sessionToken, setSessionToken, setUser, sessionKey) {
  useEffect(() => {
    if (!sessionToken) {
      setUser(null);
      return;
    }

    fetchMe(sessionToken)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(sessionKey);
        setSessionToken(null);
        setUser(null);
      });
  }, [sessionKey, sessionToken, setSessionToken, setUser]);
}

export function getOAuthStartUrl() {
  return `${API}/auth/github`;
}

export function confirmAuthFlow(sessionToken, setPhase) {
  setPhase("repos");
}


export async function logoutSession(sessionToken, sessionKey, setSessionToken, setUser, reset) {
  if (sessionToken) {
    try {
      await logoutRequest(sessionToken);
    } catch (error) {
    }
  }

  localStorage.removeItem(sessionKey);
  setSessionToken(null);
  setUser(null);
  reset();
}
