/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config, { dev, isServer }) => {
    // 개발 환경에서 HMR을 더 잘 지원하도록 설정
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000, // 1초마다 변경사항 체크
        aggregateTimeout: 300, // 변경사항이 감지되면 300ms 후에 다시 빌드
      };
    }

    // Monaco Editor 웹팩 설정
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }

    return config;
  },
  // API 라우트를 위한 설정
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  // 폰트 최적화 비활성화
  optimizeFonts: false,
};

module.exports = nextConfig; 