import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Workaround for Oracle client native module loading in Next.js
  // This tells Next.js to treat 'oracledb' as an external package,
  // preventing bundling and preserving native module behavior
  serverExternalPackages: ["oracledb"],
};

export default nextConfig;
