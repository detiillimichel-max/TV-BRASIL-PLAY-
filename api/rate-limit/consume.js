const { consume } = require("../_lib/rate-limit");

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const expected = process.env.RATE_LIMIT_ADMIN_TOKEN;
  const supplied = req.headers.authorization || "";
  if (!expected || supplied !== "Bearer " + expected) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const source = req.body && req.body.source;
  if (typeof source !== "string" || !/^[a-z0-9-]{2,60}$/.test(source)) {
    return res.status(400).json({ error: "Invalid source identifier" });
  }

  try {
    const result = await consume(source);
    return res.status(200).json({ ok: true, ...result });
  } catch (error) {
    const status = error.code === "SOURCE_LIMIT_REACHED" ? 429 :
      error.code === "UNKNOWN_SOURCE" ? 404 :
      error.code === "SOURCE_DISABLED" || error.code === "SOURCE_QUOTA_NOT_CONFIGURED" ? 409 : 503;
    return res.status(status).json({
      ok: false,
      code: error.code || "RATE_LIMIT_ERROR",
      message: error.message
    });
  }
};
