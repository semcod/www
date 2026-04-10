import { useEffect } from "react";
import { fetchMe, demoLogin, logout as logoutRequest } from "../api.js";
import { DEMO_REPOS, API } from "../constants.js";

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

export function confirmAuthFlow(sessionToken, setRepos, setPhase) {
  if (sessionToken) {
    setPhase("repos");
    return;
  }

  setRepos(DEMO_REPOS);
  setPhase("repos");
}

export async function startDemoSession(setSessionToken, setRepos, setPhase, sessionKey) {
  try {
    const data = await demoLogin();
    if (!data.session) {
      return;
    }

    setSessionToken(data.session);
    localStorage.setItem(sessionKey, data.session);
    setRepos(DEMO_REPOS);
    setPhase("repos");
  } catch (error) {
  }
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
