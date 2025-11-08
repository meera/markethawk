import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config, { isServer }) => {
    // Fix for drizzle-orm module resolution issue with Better Auth
    if (isServer) {
      config.externals = config.externals || [];
      config.externals.push({
        'drizzle-orm': 'commonjs drizzle-orm',
      });
    }
    return config;
  },
};

export default nextConfig;
