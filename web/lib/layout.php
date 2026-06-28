<?php
/** Shared HTML helpers and page chrome for the semcod.com portal. */

function e(?string $s): string
{
    return htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** A safe repo slug (org repo names: letters, digits, ., _, -). */
function clean_repo(string $s): string
{
    return preg_replace('/[^A-Za-z0-9._-]/', '', $s);
}

/** Short relative "x days ago" style label from an ISO-8601 timestamp. */
function ago(?string $iso): string
{
    if (!$iso) {
        return '';
    }
    $t = strtotime($iso);
    if (!$t) {
        return '';
    }
    $d = max(0, time() - $t);
    $units = [31536000 => 'y', 2592000 => 'mo', 604800 => 'w', 86400 => 'd', 3600 => 'h', 60 => 'min'];
    foreach ($units as $secs => $label) {
        if ($d >= $secs) {
            return intdiv($d, $secs) . $label . ' ago';
        }
    }
    return 'just now';
}

function layout_head(string $title, string $description = ''): void
{
    ?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?= e($title) ?></title>
<meta name="description" content="<?= e($description) ?>">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="/">semcod</a>
  <nav>
    <a href="/">Projects</a>
    <a href="https://github.com/orgs/semcod/repositories" target="_blank" rel="noopener">GitHub org</a>
  </nav>
</header>
<main><?php
}

function layout_foot(): void
{
    ?></main>
<footer class="foot">
  <p>Auto-generated from <a href="https://github.com/orgs/semcod/repositories" target="_blank" rel="noopener">github.com/orgs/semcod</a> · semcod ecosystem</p>
</footer>
</body>
</html><?php
}
