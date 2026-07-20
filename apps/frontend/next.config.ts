import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Increase proxy timeout for long-running analysis requests (default is 30s)
  experimental: {
    proxyTimeout: 180_000, // 3 minutes
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

export default nextConfig;
