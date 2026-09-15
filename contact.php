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

/**
 * SMTP relay — STRONGLY RECOMMENDED when the mailbox is on Google Workspace
 * (or any mail host that is not this web server).
 *
 * Two things break PHP's built-in mail() in that situation:
 *
 *  1. The web server may decide it handles this domain's mail itself and try
 *     to deliver locally, to a mailbox that does not exist there. The message
 *     then vanishes without an error.
 *  2. The domain's SPF record lists Google as the only authorised sender, so a
 *     message sent straight from the web server fails SPF and is spam-filed or
 *     rejected.
 *
 * Relaying through Workspace fixes both: the mail genuinely originates from
 * Google, so SPF and DKIM pass and delivery is reliable.
 *
 * To enable, fill these in. Leave SMTP_HOST empty to fall back to mail().
 * SMTP_PASS must be a Google APP PASSWORD, not the account password —
 * Google Account > Security > 2-Step Verification > App passwords.
 */
const SMTP_HOST = '';                     // e.g. 'smtp.gmail.com'
const SMTP_PORT = 587;                    // 587 = STARTTLS
const SMTP_USER = '';                     // e.g. 'info@wmrpl.com'
const SMTP_PASS = '';                     // 16-character app password
const SMTP_TLS  = true;                   // STARTTLS; false only for testing

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

/**
 * Minimal SMTP client: connect, EHLO, STARTTLS, AUTH LOGIN, envelope, DATA.
 * Written out rather than pulling in a library so the site stays a plain
 * upload with no composer step.
 */
function smtpSend(string $to, string $subjectEncoded, string $body, array $headers, string &$error = null): bool
{
    $socket = @stream_socket_client(
        sprintf('tcp://%s:%d', SMTP_HOST, SMTP_PORT),
        $errno,
        $errstr,
        20,
        STREAM_CLIENT_CONNECT
    );
    if (!$socket) {
        $error = "connect failed: $errstr ($errno)";
        return false;
    }
    stream_set_timeout($socket, 20);

    $read = static function () use ($socket, &$error): string {
        $out = '';
        while (($line = fgets($socket, 1024)) !== false) {
            $out .= $line;
            // a multi-line reply has a hyphen after the code; the last does not
            if (strlen($line) < 4 || $line[3] !== '-') {
                break;
            }
        }
        return $out;
    };

    $cmd = static function (string $line, string $expect) use ($socket, $read, &$error): bool {
        if ($line !== '') {
            fwrite($socket, $line . "\r\n");
        }
        $reply = $read();
        if (strncmp($reply, $expect, strlen($expect)) !== 0) {
            $error = trim(($line !== '' ? explode(' ', $line)[0] : 'greeting') . ' -> ' . $reply);
            return false;
        }
        return true;
    };

    $ok = $cmd('', '220')
        && $cmd('EHLO ' . (SMTP_USER !== '' ? explode('@', SMTP_USER)[1] : 'localhost'), '250');

    if ($ok && SMTP_TLS) {
        $ok = $cmd('STARTTLS', '220');
        if ($ok) {
            $ok = @stream_socket_enable_crypto(
                $socket,
                true,
                STREAM_CRYPTO_METHOD_TLS_CLIENT
            );
            if (!$ok) {
                $error = 'STARTTLS negotiation failed';
            } else {
                // the session resets after TLS, so greet again
                $ok = $cmd('EHLO ' . explode('@', SMTP_USER)[1], '250');
            }
        }
    }

    if ($ok && SMTP_USER !== '') {
        $ok = $cmd('AUTH LOGIN', '334')
            && $cmd(base64_encode(SMTP_USER), '334')
            && $cmd(base64_encode(SMTP_PASS), '235');
    }

    if ($ok) {
        $data = implode("\r\n", $headers) . "\r\n"
            . 'To: ' . $to . "\r\n"
            . 'Subject: ' . $subjectEncoded . "\r\n"
            . 'Date: ' . date(DATE_RFC2822) . "\r\n"
            . "\r\n"
            // a lone "." would end DATA early, so any line that is just a dot
            // is escaped to ".."
            . preg_replace('/^\./m', '..', str_replace("\n", "\r\n", $body));

        $ok = $cmd('MAIL FROM:<' . MAIL_FROM . '>', '250')
            && $cmd('RCPT TO:<' . $to . '>', '250')
            && $cmd('DATA', '354')
            && $cmd($data . "\r\n.", '250');
    }

    @fwrite($socket, "QUIT\r\n");
    @fclose($socket);
    return (bool) $ok;
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
    'Insolvency Advisory',
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

$subjectEncoded = '=?UTF-8?B?' . base64_encode($subject) . '?=';
$wrapped = wordwrap($body, 78, "\n", true);
$smtpError = null;

if (SMTP_HOST !== '') {
    $sent = smtpSend(MAIL_TO, $subjectEncoded, $wrapped, $headers, $smtpError);
} else {
    $sent = @mail(
        MAIL_TO,
        $subjectEncoded,
        $wrapped,
        implode("\r\n", $headers),
        '-f' . MAIL_FROM
    );
}

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
        gmdate('c') . "\t" . ($smtpError ?? 'mail() returned false') . "\t"
            . str_replace("\n", ' | ', $body) . "\n",
        FILE_APPEND | LOCK_EX
    );
    fail('send');
}

succeed();
