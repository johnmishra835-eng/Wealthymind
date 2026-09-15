<?php
/**
 * Contact form handler for the Wealthymind Research website.
 *
 * Receives a POST from contact.html and emails it. Plain PHP with no
 * dependencies, because Hostinger shared hosting provides PHP and a local mail
 * transport — no third-party form service is needed.
 *
 * On success it redirects to thank-you.html. On failure it redirects back to
 * contact.html with an error code, which the page shows above the form.
 *
 * ---------------------------------------------------------------------------
 * IMPORTANT: the From address must be a real mailbox on this domain. Mail sent
 * with the visitor's address in From is rejected or spam-filed by most
 * providers, because this server is not authorised to send as their domain.
 * The visitor's address goes in Reply-To instead, so replying still works.
 * ---------------------------------------------------------------------------
 */

declare(strict_types=1);

// --- settings ---------------------------------------------------------------

const MAIL_TO       = 'info@wmrpl.com';   // where enquiries are delivered
const MAIL_FROM     = 'info@wmrpl.com';   // must be a mailbox on this domain
const MAIL_FROM_NAME = 'Wealthymind Research website';
const SITE_NAME     = 'Wealthymind Research Private Limited';

const MAX_PER_HOUR  = 5;                  // submissions allowed per IP per hour
const MIN_SECONDS   = 3;                  // reject anything faster than a human

// --- helpers ----------------------------------------------------------------

/** Strip CR/LF so a value can never inject extra mail headers. */
function headerSafe(string $value): string
{
    return trim(str_replace(["\r", "\n", "%0a", "%0d"], ' ', $value));
}

function field(string $name): string
{
    $raw = $_POST[$name] ?? '';
    if (!is_string($raw)) {
        return '';
    }
    // normalise newlines, strip control characters except tab and newline
    $raw = str_replace(["\r\n", "\r"], "\n", $raw);
    $raw = preg_replace('/[^\P{C}\n\t]+/u', '', $raw) ?? '';
    return trim($raw);
}

/**
 * Single-line fields must not keep newlines. Without this, a name containing
 * CRLF still lands on its own line in the message body, which reads as though
 * it were a real header even though headerSafe() stops it becoming one.
 */
function line(string $name): string
{
    return trim(preg_replace('/\s+/u', ' ', field($name)) ?? '');
}

function fail(string $code): never
{
    header('Location: contact.html?error=' . urlencode($code) . '#enquiry', true, 303);
    exit;
}

function succeed(): never
{
    header('Location: thank-you.html', true, 303);
    exit;
}

// --- only accept POST -------------------------------------------------------

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    header('Location: contact.html', true, 303);
    exit;
}

// --- spam traps -------------------------------------------------------------

// Honeypot: a field hidden from people, so anything in it came from a bot.
if (field('website') !== '') {
    succeed(); // answer as if it worked, so the bot does not retry
}

// Time trap: a genuine person cannot read and complete the form instantly.
$started = (int) ($_POST['started'] ?? 0);
if ($started > 0 && (time() - $started) < MIN_SECONDS) {
    succeed();
}

// Rate limit per IP. Best effort — the temp directory may be cleared, which
// only means a visitor gets their full allowance again.
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? 'unknown');
$bucket = sys_get_temp_dir() . '/wm-contact-' . hash('sha256', $ip) . '.txt';
$now = time();
$hits = [];
if (is_readable($bucket)) {
    $hits = array_filter(
        array_map('intval', explode(',', (string) file_get_contents($bucket))),
        static fn(int $t): bool => $t > $now - 3600
    );
}
if (count($hits) >= MAX_PER_HOUR) {
    fail('rate');
}
$hits[] = $now;
@file_put_contents($bucket, implode(',', $hits), LOCK_EX);

// --- validate ---------------------------------------------------------------

$name    = line('name');
$company = line('company');
$email   = line('email');
$phone   = line('phone');
$topic   = line('topic');
$message = field('message');   // the only field that may contain newlines
$consent = isset($_POST['consent']);

$allowedTopics = [
    'Private Equity raise',
    'Venture Capital raise',
    'Pre-IPO Placement',
    'IPO & Capital Market Advisory',
    'Debt Syndication',
    'Structured Finance',
    'Due Diligence',
    'Something else',
];

if ($name === '' || $company === '' || $email === '' || $topic === '' || $message === '') {
    fail('required');
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    fail('email');
}
if ($phone !== '' && !preg_match('/^[6-9][0-9]{9}$/', $phone)) {
    fail('phone');
}
if (!in_array($topic, $allowedTopics, true)) {
    fail('topic');
}
if (mb_strlen($message) < 20) {
    fail('message');
}
if (!$consent) {
    fail('consent');
}
if (mb_strlen($name) > 120 || mb_strlen($company) > 160 || mb_strlen($message) > 6000) {
    fail('length');
}

// --- compose ----------------------------------------------------------------

$subject = headerSafe(sprintf('Website enquiry — %s (%s)', $topic, $company));

$body = implode("\n", [
    'A new enquiry was submitted on the ' . SITE_NAME . ' website.',
    '',
    'Name:     ' . $name,
    'Company:  ' . $company,
    'Email:    ' . $email,
    'Phone:    ' . ($phone !== '' ? $phone : '(not given)'),
    'Topic:    ' . $topic,
    '',
    'Message:',
    '--------',
    $message,
    '',
    '--------',
    'Submitted: ' . gmdate('d M Y H:i') . ' UTC',
    'IP:        ' . $ip,
    '',
    'Reply directly to this email to respond to the sender.',
]);

$headers = [
    'From: ' . headerSafe(MAIL_FROM_NAME) . ' <' . MAIL_FROM . '>',
    'Reply-To: ' . headerSafe($name) . ' <' . headerSafe($email) . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: PHP/' . phpversion(),
];

$sent = @mail(
    MAIL_TO,
    '=?UTF-8?B?' . base64_encode($subject) . '?=',
    wordwrap($body, 78, "\n", true),
    implode("\r\n", $headers),
    '-f' . MAIL_FROM
);

if (!$sent) {
    /**
     * Keep a copy so an enquiry is not lost if the mail transport is
     * misconfigured. Written one level ABOVE public_html: this file holds a
     * visitor's name, email and message, and must never be reachable over the
     * web. .htaccess also blocks .log, but a file outside the web root is safe
     * even if .htaccess is missing.
     */
    $log = dirname(__DIR__) . '/wm-contact-failed.log';
    if (!@is_writable(dirname($log))) {
        $log = sys_get_temp_dir() . '/wm-contact-failed.log';
    }
    @file_put_contents(
        $log,
        gmdate('c') . "\t" . str_replace("\n", ' | ', $body) . "\n",
        FILE_APPEND | LOCK_EX
    );
    fail('send');
}

succeed();
