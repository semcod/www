<?php
/**
 * Site configuration for the semcod.com project portal.
 *
 * A GitHub token is optional but recommended: without it the GitHub API
 * limits unauthenticated requests to 60/hour per server IP. With a token
 * (read-only / public_repo scope is plenty) the limit is 5000/hour.
 *
 * Provide the token in ANY of these ways (checked in order):
 *   1. Environment variable GITHUB_TOKEN (set in Plesk > PHP settings).
 *   2. A file config.local.php next to this one returning the token string,
 *      e.g.:  <?php return 'ghp_xxx';
 *   3. Leave empty to run unauthenticated.
 */

return [
    'org'         => 'semcod',
    'cache_dir'   => __DIR__ . '/cache',
    'cache_ttl'   => 1800,          // seconds (30 min) for the repo list
    'readme_ttl'  => 3600,          // seconds (1 h) for individual READMEs
    'token'       => (function () {
        $env = getenv('GITHUB_TOKEN');
        if ($env) {
            return trim($env);
        }
        $local = __DIR__ . '/config.local.php';
        if (is_file($local)) {
            $t = include $local;
            if (is_string($t) && $t !== '') {
                return trim($t);
            }
        }
        return '';
    })(),
];
