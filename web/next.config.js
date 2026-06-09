/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Long-running agent calls (e.g. the Opus portfolio review) exceed the
    // default 30s proxy timeout for rewrites; allow up to 5 minutes.
    proxyTimeout: 300_000,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
