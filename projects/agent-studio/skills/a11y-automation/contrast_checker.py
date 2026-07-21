#!/usr/bin/env python3
"""
WCAG Contrast Ratio Checker
Checks foreground/background color pairs against WCAG 2.1 contrast requirements.
"""
import re
import math

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb: tuple) -> float:
    """Calculate relative luminance per WCAG 2.1 definition."""
    def channel_luminance(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel_luminance(rgb[0]) + 0.7152 * channel_luminance(rgb[1]) + 0.0722 * channel_luminance(rgb[2])

def contrast_ratio(fg: str, bg: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    l1 = relative_luminance(hex_to_rgb(fg))
    l2 = relative_luminance(hex_to_rgb(bg))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def check_wcag(fg: str, bg: str) -> dict:
    """Check contrast ratio against WCAG standards."""
    ratio = contrast_ratio(fg, bg)
    aa_large = ratio >= 3.0   # AA for large text (18pt+)
    aa_normal = ratio >= 4.5  # AA for normal text
    aaa_large = ratio >= 4.5  # AAA for large text
    aaa_normal = ratio >= 7.0 # AAA for normal text
    return {
        "foreground": fg,
        "background": bg,
        "ratio": round(ratio, 2),
        "wcag_aa_large": aa_large,
        "wcag_aa_normal": aa_normal,
        "wcag_aaa_large": aaa_large,
        "wcag_aaa_normal": aaa_normal,
        "passes_aa": aa_normal,
        "passes_aaa": aaa_normal,
    }

def scan_css_for_contrast(css_content: str) -> list:
    """Scan CSS content for color pairs and check contrast."""
    hex_pattern = re.compile(r"#[0-9a-fA-F]{3,6}")
    results = []
    # Very basic: look for color and background-color in same rule
    rules = re.findall(r"\{[^}]*\}", css_content)
    for rule in rules:
        colors = hex_pattern.findall(rule)
        if len(colors) >= 2:
            result = check_wcag(colors[0], colors[1])
            if not result["passes_aa"]:
                results.append({"rule": rule.strip(), **result})
    return results

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) >= 2:
        result = check_wcag(args[0], args[1])
        print(f"Contrast ratio: {result['ratio']}:1")
        print(f"WCAG AA (normal text): {'✅ PASS' if result['wcag_aa_normal'] else '❌ FAIL'}")
        print(f"WCAG AAA (normal text): {'✅ PASS' if result['wcag_aaa_normal'] else '❌ FAIL'}")
    else:
        print("Usage: contrast_checker.py #ffffff #000000")
