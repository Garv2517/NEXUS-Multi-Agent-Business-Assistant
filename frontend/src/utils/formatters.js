/**
 * Utility formatters for NEXUS Analytics & Business Metrics.
 * Handles integer-cent USD conversions, currency formatting, and numeric displays.
 */

/**
 * Formats integer cents into a USD string.
 * @param {number} cents - Amount in minor currency units (cents).
 * @param {Object} [options]
 * @param {boolean} [options.compact=false] - Whether to use compact notation ($9.86M, $430.6K).
 * @param {number} [options.decimals=2] - Number of decimal digits for standard display.
 * @returns {string} Formatted USD string.
 */
export function formatUSDFromCents(cents, options = {}) {
  if (cents === null || cents === undefined || isNaN(cents)) {
    return '$0.00';
  }

  const dollars = Number(cents) / 100;
  const { compact = false, decimals = 2 } = options;

  if (compact) {
    if (Math.abs(dollars) >= 1_000_000) {
      return `$${(dollars / 1_000_000).toFixed(decimals)}M`;
    }
    if (Math.abs(dollars) >= 1_000) {
      return `$${(dollars / 1_000).toFixed(decimals)}K`;
    }
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(dollars);
}

/**
 * Formats a plain dollar value into a USD string.
 * @param {number} dollars
 * @param {Object} [options]
 * @returns {string}
 */
export function formatUSD(dollars, options = {}) {
  if (dollars === null || dollars === undefined || isNaN(dollars)) {
    return '$0.00';
  }

  const { compact = false, decimals = 2 } = options;

  if (compact) {
    if (Math.abs(dollars) >= 1_000_000) {
      return `$${(dollars / 1_000_000).toFixed(decimals)}M`;
    }
    if (Math.abs(dollars) >= 1_000) {
      return `$${(dollars / 1_000).toFixed(decimals)}K`;
    }
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(dollars);
}

/**
 * Formats integer or float count with comma grouping.
 * @param {number} val
 * @returns {string}
 */
export function formatNumber(val) {
  if (val === null || val === undefined || isNaN(val)) {
    return '0';
  }
  return Number(val).toLocaleString('en-US');
}

/**
 * Formats a percentage number.
 * @param {number} val - e.g. 43.66
 * @param {number} [decimals=2]
 * @returns {string} e.g. "43.66%"
 */
export function formatPercent(val, decimals = 2) {
  if (val === null || val === undefined || isNaN(val)) {
    return '0.00%';
  }
  return `${Number(val).toFixed(decimals)}%`;
}
