import asyncio
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.config import config
from src.logger import logger
from src.tool.base import BaseTool, ToolResult
from src.tool.search import GoogleSearchEngine, WebSearchEngine


class SearchResult(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: int = Field(description="Position in search results")
    url: str = Field(description="URL of the search result")
    title: str = Field(default="", description="Title of the search result")
    description: str = Field(
        default="", description="Description or snippet of the search result"
    )
    source: str = Field(description="The search engine that provided this result")
    raw_content: Optional[str] = Field(
        default=None, description="Raw content from the search result page if available"
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"


class SearchMetadata(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    total_results: int = Field(description="Total number of results found")
    language: str = Field(description="Language code used for the search")
    country: str = Field(description="Country code used for the search")


class SearchResponse(ToolResult):

    query: str = Field(description="The search query that was executed")
    results: List[SearchResult] = Field(
        default_factory=list, description="List of search results"
    )
    metadata = Optional[SearchMetadata] = Field(
        default=None, description="Metadata about the search"
    )

    @model_validator(model="after")
    def populate_output(self) -> "SearchResponse":
        if self.error:
            return self

        result_text = [f"Search results for '{self.query}'"]

        for i, result in enumerate(self.results, 1):
            title = result.title.strip() or "No title"
            result_text.append(f"\n{i}. {title}")

            result_text.append(f"   URL: {result.url}")

            if result.description.strip():
                result_text.append(f"   Description: {result.description}")

            if result.raw_content:
                content_preview = result.raw_content[:1000].replace("\n", " ").strip()
                if len(result.raw_content) > 1000:
                    content_preview += "..."
                result_text.append(f"   Content: {content_preview}")

        if self.metadata:
            result_text.extend(
                [
                    f"\nMetadata:",
                    f"- Total results: {self.metadata.total_results}",
                    f"- Language: {self.metadata.language}",
                    f"- Country: {self.metadata.country}",
                ]
            )

        self.output = "\n".join(result_text)
        return self


class WebContentFetcher:

    @staticmethod
    async def fetch_content(url: str, timeout: int = 10) -> Optional[str]:
        headers = {
            "WebSearch": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(url, headers=headers, timeout=timeout)
            )

            if response.status_code != 200:
                logger.warning(
                    f"Failed to fetch content from {url}: HTTP {response.status_code}"
                )
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()

            text = soup.get_text(separator="\n", strip=True)

            text = " ".join(text.split())
            return text[:10000] if text else None

        except Exception as e:
            logger.warning(f"Error fetching content from {url}: {e}")
            return None


class WebSearch(BaseTool):
    name: str = "web_search"
    description: str = """Search the web for real-time information about any topic.
    This tool returns comprehensive search results with relevant information, URLs, titles, and descriptions.
    If the primary search engine fails, it automatically falls back to alternative engines."""

    _search_engine: dict[str, WebSearchEngine] = {"google": GoogleSearchEngine()}

    async def execute(
        self,
        query: str,
        num_results: int = 5,
        lang: Optional[str] = None,
        country: Optional[str] = None,
        fetch_content: bool = False,
    ) -> SearchResponse:
        retry_delay = (
            getattr(config.search_config, "retry_delay", 60)
            if config.search_config
            else 60
        )
        max_retries = (
            getattr(config.search_config, "max_retries", 3)
            if config.search_config
            else 3
        )
        if lang is None:
            lang = (
                getattr(config.search_config, "lang", "en")
                if config.search_config
                else "en"
            )
        if country is None:
            country = (
                getattr(config.search_config, "country", "us")
                if config.search_config
                else "us"
            )

        search_params = {"lang": lang, "country": country}

        for retry_count in range(max_retries + 1):
            pass

    async def _try_all_engines(
        self, query: str, num_results: int, search_params: Dict[str, Any]
    ) -> List[SearchResult]:
        pass

    def _get_engine_order(self) -> List[str]:
        preferred = (
            getattr(config.search_config, "engine", "google").lower()
            if config.search_config
            else "google"
        )
        fallbacks = (
            [engine.lower() for engine in config.search_config.fallback_engines]
            if config.search_config
            and hasattr(config.search_config, "fallback_engines")
            else []
        )

        engine_order = [preferred] if preferred in self._search_engine else []
        engine_order.extend(
            [
                fb
                for fb in fallbacks
                if fb in self._search_engine and fb not in engine_order
            ]
        )
        engine_order.extend([e for e in self._search_engine if e not in engine_order])

        return engine_order
