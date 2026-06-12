const jwt = require("jsonwebtoken");

const JWT_ACCESS_SECRET =
  process.env.JWT_ACCESS_SECRET || process.env.JWT_SECRET;
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET;

if (!JWT_ACCESS_SECRET || !JWT_REFRESH_SECRET) {
  console.error(
    "[CRITICAL] JWT Secrets are not fully defined in environment variables",
  );
  process.exit(1);
}

const JWT_EXPIRES_IN = process.env.NODE_ENV === "production" ? "2h" : "8h";
const REFRESH_EXPIRES_IN = "7d";

/**
 * Genera un token con claims de rol y permisos
 */
exports.generateToken = (user) => {
  const payload = {
    id: user.id,
    email: user.email,
    role: user.role,
    permissions: user.permissions || [],
    tenantId: user.tenantId || null,
    correlationId: user.correlationId || null,
    iat: Math.floor(Date.now() / 1000),
  };
  return jwt.sign(payload, JWT_ACCESS_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
    algorithm: "HS256",
  });
};

/**
 * Genera un Refresh Token persistente
 */
exports.generateRefreshToken = (userId) => {
  return jwt.sign({ id: userId }, JWT_REFRESH_SECRET, {
    expiresIn: REFRESH_EXPIRES_IN,
    algorithm: "HS256",
  });
};

exports.verifyToken = (token, isRefresh = false) => {
  if (!token) throw new Error("Token no proporcionado");

  try {
    return jwt.verify(
      token,
      isRefresh ? JWT_REFRESH_SECRET : JWT_ACCESS_SECRET,
      {
        algorithms: ["HS256"],
        ignoreExpiration: false,
      },
    );
  } catch (error) {
    throw error;
  }
};
