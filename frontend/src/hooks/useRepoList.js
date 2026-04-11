import { useState, useEffect } from "react";
import { fetchRepos } from "../api.js";

export function useRepoList(sessionToken, phase) {
  const [repos, setRepos] = useState([]);

  useEffect(() => {
    if (!sessionToken || phase !== "repos") {
      return;
    }

    fetchRepos(sessionToken)
      .then(setRepos)
      .catch(() => setRepos([]));
  }, [phase, sessionToken]);

  return { repos, setRepos };
}
