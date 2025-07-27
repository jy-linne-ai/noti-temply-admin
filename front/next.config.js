/** @type {import('next').NextConfig} */
const nextConfig = {
  // 빌드 최적화
  output: 'standalone',
  
  // 실험적 기능
  experimental: {
    // 출력 추적 활성화 (Docker 최적화)
    outputFileTracingRoot: undefined,
  },
  
  // 이미지 최적화
  images: {
    // 외부 이미지 도메인 허용
    domains: ['localhost'],
    // 이미지 최적화 비활성화 (개발 환경에서)
    unoptimized: process.env.NODE_ENV === 'development',
  },
  
  // 웹팩 최적화
  webpack: (config, { dev, isServer }) => {
    // 개발 환경에서 캐시 활성화
    if (dev) {
      config.cache = {
        type: 'filesystem',
        buildDependencies: {
          config: [__filename],
        },
      };
    }
    
    // 번들 크기 최적화
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      },
    };
    
    return config;
  },
  
  // 컴파일러 최적화
  compiler: {
    // 불필요한 console.log 제거 (프로덕션)
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // 타입스크립트 최적화
  typescript: {
    // 빌드 시 타입 체크 건너뛰기 (개발 환경에서)
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  
  // ESLint 최적화
  eslint: {
    // 빌드 시 ESLint 건너뛰기 (개발 환경에서)
    ignoreDuringBuilds: process.env.NODE_ENV === 'development',
  },
  
  // 환경 변수
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // 헤더 설정
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig; 