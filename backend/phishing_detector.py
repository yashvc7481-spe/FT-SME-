"""
CyberGuard SME - Advanced Rule-Based Phishing Detection Engine
Transparent, explainable, multi-factor heuristic analysis of URLs.
"""

import re
import ipaddress
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote, parse_qs

# ---------------------------------------------------------------------------
# CONSTANTS & DICTIONARIES
# ---------------------------------------------------------------------------

TRUSTED_BRANDS = {
    "google": ["google.com", "google.co.in", "google.co.uk", "accounts.google.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com", "outlook.com", "login.microsoftonline.com"],
    "apple": ["apple.com", "icloud.com", "idmsa.apple.com"],
    "paypal": ["paypal.com", "paypal.me"],
    "amazon": ["amazon.com", "amazon.in", "amazon.co.uk"],
    "netflix": ["netflix.com"],
    "facebook": ["facebook.com", "fb.com", "meta.com"],
    "instagram": ["instagram.com"],
    "chase": ["chase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "bankofamerica": ["bankofamerica.com"],
    "binance": ["binance.com"],
    "metamask": ["metamask.io"],
    "coinbase": ["coinbase.com"],
    "dropbox": ["dropbox.com"],
    "github": ["github.com"],
    "linkedin": ["linkedin.com"]
}

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly",
    "rb.gy", "goo.gl", "ow.ly", "buff.ly", "rebrand.ly",
    "shorte.st", "adf.ly", "bl.ink", "trib.al"
}

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "verification", "secure", "security",
    "update", "account", "password", "wallet", "banking",
    "payment", "recovery", "confirm", "confirmation", "support-desk",
    "alert", "authenticate", "suspend", "suspended", "unlock"
]

HIGH_RISK_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".vbs", ".vbe",
    ".js", ".jse", ".wsf", ".wsh", ".ps1", ".iso",
    ".img", ".apk", ".jar", ".hta", ".cpl", ".msi"
}

STANDARD_PORTS = {80, 443, 8080, 8443}

TYPOSQUAT_SUBSTITUTIONS = {
    "0": "o", "1": "l", "i": "l", "5": "s", "@": "a", "vv": "w"
}


# ---------------------------------------------------------------------------
# SSRF & PRIVATE IP VALIDATION
# ---------------------------------------------------------------------------

def is_private_or_restricted_ip(ip_str):
    """Check if an IP string belongs to private, loopback, link-local, or reserved ranges."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# URL PARSING & NORMALIZATION
# ---------------------------------------------------------------------------

def validate_and_normalize_url(raw_url):
    """
    Validate and safely normalize a submitted URL string.
    Returns: (is_valid, normalized_url, parsed_obj, error_message)
    """
    if not isinstance(raw_url, str) or not raw_url.strip():
        return False, "", None, "Please provide a valid URL."

    cleaned = raw_url.strip()

    if len(cleaned) > 2048:
        return False, "", None, "URL exceeds maximum allowed length of 2048 characters."

    # Disallow control characters and spaces
    if re.search(r"[\s\u0000-\u001f\u007f]", cleaned):
        return False, "", None, "URL contains invalid whitespace or control characters."

    # Automatically prepend https:// if missing scheme
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned):
        cleaned = "https://" + cleaned

    try:
        parsed = urlparse(cleaned)
    except Exception as e:
        return False, "", None, f"Malformed URL: {str(e)}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, "", None, "Only HTTP and HTTPS URLs are supported."

    if not parsed.netloc:
        return False, "", None, "URL does not contain a valid host name."

    # Disallow embedded credentials in authority
    if parsed.username or parsed.password:
        pass  # Flagged later as a risk rule, but parsed correctly

    # Handle Punycode and IDN safely
    hostname = parsed.hostname or ""
    try:
        # Convert IDN to ascii punycode if needed
        hostname_ascii = hostname.encode("idna").decode("ascii")
    except Exception:
        hostname_ascii = hostname

    # Reconstruct normalized URL
    netloc_clean = hostname_ascii.lower()
    if parsed.port and parsed.port not in (80, 443):
        netloc_clean += f":{parsed.port}"

    normalized = f"{parsed.scheme.lower()}://{netloc_clean}{parsed.path or '/'}"
    if parsed.query:
        normalized += f"?{parsed.query}"

    return True, normalized, parsed, ""


# ---------------------------------------------------------------------------
# REGISTRABLE DOMAIN EXTRACTOR (LIGHTWEIGHT HEURISTIC)
# ---------------------------------------------------------------------------

MULTI_PART_TLDS = {
    "co.uk", "org.uk", "gov.uk", "ac.uk", "co.in", "net.in",
    "org.in", "gen.in", "firm.in", "com.au", "net.au", "org.au",
    "co.nz", "com.br", "co.jp", "com.sg", "edu.au"
}


def extract_registrable_domain(hostname):
    """Extract registrable domain from hostname (e.g. login.paypal.com -> paypal.com)."""
    parts = hostname.lower().split(".")
    if len(parts) <= 2:
        return hostname.lower()

    last_two = f"{parts[-2]}.{parts[-1]}"
    if last_two in MULTI_PART_TLDS and len(parts) >= 3:
        return f"{parts[-3]}.{last_two}"

    return f"{parts[-2]}.{parts[-1]}"


# ---------------------------------------------------------------------------
# DETECTION RULES
# ---------------------------------------------------------------------------

def rule_ip_address_host(parsed, raw_url):
    hostname = parsed.hostname or ""
    is_ip = False
    try:
        ipaddress.ip_address(hostname)
        is_ip = True
    except ValueError:
        pass

    if is_ip:
        is_restricted = is_private_or_restricted_ip(hostname)
        explanation = "The URL uses an IP address instead of a legitimate domain name."
        if is_restricted:
            explanation += " Additionally, this points to an internal/private network space."
        return {
            "id": "RULE_IP_HOST",
            "name": "IP Address Host",
            "triggered": True,
            "severity": "high",
            "score_contribution": 30,
            "explanation": explanation
        }
    return {"id": "RULE_IP_HOST", "name": "IP Address Host", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_embedded_credentials(parsed, raw_url):
    has_creds = bool(parsed.username or parsed.password or ("@" in raw_url.split("?")[0]))
    if has_creds:
        return {
            "id": "RULE_EMBEDDED_CREDS",
            "name": "Embedded Credentials / '@' Symbol",
            "triggered": True,
            "severity": "high",
            "score_contribution": 25,
            "explanation": "URL contains an '@' symbol or embedded credentials, which attackers often use to disguise the real destination."
        }
    return {"id": "RULE_EMBEDDED_CREDS", "name": "Embedded Credentials / '@' Symbol", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_brand_impersonation(parsed, raw_url):
    hostname = (parsed.hostname or "").lower()
    reg_domain = extract_registrable_domain(hostname)

    impersonated = []
    for brand, leg_domains in TRUSTED_BRANDS.items():
        # Check if brand appears in hostname or path
        in_host = brand in hostname
        in_path = brand in (parsed.path or "").lower()

        is_legitimate = any(reg_domain == leg or reg_domain.endswith("." + leg) for leg in leg_domains)

        if (in_host or in_path) and not is_legitimate:
            impersonated.append(brand.capitalize())

    if impersonated:
        return {
            "id": "RULE_BRAND_IMPERSONATION",
            "name": "Trusted Brand Impersonation",
            "triggered": True,
            "severity": "high",
            "score_contribution": 30,
            "explanation": f"The URL references reputable brand name(s) ({', '.join(impersonated)}) but is hosted on an unrelated domain ({reg_domain})."
        }
    return {"id": "RULE_BRAND_IMPERSONATION", "name": "Trusted Brand Impersonation", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_punycode_and_homoglyphs(parsed, raw_url):
    hostname = (parsed.hostname or "").lower()
    is_punycode = "xn--" in hostname
    has_non_ascii = any(ord(c) > 127 for c in raw_url)

    if is_punycode or has_non_ascii:
        return {
            "id": "RULE_PUNYCODE_HOMOGLYPH",
            "name": "Punycode & Lookalike Characters",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 20,
            "explanation": "Domain utilizes Punycode ('xn--') or non-ASCII characters, a technique commonly used to craft visually deceptive lookalike domains."
        }
    return {"id": "RULE_PUNYCODE_HOMOGLYPH", "name": "Punycode & Lookalike Characters", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_excessive_subdomains(parsed, raw_url):
    hostname = (parsed.hostname or "").lower()
    labels = [p for p in hostname.split(".") if p]
    if len(labels) >= 5:
        return {
            "id": "RULE_EXCESSIVE_SUBDOMAINS",
            "name": "Excessive Subdomains",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 15,
            "explanation": f"The hostname contains {len(labels)} domain levels. Deep subdomain nesting is frequently used to bury suspicious domains."
        }
    elif len(labels) == 4:
        return {
            "id": "RULE_EXCESSIVE_SUBDOMAINS",
            "name": "Subdomain Nesting",
            "triggered": True,
            "severity": "low",
            "score_contribution": 8,
            "explanation": "The hostname contains 4 domain levels, slightly above standard commercial domains."
        }
    return {"id": "RULE_EXCESSIVE_SUBDOMAINS", "name": "Excessive Subdomains", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_url_shortener(parsed, raw_url):
    hostname = (parsed.hostname or "").lower()
    if hostname in KNOWN_SHORTENERS:
        return {
            "id": "RULE_URL_SHORTENER",
            "name": "URL Shortener Service",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 15,
            "explanation": f"The link uses a known URL shortening service ({hostname}) that obscures the ultimate destination."
        }
    return {"id": "RULE_URL_SHORTENER", "name": "URL Shortener Service", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_excessive_length(parsed, raw_url):
    length = len(raw_url)
    if length > 120:
        return {
            "id": "RULE_URL_LENGTH",
            "name": "Unusually Long URL",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 12,
            "explanation": f"URL length ({length} characters) is unusually long, frequently seen in phishing kits embedding token parameters."
        }
    elif length > 80:
        return {
            "id": "RULE_URL_LENGTH",
            "name": "Moderately Long URL",
            "triggered": True,
            "severity": "low",
            "score_contribution": 6,
            "explanation": f"URL length ({length} characters) is moderately long."
        }
    return {"id": "RULE_URL_LENGTH", "name": "URL Length", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_excessive_hyphens(parsed, raw_url):
    hostname = (parsed.hostname or "").lower()
    hyphen_count = hostname.count("-")
    if hyphen_count >= 3:
        return {
            "id": "RULE_EXCESSIVE_HYPHENS",
            "name": "Excessive Domain Hyphens",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 12,
            "explanation": f"Hostname contains {hyphen_count} hyphens. Attackers frequently use hyphenated strings to mimic brand names."
        }
    return {"id": "RULE_EXCESSIVE_HYPHENS", "name": "Excessive Domain Hyphens", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_suspicious_keywords(parsed, raw_url):
    lower_url = raw_url.lower()
    matched = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lower_url]
    if len(matched) >= 3:
        return {
            "id": "RULE_SUSPICIOUS_KEYWORDS",
            "name": "Suspicious Security Keywords",
            "triggered": True,
            "severity": "high",
            "score_contribution": 20,
            "explanation": f"URL contains multiple urgent or credential-related terms: {', '.join(matched[:5])}."
        }
    elif len(matched) >= 1:
        return {
            "id": "RULE_SUSPICIOUS_KEYWORDS",
            "name": "Suspicious Security Keyword",
            "triggered": True,
            "severity": "low",
            "score_contribution": 8,
            "explanation": f"URL contains a credential/security-related keyword: {', '.join(matched)}."
        }
    return {"id": "RULE_SUSPICIOUS_KEYWORDS", "name": "Suspicious Keywords", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_unusual_port(parsed, raw_url):
    port = parsed.port
    if port and port not in STANDARD_PORTS:
        return {
            "id": "RULE_UNUSUAL_PORT",
            "name": "Non-Standard Port Number",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 15,
            "explanation": f"The URL specifies a non-standard port ({port}) rather than the standard web ports (80 / 443)."
        }
    return {"id": "RULE_UNUSUAL_PORT", "name": "Port Number", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_insecure_http(parsed, raw_url):
    if parsed.scheme.lower() == "http":
        return {
            "id": "RULE_INSECURE_HTTP",
            "name": "Insecure HTTP Protocol",
            "triggered": True,
            "severity": "low",
            "score_contribution": 8,
            "explanation": "Website uses unencrypted HTTP rather than modern HTTPS. (Note: HTTP alone does not prove malicious intent)."
        }
    return {"id": "RULE_INSECURE_HTTP", "name": "Insecure HTTP Protocol", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_high_risk_extension(parsed, raw_url):
    path = (parsed.path or "").lower()
    for ext in HIGH_RISK_EXTENSIONS:
        if path.endswith(ext):
            return {
                "id": "RULE_HIGH_RISK_EXT",
                "name": "High-Risk Executable Extension",
                "triggered": True,
                "severity": "critical",
                "score_contribution": 35,
                "explanation": f"URL links directly to a high-risk executable or script payload ({ext})."
            }
    return {"id": "RULE_HIGH_RISK_EXT", "name": "File Extension", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_suspicious_query_params(parsed, raw_url):
    query = parsed.query
    if not query:
        return {"id": "RULE_SUSPICIOUS_QUERY", "name": "Query Parameters", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}

    qs = parse_qs(query)
    suspicious_params = {"redirect", "next", "url", "target", "dest", "return", "login_url", "cmd", "exec"}
    matched_params = suspicious_params.intersection({k.lower() for k in qs.keys()})

    # Check if a nested URL is in query values
    contains_nested_url = any("http://" in v or "https://" in v for vals in qs.values() for v in vals)

    if contains_nested_url or len(matched_params) >= 2:
        return {
            "id": "RULE_SUSPICIOUS_QUERY",
            "name": "Open Redirect / Nested URL in Query",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 16,
            "explanation": "Query string contains open-redirect indicators or another embedded URL, often leveraged in phishing redirects."
        }
    elif matched_params:
        return {
            "id": "RULE_SUSPICIOUS_QUERY",
            "name": "Redirection Parameter",
            "triggered": True,
            "severity": "low",
            "score_contribution": 6,
            "explanation": f"URL contains a redirection query parameter ({', '.join(matched_params)})."
        }
    return {"id": "RULE_SUSPICIOUS_QUERY", "name": "Query Parameters", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


def rule_obfuscated_encoding(parsed, raw_url):
    # Detect double percent-encoding e.g. %252f or excessive %
    if "%25" in raw_url or raw_url.count("%") >= 5:
        return {
            "id": "RULE_OBFUSCATED_ENCODING",
            "name": "Obfuscated / Multi-layer Encoding",
            "triggered": True,
            "severity": "medium",
            "score_contribution": 15,
            "explanation": "URL contains multiple percent-encoding layers, a common technique to evade perimeter security filters."
        }
    return {"id": "RULE_OBFUSCATED_ENCODING", "name": "Obfuscated Encoding", "triggered": False, "severity": "none", "score_contribution": 0, "explanation": ""}


ALL_RULES = [
    rule_ip_address_host,
    rule_embedded_credentials,
    rule_brand_impersonation,
    rule_punycode_and_homoglyphs,
    rule_excessive_subdomains,
    rule_url_shortener,
    rule_excessive_length,
    rule_excessive_hyphens,
    rule_suspicious_keywords,
    rule_unusual_port,
    rule_insecure_http,
    rule_high_risk_extension,
    rule_suspicious_query_params,
    rule_obfuscated_encoding
]


# ---------------------------------------------------------------------------
# MAIN ANALYSIS ENGINE
# ---------------------------------------------------------------------------

def analyze_phishing_url(raw_url, check_external=False):
    """
    Evaluate URL across multi-factor rule suite and generate transparent score.

    Returns:
    {
        "submitted_url": str,
        "normalized_url": str,
        "risk_score": int (0-100),
        "risk_level": "Low" | "Medium" | "High" | "Critical",
        "risk_classification": str,
        "indicators": list[str],
        "rule_results": list[dict],
        "recommended_action": str,
        "timestamp": str (ISO 8601),
        "external_check_performed": bool,
        "disclaimer": str
    }
    """
    is_valid, normalized_url, parsed, error_msg = validate_and_normalize_url(raw_url)

    now_iso = datetime.now(timezone.utc).isoformat()

    if not is_valid:
        return {
            "submitted_url": raw_url,
            "normalized_url": "",
            "risk_score": 100,
            "risk_level": "Critical",
            "risk_classification": "Invalid / Malformed URL",
            "indicators": [f"Validation failed: {error_msg}"],
            "rule_results": [{
                "id": "RULE_VALIDATION_FAILED",
                "name": "URL Format Validation",
                "triggered": True,
                "severity": "critical",
                "score_contribution": 100,
                "explanation": error_msg
            }],
            "recommended_action": "Do not navigate to or interact with malformed links.",
            "timestamp": now_iso,
            "external_check_performed": False,
            "disclaimer": "This is an explainable heuristic security check, not an absolute guarantee."
        }

    raw_score = 0
    rule_results = []
    indicators = []

    for rule_fn in ALL_RULES:
        result = rule_fn(parsed, raw_url)
        rule_results.append(result)
        if result["triggered"]:
            raw_score += result["score_contribution"]
            indicators.append(result["explanation"])

    # Score bounded between 0 and 100
    risk_score = min(max(raw_score, 0), 100)

    # Classifications
    if risk_score >= 75:
        risk_level = "Critical"
        classification = "Critical Risk - Strongly Suspicious"
        recommended_action = "CRITICAL: Do not open this link or submit any passwords or credentials. Report to IT security."
    elif risk_score >= 50:
        risk_level = "High"
        classification = "High Risk Detected"
        recommended_action = "HIGH RISK: Avoid opening this link. Multiple indicators suggest possible phishing or deception."
    elif risk_score >= 25:
        risk_level = "Medium"
        classification = "Medium Risk Observed"
        recommended_action = "CAUTION: Exercise caution. Verify the sender and destination domain before interacting."
    else:
        risk_level = "Low"
        classification = "Low Observed Risk"
        recommended_action = "No major suspicious indicators detected by heuristic rules. Always remain vigilant with unknown links."

    if not indicators:
        indicators.append("No obvious suspicious patterns detected by heuristic rule engine.")

    return {
        "submitted_url": raw_url,
        "normalized_url": normalized_url,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_classification": classification,
        "indicators": indicators,
        "rule_results": rule_results,
        "recommended_action": recommended_action,
        "timestamp": now_iso,
        "external_check_performed": False,
        "disclaimer": "This analysis provides an explainable heuristic risk assessment and does not guarantee that a URL is safe."
    }


# Backwards compatibility alias
def analyze_url(url):
    res = analyze_phishing_url(url)
    return {
        "url": res["normalized_url"] or url,
        "risk_score": res["risk_score"],
        "risk_level": res["risk_level"],
        "reasons": res["indicators"],
        "disclaimer": res["disclaimer"]
    }
