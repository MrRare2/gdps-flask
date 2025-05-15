# Submissions by unregistered accounts
# True — unregistered accounts can interact with GDPS
# False — only registered accounts can interact with GDPS
unregistered_submissions = True

# Preactivate accounts
# True — all new accounts are automatically registered
# False — new accounts must be activated
preactivate_accounts = True

# Debug mode
# True — show errors
# False — disable error reporting
debug_mode = True

# Captcha settings
enable_captcha = False
captcha_type = 1  # 1: hCaptcha, 2: reCaptcha, 3: Cloudflare Turnstile
captcha_key = ""
captcha_secret = ""

# Block access from free proxies and common VPNs
block_free_proxies = False
block_common_vpns = False

proxies = {
    "http": "https://fhgdps.com/proxies/http.txt",
    "https": "https://fhgdps.com/proxies/https.txt",
    "socks4": "https://fhgdps.com/proxies/socks4.txt",
    "socks5": "https://fhgdps.com/proxies/socks5.txt",
    "unknown": "https://fhgdps.com/proxies/unknown.txt"
}

vpns = {
    "vpn": "https://raw.githubusercontent.com/X4BNet/lists_vpn/main/output/vpn/ipv4.txt"
}

# GDPS automod config

# -- SECURITY --
rate_limit_ban_multiplier = 2
rate_limit_ban_time = 3600

max_login_tries = 4

stats_time_check = 600
max_stars_possible = 150
max_moons_possible = 150
max_user_coins_possible = 80
max_demons_possible = 30

# -- ANTI-SPAM --
warnings_period = 302400

levels_count_modifier = 1.3
levels_days_check_period = 7
levels_spam_upload_disable = 1200

accounts_count_modifier = 1.3
accounts_days_check_period = 7
accounts_spam_upload_disable = 1200

comments_check_period = 600
comments_spam_upload_disable = 600

global_levels_upload_delay = 2
per_user_levels_upload_delay = 5
accounts_register_delay = 5
users_create_delay = 10

filter_time_check = 60
filter_rate_limit_ban = 10

# -- CONTENT FILTERS --
filter_usernames = 2
banned_usernames = [
    "RobTop",
    "nig",
    "fag"
]
whitelisted_usernames = [
    "night"
]

filter_clan_names = 2
banned_clan_names = [
    "Support",
    "Administration",
    "Moderation",
    "nig",
    "fag"
]
whitelisted_clan_names = [
    "night"
]

filter_clan_tags = 2
banned_clan_tags = [
    "ADM",
    "MOD",
    "nig",
    "fag"
]
whitelisted_clan_tags = [
    "night"
]

filter_common = 2
banned_common = [
    "nig",
    "fag"
]
whitelisted_common = [
    "night"
]

