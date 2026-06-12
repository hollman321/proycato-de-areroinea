(async () => {
  try {
    const res = await fetch("http://backend:8000/debug/echo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "a@b.com", password: "p" }),
    });
    const t = await res.text();
    console.log(t);
  } catch (e) {
    console.error(e);
  }
})();
