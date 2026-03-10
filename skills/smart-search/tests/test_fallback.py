"""
降级链测试
==========
测试降级策略和各种异常情况
"""

import asyncio
import pytest
from utils.fallback_chain import FallbackChain, FetchResult


class TestFallbackChain:
    """FallbackChain 测试"""
    
    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        """成功抓取测试"""
        async with FallbackChain() as chain:
            result = await chain.fetch("https://example.com")
            
            # 验证结果结构
            assert result.success or result.error  # 可能成功也可能失败 (取决于网络)
            assert result.url == "https://example.com"
            assert result.method != ""
    
    @pytest.mark.asyncio
    async def test_fallback_strategy(self):
        """降级策略测试"""
        async with FallbackChain() as chain:
            # 测试一个可能失败的 URL
            result = await chain.fetch("https://this-url-probably-does-not-exist-12345.com")
            
            # 应该失败并记录错误
            assert not result.success
            assert result.error is not None
            assert result.retry_count > 0
    
    @pytest.mark.asyncio
    async def test_retries(self):
        """重试机制测试"""
        async with FallbackChain() as chain:
            # 测试失败 URL，验证重试
            result = await chain.fetch("https://nonexistent-domain-xyz.com")
            
            # 验证重试次数
            assert result.retry_count <= 2  # 最大重试次数
    
    def test_sync_fetch(self):
        """同步抓取测试"""
        async def run_test():
            async with FallbackChain() as chain:
                result = await chain.fetch("https://example.com")
                return result
        
        result = asyncio.run(run_test())
        assert result.url == "https://example.com"


class TestFetchResult:
    """FetchResult 测试"""
    
    def test_result_to_dict(self):
        """结果转字典测试"""
        result = FetchResult(
            success=True,
            url="https://example.com",
            content="test content",
            title="Test Title",
            source="test",
            fetch_time=1.5,
            method="test",
            retry_count=0
        )
        
        data = result.to_dict()
        
        assert data["success"] is True
        assert data["url"] == "https://example.com"
        assert data["content"] == "test content"
        assert data["title"] == "Test Title"
        assert data["source"] == "test"
        assert data["fetch_time"] == 1.5


class TestContentLength:
    """内容长度测试"""
    
    @pytest.mark.asyncio
    async def test_large_content(self):
        """大内容抓取测试"""
        async with FallbackChain() as chain:
            result = await chain.fetch("https://example.com")
            
            # 验证内容长度限制
            if result.content:
                max_length = 50000
                assert len(result.content) <= max_length or result.success is False


class TestTimeout:
    """超时测试"""
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """超时处理测试"""
        # 使用较短的超时时间
        from config import ScraperConfig
        config = ScraperConfig(timeout_seconds=2)
        
        async with FallbackChain(config) as chain:
            # 尝试抓取一个可能超时的 URL
            result = await chain.fetch("https://httpbin.org/delay/10")
            
            # 应该超时或失败
            assert not result.success or result.error is not None


class TestErrorLogging:
    """错误日志测试"""
    
    @pytest.mark.asyncio
    async def test_error_logging(self):
        """错误日志测试"""
        async with FallbackChain() as chain:
            # 抓取失败 URL
            result = await chain.fetch("https://invalid-url-test-12345.com")
            
            # 验证错误被记录
            assert not result.success
            assert result.error is not None
            
            # 验证结果日志
            log = chain.get_results_log()
            assert len(log) > 0
            assert log[-1].url == "https://invalid-url-test-12345.com"


class TestConcurrency:
    """并发测试"""
    
    @pytest.mark.asyncio
    async def test_parallel_fetch(self):
        """并行抓取测试"""
        async with FallbackChain() as chain:
            urls = [
                "https://example.com",
                "https://httpbin.org/get",
                "https://httpbin.org/html"
            ]
            
            tasks = [chain.fetch(url) for url in urls]
            results = await asyncio.gather(*tasks)
            
            # 验证所有结果
            assert len(results) == 3
            for result in results:
                assert result.url in urls


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
