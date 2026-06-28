<?php
/**
 * semcod.com — per-project documentation subpage.
 *
 * Renders a repository's README (fetched from GitHub) as a styled HTML page,
 * with a header summarising what the project is and what it is for.
 */

declare(strict_types=1);

$cfg = require __DIR__ . '/config.php';
require __DIR__ . '/lib/gh.php';
require __DIR__ . '/lib/layout.php';
require __DIR__ . '/lib/Parsedown.php';

$name = clean_repo((string)($_GET['name'] ?? ''));
if ($name === '') {
    http_response_code(400);
    layout_head('semcod · project');
    echo '<p class="empty">No project specified. <a href="/">Back to all projects</a>.</p>';
    layout_foot();
    exit;
}

$gh = new GitHub($cfg['token'], $cfg['cache_dir']);

// Pull metadata from the cached org listing (no extra API call needed).
$repos = $gh->orgRepos($cfg['org'], $cfg['cache_ttl']);
$meta = null;
foreach ($repos as $r) {
    if (strcasecmp((string)($r['name'] ?? ''), $name) === 0) {
        $meta = $r;
        break;
    }
}

if ($meta === null) {
    http_response_code(404);
    layout_head('semcod · not found');
    echo '<p class="empty">Project <code>' . e($name) . '</code> was not found in the semcod organisation. <a href="/">Back to all projects</a>.</p>';
    layout_foot();
    exit;
}

$realName = (string)$meta['name'];
$branch   = (string)($meta['default_branch'] ?? 'main');
$desc     = (string)($meta['description'] ?? '');
$homepage = (string)($meta['homepage'] ?? '');

$md = $gh->readme($cfg['org'], $realName, $cfg['readme_ttl']);

$parsedown = new Parsedown();
$parsedown->setSafeMode(true);          // escape raw HTML embedded in READMEs
$parsedown->setBreaksEnabled(true);
$html = $md !== null ? $parsedown->text($md) : '';

// Rewrite relative links/images so README assets resolve against GitHub.
if ($html !== '') {
    $rawBase  = "https://raw.githubusercontent.com/{$cfg['org']}/{$realName}/{$branch}/";
    $blobBase = "https://github.com/{$cfg['org']}/{$realName}/blob/{$branch}/";
    $isAbs = fn(string $u): bool => (bool)preg_match('#^(https?:)?//|^#|^mailto:|^data:#i', $u);

    $html = preg_replace_callback('#(<img\b[^>]*?\bsrc=")([^"]+)(")#i', function ($m) use ($rawBase, $isAbs) {
        return $isAbs($m[2]) ? $m[0] : $m[1] . $rawBase . ltrim($m[2], './') . $m[3];
    }, $html);

    $html = preg_replace_callback('#(<a\b[^>]*?\bhref=")([^"]+)(")#i', function ($m) use ($blobBase, $isAbs) {
        return $isAbs($m[2]) ? $m[0] : $m[1] . $blobBase . ltrim($m[2], './') . $m[3];
    }, $html);
}

layout_head(
    'semcod · ' . $realName,
    $desc !== '' ? $desc : ('Documentation for the semcod project ' . $realName)
);
?>
<article class="doc">
  <p class="crumb"><a href="/">← all projects</a></p>
  <header class="doc-head">
    <h1><?= e($realName) ?></h1>
    <?php if ($desc !== ''): ?><p class="lead"><?= e($desc) ?></p><?php endif; ?>
    <div class="meta">
      <?php if (!empty($meta['language'])): ?><span class="tag lang"><?= e($meta['language']) ?></span><?php endif; ?>
      <?php if (!empty($meta['stargazers_count'])): ?><span class="tag">★ <?= (int)$meta['stargazers_count'] ?></span><?php endif; ?>
      <span class="tag muted">updated <?= e(ago($meta['pushed_at'] ?? null)) ?></span>
      <a class="tag link" href="<?= e($meta['html_url'] ?? '#') ?>" target="_blank" rel="noopener">View on GitHub →</a>
      <?php if ($homepage !== ''): ?><a class="tag link" href="<?= e($homepage) ?>" target="_blank" rel="noopener">Homepage</a><?php endif; ?>
    </div>
  </header>

  <div class="readme">
    <?php if ($html !== ''): ?>
      <?= $html /* sanitised via Parsedown safe mode */ ?>
    <?php else: ?>
      <p class="empty">This project has no README yet.
         <?php if ($desc !== ''): ?>In short: <?= e($desc) ?><?php endif; ?></p>
    <?php endif; ?>
  </div>
</article>
<?php layout_foot();
