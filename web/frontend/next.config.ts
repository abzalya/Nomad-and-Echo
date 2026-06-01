import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Lets the browser use same-origin relative "/api" paths everywhere.
  //   dev:  forwards /api/* to the gateway over the chessnet docker network
  //         (frontend joins chessnet in docker-compose.override.yml).
  //   prod: Traefik routes <domain>/api/* to the gateway at the edge, so /api
  //         never reaches Next and this rewrite is simply never exercised.
  // The destination is the internal docker service name, identical in every
  // environment, so nothing environment-specific is baked into the image.
  // NOTE: rewrites() runs at *build* time, so the destination must be a
  // constant string, not a runtime env var.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: "http://gateway:8000/api/:path*" },
    ];
  },
};

export default nextConfig;
