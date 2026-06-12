const { verifyToken } = require("./jwt"); // Ajustado a la estructura detectada
const crypto = require("crypto");

/**
 * Middleware principal de autenticación
 */
exports.requireAuth = (req, res, next) => {
  const authHeader = req.headers.authorization;

  // Request Tracing: Correlation ID para observabilidad
  req.correlationId = req.headers["x-correlation-id"] || crypto.randomUUID();
  res.setHeader("X-Correlation-ID", req.correlationId);

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res
      .status(401)
      .json({ error: "Acceso denegado. Token no proporcionado." });
  }

  const token = authHeader.split(" ")[1];

  try {
    const decoded = verifyToken(token);
    req.user = decoded; // Inyectamos el payload (id, email, role)
    next();
  } catch (err) {
    return res.status(403).json({
      error: "Token inválido o expirado.",
      audit: {
        traceId: req.correlationId,
        timestamp: new Date().toISOString(),
        code: "INVALID_TOKEN",
      },
    });
  }
};

/**
 * Middleware de autorización por roles (RBAC)
 * @param {Array} allowedRoles - Roles permitidos para este endpoint
 */
exports.requireRole = (allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !req.user.id) {
      return res.status(401).json({ error: "No autenticado." });
    }

    // Normalización de roles a mayúsculas para coincidir con el ENUM de la base de datos
    const userRole = req.user.role?.toUpperCase();
    const rolesPermitidos = allowedRoles.map((r) => r.toUpperCase());

    if (!rolesPermitidos.includes(userRole)) {
      // Log de intento de escalada de privilegios
      console.warn(`[SECURITY ALERT][403] Unauthorized Access Attempt:
                Timestamp: ${new Date().toISOString()}
                User: ${req.user.email} | Required: ${rolesPermitidos} | Actual: ${userRole}
                Path: ${req.method} ${req.originalUrl} | TraceID: ${req.correlationId}
                IP: ${req.ip}`);

      return res.status(403).json({
        error: "Acceso denegado. No tienes los privilegios necesarios.",
      });
    }

    next();
  };
};
