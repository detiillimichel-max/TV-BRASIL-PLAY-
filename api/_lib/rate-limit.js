const fs = require("fs");
const path = require("path");

const CONFIG_PATH = path.join(process.cwd(), "config", "api-sources.json");
const WINDOWS = { hour: 3600, day: 86400, month: 2592000 };

function loadConfig() {
  return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
}

function redisConfig() {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) {
    const error = new Error("Shared rate-limit storage is not configured");
    error.code = "RATE_LIMIT_STORAGE_NOT_CONFIGURED";
    throw error;
  }
  return { url: url.replace(/\/$/, ""), token };
}

async function redisCommand(command) {
  const { url, token } = redisConfig();
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(command)
  });
  if (!response.ok) {
    const error = new Error("Shared rate-limit storage request failed");
    error.code = "RATE_LIMIT_STORAGE_ERROR";
    throw error;
  }
  const payload = await response.json();
  if (payload.error) {
    const error = new Error("Shared rate-limit storage returned an error");
    error.code = "RATE_LIMIT_STORAGE_ERROR";
    throw error;
  }
  return payload.result;
}

function getSource(sourceId) {
  const config = loadConfig();
  const source = config.sources.find(item => item.id === sourceId);
  if (!source) {
    const error = new Error("Unknown API source");
    error.code = "UNKNOWN_SOURCE";
    throw error;
  }
  if (source.enabled !== true) {
    const error = new Error("API source is not enabled in the quota registry");
    error.code = "SOURCE_DISABLED";
    throw error;
  }
  return { config, source };
}

async function consume(sourceId, now = Date.now()) {
  const { config, source } = getSource(sourceId);
  const percent = Number(config.policy && config.policy.usagePercent);
  if (!Number.isFinite(percent) || percent <= 0 || percent > 40) {
    const error = new Error("The global usage policy must be between 1 and 40 percent");
    error.code = "INVALID_GLOBAL_POLICY";
    throw error;
  }

  const limits = source.limits || {};
  const applicable = Object.entries(WINDOWS).filter(([window]) => limits[window] !== null && limits[window] !== undefined);
  if (applicable.length === 0) {
    const error = new Error("No provider quota or internal cap has been configured for this source");
    error.code = "SOURCE_QUOTA_NOT_CONFIGURED";
    throw error;
  }

  const checks = [];
  for (const [window, seconds] of applicable) {
    const providerLimit = Number(limits[window]);
    if (!Number.isSafeInteger(providerLimit) || providerLimit < 1) {
      const error = new Error("Invalid configured quota for " + sourceId + " (" + window + ")");
      error.code = "INVALID_SOURCE_QUOTA";
      throw error;
    }
    const allowed = Math.floor(providerLimit * percent / 100);
    if (allowed < 1) {
      const error = new Error("40 percent of this provider quota is below one request");
      error.code = "QUOTA_TOO_SMALL";
      throw error;
    }
    const bucket = Math.floor(now / (seconds * 1000));
    const key = "tvbrasil:ratelimit:v1:" + sourceId + ":" + window + ":" + bucket;
    const count = Number(await redisCommand(["INCR", key]));
    if (count === 1) await redisCommand(["EXPIRE", key, seconds * 2]);
    checks.push({ window, used: count, allowed, remaining: Math.max(0, allowed - count) });
  }

  const exceeded = checks.find(item => item.used > item.allowed);
  if (exceeded) {
    const error = new Error("The 40 percent usage ceiling has been reached for " + sourceId);
    error.code = "SOURCE_LIMIT_REACHED";
    error.details = { source: sourceId, window: exceeded.window, allowed: exceeded.allowed };
    throw error;
  }

  return { source: sourceId, usagePercent: percent, windows: checks };
}

module.exports = { consume, getSource, loadConfig };
