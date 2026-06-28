<?php
/**
 * Tiny cached GitHub REST API client for the semcod.com portal.
 *
 * All responses are cached on disk so the public site stays fast and well
 * under GitHub's rate limit even with many visitors.
 */

class GitHub
{
    private string $token;
    private string $cacheDir;

    public function __construct(string $token, string $cacheDir)
    {
        $this->token = $token;
        $this->cacheDir = $cacheDir;
        if (!is_dir($cacheDir)) {
            @mkdir($cacheDir, 0775, true);
        }
    }

    /** Cached GET returning decoded JSON (assoc array), or null on failure. */
    public function getJson(string $url, int $ttl): ?array
    {
        $raw = $this->getRaw($url, $ttl, ['Accept: application/vnd.github+json']);
        if ($raw === null) {
            return null;
        }
        $data = json_decode($raw, true);
        return is_array($data) ? $data : null;
    }

    /** Cached GET returning the raw response body, or null on failure. */
    public function getRaw(string $url, int $ttl, array $headers = []): ?string
    {
        $key = $this->cacheDir . '/' . sha1($url) . '.cache';
        if (is_file($key) && (time() - filemtime($key)) < $ttl) {
            $cached = file_get_contents($key);
            if ($cached !== false) {
                return $cached;
            }
        }

        $body = $this->fetch($url, $headers);
        if ($body !== null) {
            @file_put_contents($key, $body, LOCK_EX);
            return $body;
        }

        // On a failed live fetch, fall back to a stale cache entry if present
        // so a rate-limit blip never blanks the site.
        if (is_file($key)) {
            $stale = file_get_contents($key);
            if ($stale !== false) {
                return $stale;
            }
        }
        return null;
    }

    private function fetch(string $url, array $headers): ?string
    {
        $hdrs = array_merge([
            'User-Agent: semcod-portal',
            'X-GitHub-Api-Version: 2022-11-28',
        ], $headers);
        if ($this->token !== '') {
            $hdrs[] = 'Authorization: Bearer ' . $this->token;
        }

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER     => $hdrs,
            CURLOPT_TIMEOUT        => 15,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYPEER => true,
        ]);
        $body = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($body === false || $code < 200 || $code >= 300) {
            return null;
        }
        return $body;
    }

    /**
     * All public repos of an org, sorted by most-recently pushed.
     * Follows pagination up to 300 repos.
     */
    public function orgRepos(string $org, int $ttl): array
    {
        $all = [];
        for ($page = 1; $page <= 3; $page++) {
            $url = sprintf(
                'https://api.github.com/orgs/%s/repos?per_page=100&page=%d&type=public&sort=pushed',
                rawurlencode($org),
                $page
            );
            $batch = $this->getJson($url, $ttl);
            if (!$batch) {
                break;
            }
            foreach ($batch as $r) {
                $all[] = $r;
            }
            if (count($batch) < 100) {
                break;
            }
        }
        return $all;
    }

    /** Decoded README markdown for a repo, or null if none. */
    public function readme(string $org, string $repo, int $ttl): ?string
    {
        $url = sprintf(
            'https://api.github.com/repos/%s/%s/readme',
            rawurlencode($org),
            rawurlencode($repo)
        );
        $data = $this->getJson($url, $ttl);
        if (!$data || empty($data['content'])) {
            return null;
        }
        $decoded = base64_decode(str_replace("\n", '', $data['content']), true);
        return $decoded === false ? null : $decoded;
    }
}
