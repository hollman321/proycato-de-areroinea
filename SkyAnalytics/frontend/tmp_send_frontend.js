(async () => {
  try {
    const res = await fetch("http://localhost:3000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "admin@skyanalytics.com",
        password: "admin123",
      }),
    });
    const t = await res.text();
    console.log("status", res.status);
    console.log(t);
  } catch (e) {
    console.error(e);
  }
})();
