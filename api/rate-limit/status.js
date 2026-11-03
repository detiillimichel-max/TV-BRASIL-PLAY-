const { loadConfig } = require("../_lib/rate-limit");

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const config = loadConfig();
    const redisReady = Boolean(process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN);
    const tokenReady = Boolean(process.env.RATE_LIMIT_ADMIN_TOKEN);
    const sources = config.sources.map(source => ({
      id: source.id,
      name: source.name,
      enabled: source.enabled === true,
      quotaConfigured: Object.values(source.limits || {}).some(value => Number.isSafeInteger(value) && value > 0),
      windowsConfigured: Object.entries(source.limits || {})
        .filter(([, value]) => Number.isSafeInteger(value) && value > 0)
        .map(([window]) => window)
    }));
    return res.status(200).json({
      service: "TV-BRASIL-PLAY central API rate limiter",
      usagePercent: config.policy.usagePercent,
      failClosed: config.policy.failClosed,
      storage: redisReady ? "configured" : "missing",
      collectorAuth: tokenReady ? "configured" : "missing",
      ready: redisReady && tokenReady,
      sources
    });
  } catch (error) {
    return res.status(500).json({ error: "Unable to read rate-limit configuration" });
  }
};
