"""
Least Recently Used (LRU) Cache implementation
"""

import logging
import time
from collections import OrderedDict
from typing import Any, Dict, Generic, List, Optional, TypeVar

logger = logging.getLogger(__name__)


T = TypeVar("T")


class LRUCache(Generic[T]):
    """LRU 캐시 클래스 - 최대 10개 항목 관리"""

    def __init__(self, max_size: int = 10) -> None:
        """LRU 캐시 초기화"""
        self.max_size = max_size
        self.cache: OrderedDict[str, T] = OrderedDict()
        self.access_times: Dict[str, float] = {}

    def get(self, key: str) -> Optional[T]:
        """캐시에서 값 조회"""
        if key in self.cache:
            # 접근 시간 업데이트
            self.access_times[key] = time.time()
            # OrderedDict에서 맨 뒤로 이동 (최근 사용)
            self.cache.move_to_end(key)
            logger.debug(f"캐시 히트: {key}")
            return self.cache[key]

        logger.debug(f"캐시 미스: {key}")
        return None

    def set(self, key: str, value: T) -> None:
        """캐시에 값 저장"""
        # 캐시가 가득 찬 경우 가장 오래된 항목 제거
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_oldest()

        # 새 항목 추가
        self.cache[key] = value
        self.access_times[key] = time.time()
        logger.debug(f"캐시 저장: {key}")

    def delete(self, key: str) -> bool:
        """캐시에서 항목 삭제"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
            logger.debug(f"캐시 삭제: {key}")
            return True
        return False

    def delete_pattern(self, pattern: str) -> int:
        """패턴에 맞는 키들 삭제"""
        deleted_count = 0
        keys_to_delete = []

        for key in list(self.cache.keys()):
            if pattern in key:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            if self.delete(key):
                deleted_count += 1

        logger.debug(f"패턴 삭제: {pattern}, 삭제된 키: {deleted_count}개")
        return deleted_count

    def delete_multiple(self, keys: List[str]) -> int:
        """여러 키 삭제"""
        deleted_count = 0
        for key in keys:
            if self.delete(key):
                deleted_count += 1
        return deleted_count

    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        self.access_times.clear()
        logger.debug("캐시 전체 삭제")

    def size(self) -> int:
        """캐시 크기 반환"""
        return len(self.cache)

    def keys(self) -> List[str]:
        """캐시 키 목록 반환"""
        return list(self.cache.keys())

    def _evict_oldest(self) -> None:
        """가장 오래된 항목 제거"""
        if not self.cache:
            return

        # 가장 오래된 항목 찾기 (OrderedDict의 첫 번째 항목)
        oldest_key = next(iter(self.cache))
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        logger.debug(f"LRU 제거: {oldest_key}")

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "keys": list(self.cache.keys()),
            "access_times": self.access_times.copy(),
        }
