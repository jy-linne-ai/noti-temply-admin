from typing import Generic, Optional, TypeVar

from temply_app.core.config import Config
from temply_app.core.lru_cache import LRUCache
from temply_app.core.temply.parser.layout_parser import LayoutParser
from temply_app.core.temply.parser.partial_parser import PartialParser
from temply_app.core.temply.parser.template_parser import TemplateParser
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.core.temply_version_env import TemplyVersionEnv
from temply_app.models.common_model import VersionInfo

T = TypeVar("T")


class CacheUtil(Generic[T]):
    """Cache Util"""

    def __init__(self, max_size: int = 10) -> None:
        self._cache: LRUCache[T] = LRUCache(max_size)

    def get(self, temply_env: TemplyEnv) -> Optional[T]:
        """Get Cache"""
        cache_key = str(temply_env)
        return self._cache.get(cache_key)

    def set(self, temply_env: TemplyEnv, value: T) -> None:
        """Set Cache"""
        cache_key = str(temply_env)
        self._cache.set(cache_key, value)

    def clear(self) -> None:
        """Clear Cache"""
        self._cache.clear()

    def delete(self, temply_env: TemplyEnv) -> None:
        """Delete Cache"""
        self._cache.delete(str(temply_env))


_layout_cache_util: Optional[CacheUtil[LayoutParser]] = None


def _get_layout_cache_util() -> CacheUtil[LayoutParser]:
    """Get Layout Cache Util"""
    global _layout_cache_util  # pylint: disable=global-statement
    if _layout_cache_util is None:
        _layout_cache_util = CacheUtil[LayoutParser]()
    return _layout_cache_util


def get_layout_parser(temply_env: TemplyEnv) -> LayoutParser:
    """Get Layout Parser"""
    layout_cache_util = _get_layout_cache_util()
    layout_parser = layout_cache_util.get(temply_env)
    if layout_parser is None:
        layout_parser = LayoutParser(temply_env)
        layout_cache_util.set(temply_env, layout_parser)
    return layout_parser


_partial_cache_util: Optional[CacheUtil[PartialParser]] = None


def _get_partial_cache_util() -> CacheUtil[PartialParser]:
    """Get Partial Cache Util"""
    global _partial_cache_util  # pylint: disable=global-statement
    if _partial_cache_util is None:
        _partial_cache_util = CacheUtil[PartialParser]()
    return _partial_cache_util


def get_partial_parser(temply_env: TemplyEnv) -> PartialParser:
    """Get Partial Parser"""
    partial_cache_util = _get_partial_cache_util()
    partial_parser = partial_cache_util.get(temply_env)
    if partial_parser is None:
        partial_parser = PartialParser(temply_env)
        partial_cache_util.set(temply_env, partial_parser)
    return partial_parser


_template_cache_util: Optional[CacheUtil[TemplateParser]] = None


def _get_template_cache_util() -> CacheUtil[TemplateParser]:
    """Get Template Cache Util"""
    global _template_cache_util  # pylint: disable=global-statement
    if _template_cache_util is None:
        _template_cache_util = CacheUtil[TemplateParser]()
    return _template_cache_util


def get_template_parser(temply_env: TemplyEnv) -> TemplateParser:
    """Get Template Parser"""
    template_cache_util = _get_template_cache_util()
    template_parser = template_cache_util.get(temply_env)
    if template_parser is None:
        template_parser = TemplateParser(temply_env)
        template_cache_util.set(temply_env, template_parser)
    return template_parser


class TemplyVersionEnvCacheUtil:
    """Temply Version Env Cache Util"""

    def __init__(self, max_size: int = 10) -> None:
        self._cache: LRUCache[TemplyVersionEnv] = LRUCache(max_size)

    def get(self, version_info: VersionInfo) -> Optional[TemplyVersionEnv]:
        """Get Cache"""
        return self._cache.get(version_info.get_cache_key())

    def set(self, version_info: VersionInfo, value: TemplyVersionEnv) -> None:
        """Set Cache"""
        self._cache.set(version_info.get_cache_key(), value)

    def clear(self) -> None:
        """Clear Cache"""
        self._cache.clear()

    def delete(self, version_info: VersionInfo) -> None:
        """Delete Cache"""
        self._cache.delete(version_info.get_cache_key())


_temply_version_env_cache_util: Optional[TemplyVersionEnvCacheUtil] = None


def _get_temply_version_env_cache_util() -> TemplyVersionEnvCacheUtil:
    """Get Temply Version Env Cache Util"""
    global _temply_version_env_cache_util  # pylint: disable=global-statement
    if _temply_version_env_cache_util is None:
        _temply_version_env_cache_util = TemplyVersionEnvCacheUtil()
    return _temply_version_env_cache_util


def get_temply_version_env(config: Config, version_info: VersionInfo) -> TemplyVersionEnv:
    """Get Temply Version Env"""
    temply_version_env_cache_util = _get_temply_version_env_cache_util()
    temply_version_env = temply_version_env_cache_util.get(version_info)
    if temply_version_env is None:
        temply_version_env = TemplyVersionEnv(config, version_info)
        temply_version_env_cache_util.set(version_info, temply_version_env)
    return temply_version_env


def temply_version_env_cache_clear(version_info: VersionInfo) -> None:
    """Temply Version Env Cache Clear"""
    temply_version_env_cache_util = _get_temply_version_env_cache_util()
    temply_version_env_cache_util.delete(version_info)
