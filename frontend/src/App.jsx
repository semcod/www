import { useAppState } from "./hooks/useAppState";
import { Header } from "./components/Header";
import { ProgressSteps } from "./components/ProgressSteps";
import { LandingPhase, AuthPhase, ReposPhase, ScanningPhase, ResultPhase } from "./components/phases";
import { PRBotTab, RepoTab, BadgeTab, RecentScansTab } from "./components/tabs";
import { C } from "./constants";

export default function App() {
  const {
    tab, setTab,
    phase,
    repos,
    selectedRepo,
    scanProgress, scanLabel,
    audit,
    repoUrl, setRepoUrl,
    isSandbox,
    sessionToken, user,
    reset, startOAuth, confirmAuth, startAudit, startSandbox, startDemoLogin, doLogout,
  } = useAppState();

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.fg }}>
      <Header tab={tab} setTab={setTab} reset={reset} user={user} doLogout={doLogout} />

      <main style={{ maxWidth: 1000, margin: "0 auto", padding: "32px 24px 80px" }}>
        {tab === "audit" && (
          <>
            <ProgressSteps phase={phase} />

            {phase === "landing" && (
              <LandingPhase
                key={`landing-${Date.now()}`}
                startOAuth={startOAuth}
                startDemoLogin={startDemoLogin}
                repoUrl={repoUrl}
                setRepoUrl={setRepoUrl}
                startSandbox={startSandbox}
              />
            )}

            {phase === "auth" && <AuthPhase />}

            {phase === "repos" && (
              <ReposPhase repos={repos} startAudit={startAudit} />
            )}

            {phase === "scanning" && (
              <ScanningPhase
                scanProgress={scanProgress}
                scanLabel={scanLabel}
                selectedRepo={selectedRepo}
              />
            )}

            {(phase === "value" || phase === "trial") && (
              <ResultPhase
                audit={audit}
                selectedRepo={selectedRepo}
                isSandbox={isSandbox}
                reset={reset}
              />
            )}

            {phase === "result" && (
              <ResultPhase
                audit={audit}
                selectedRepo={selectedRepo}
                isSandbox={isSandbox}
                reset={reset}
              />
            )}
          </>
        )}

        {tab === "prbot" && <PRBotTab />}
        {tab === "recent" && <RecentScansTab />}
        {tab === "repo" && <RepoTab />}
        {tab === "badge" && <BadgeTab />}
      </main>
    </div>
  );
}
