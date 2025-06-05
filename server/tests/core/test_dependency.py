import threading

import pytest

from temply_app.core.dependency import get_config


def test_config_singleton():
    """Config가 싱글톤으로 동작하는지 테스트"""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2


def test_config_thread_safety():
    """Config가 스레드 안전하게 동작하는지 테스트"""
    configs = []
    threads = []

    def get_config_thread():
        config = get_config()
        configs.append(config)

    # 여러 스레드에서 동시에 get_config 호출
    for _ in range(10):
        thread = threading.Thread(target=get_config_thread)
        threads.append(thread)
        thread.start()

    # 모든 스레드가 완료될 때까지 대기
    for thread in threads:
        thread.join()

    # 모든 스레드가 동일한 Config 인스턴스를 받았는지 확인
    first_config = configs[0]
    assert all(config is first_config for config in configs)
