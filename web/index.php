<?php
/**
 * semcod.com — project portal homepage.
 *
 * Auto-generates the list of every public repository in the `semcod` GitHub
 * organisation, with description, primary language, stars and last-push time.
 * Each card links to a generated subpage rendering that repo's README.
 */

declare(strict_types=1);

$cfg = require __DIR__ . '/config.php';
require __DIR__ . '/lib/gh.php';
require __DIR__ . '/lib/layout.php';

$gh    = new GitHub($cfg['token'], $cfg['cache_dir']);
$repos = $gh->orgRepos($cfg['org'], $cfg['cache_ttl']);

// Drop forks/archived noise to the bottom; keep most-recently pushed first.
usort($repos, function ($a, $b) {
    $aa = !empty($a['archived']) ? 1 : 0;
    $ba = !empty($b['archived']) ? 1 : 0;
    if ($aa !== $ba) {
        return $aa <=> $ba;
    }
    return strcmp($b['pushed_at'] ?? '', $a['pushed_at'] ?? '');
});

layout_head(
    'semcod · projects',
    'Auto-generated catalogue of all semcod open-source projects — what each one does, how it works and what it is for.'
);
?>
<section class="hero">
  <h1>semcod projects</h1>
  <p>The full catalogue of the <strong>semcod</strong> ecosystem, generated live from
     GitHub. Each project below shows what it does and how it currently works — open
     any card to read its full documentation.</p>
</section>

<?php if (!$repos): ?>
  <p class="empty">Could not load repositories from GitHub right now. Please try again in a moment.</p>
<?php else: ?>
  <p class="count"><?= count($repos) ?> projects</p>
  <ul class="grid">
    <?php foreach ($repos as $r):
        $name = (string)($r['name'] ?? '');
        if ($name === '') { continue; }
        $desc = (string)($r['description'] ?? '');
        $lang = (string)($r['language'] ?? '');
        $stars = (int)($r['stargazers_count'] ?? 0);
        $topics = is_array($r['topics'] ?? null) ? $r['topics'] : [];
    ?>
    <li class="card">
      <a class="card-link" href="/repo.php?name=<?= e(rawurlencode($name)) ?>">
        <h2><?= e($name) ?><?php if (!empty($r['archived'])): ?> <span class="tag archived">archived</span><?php endif; ?></h2>
        <p class="desc"><?= $desc !== '' ? e($desc) : '<em>No description provided.</em>' ?></p>
      </a>
      <div class="meta">
        <?php if ($lang): ?><span class="tag lang"><?= e($lang) ?></span><?php endif; ?>
        <?php if ($stars): ?><span class="tag">★ <?= $stars ?></span><?php endif; ?>
        <span class="tag muted"><?= e(ago($r['pushed_at'] ?? null)) ?></span>
      </div>
      <?php if ($topics): ?>
      <div class="topics">
        <?php foreach (array_slice($topics, 0, 5) as $t): ?><span class="topic"><?= e($t) ?></span><?php endforeach; ?>
      </div>
      <?php endif; ?>
      <div class="links">
        <a href="/repo.php?name=<?= e(rawurlencode($name)) ?>">Docs →</a>
        <a href="<?= e($r['html_url'] ?? '#') ?>" target="_blank" rel="noopener">GitHub</a>
      </div>
    </li>
    <?php endforeach; ?>
  </ul>
<?php endif; ?>

<?php layout_foot();
