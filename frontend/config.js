// Direct connection to Render backend prevents Vercel's 10s proxy timeout
// when the Render free tier needs time to wake up from a cold start.
const isRender = window.location.hostname.endsWith(".onrender.com");
const isLocalFlask = ["localhost", "127.0.0.1"].includes(window.location.hostname)
    && window.location.port === "5000";

const API_BASE_URL = (isRender || isLocalFlask)
    ? window.location.origin
    : "https://stockss-backend-1.onrender.com";
