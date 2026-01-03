"""
AI Factory - Database Layer com Connection Pooling e Caching
============================================================
Módulo otimizado para acesso ao banco de dados com:
- Connection pooling async via asyncpg
- Cache em memória com TTL
- Suporte a soft delete
- Fallback para Supabase SDK
"""

import os
import asyncio
import logging
import hashlib
import json
from typing import Optional, Dict, Any, List, TypeVar, Callable
from datetime import datetime, timedelta
from functools import wraps
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Type para generics
T = TypeVar('T')


# ============================================
# CACHE LAYER
# ============================================

@dataclass
class CacheEntry:
    """Entrada de cache com TTL."""
    value: Any
    expires_at: datetime
    hits: int = 0


class InMemoryCache:
    """
    Cache em memória com TTL e estatísticas.

    Features:
    - TTL configurável por chave
    - Limpeza automática de entradas expiradas
    - Estatísticas de hit/miss
    - Namespace para isolamento
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
        self._lock = asyncio.Lock()

    def _generate_key(self, namespace: str, key: str) -> str:
        """Gera chave única com namespace."""
        return f"{namespace}:{key}"

    def _hash_params(self, params: Dict) -> str:
        """Gera hash de parâmetros para cache key."""
        serialized = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode()).hexdigest()[:12]

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Busca valor do cache."""
        full_key = self._generate_key(namespace, key)

        async with self._lock:
            entry = self._cache.get(full_key)

            if entry is None:
                self._stats["misses"] += 1
                return None

            if datetime.utcnow() > entry.expires_at:
                del self._cache[full_key]
                self._stats["misses"] += 1
                return None

            entry.hits += 1
            self._stats["hits"] += 1
            return entry.value

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Define valor no cache."""
        full_key = self._generate_key(namespace, key)
        ttl = ttl or self._default_ttl

        async with self._lock:
            # Evict se exceder tamanho máximo
            if len(self._cache) >= self._max_size:
                await self._evict_oldest()

            self._cache[full_key] = CacheEntry(
                value=value,
                expires_at=datetime.utcnow() + timedelta(seconds=ttl)
            )

    async def delete(self, namespace: str, key: str) -> bool:
        """Remove entrada do cache."""
        full_key = self._generate_key(namespace, key)

        async with self._lock:
            if full_key in self._cache:
                del self._cache[full_key]
                return True
            return False

    async def invalidate_namespace(self, namespace: str) -> int:
        """Invalida todas as entradas de um namespace."""
        count = 0
        prefix = f"{namespace}:"

        async with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
                count += 1

        logger.info(f"Invalidated {count} cache entries for namespace '{namespace}'")
        return count

    async def _evict_oldest(self) -> None:
        """Remove entradas mais antigas."""
        if not self._cache:
            return

        # Remove 10% das entradas mais antigas
        entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].expires_at
        )

        to_remove = max(1, len(entries) // 10)
        for key, _ in entries[:to_remove]:
            del self._cache[key]
            self._stats["evictions"] += 1

    async def cleanup_expired(self) -> int:
        """Remove entradas expiradas."""
        count = 0
        now = datetime.utcnow()

        async with self._lock:
            keys_to_delete = [
                k for k, v in self._cache.items()
                if now > v.expires_at
            ]
            for key in keys_to_delete:
                del self._cache[key]
                count += 1

        return count

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0

        return {
            **self._stats,
            "size": len(self._cache),
            "max_size": self._max_size,
            "hit_rate_percent": round(hit_rate, 2)
        }


def cached(
    namespace: str,
    ttl: int = 300,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator para cache automático de métodos.

    Usage:
        @cached(namespace="agents", ttl=60)
        async def get_agent(self, agent_id: str) -> Dict:
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Verifica se cache está disponível
            cache = getattr(self, '_cache', None)
            if not cache:
                return await func(self, *args, **kwargs)

            # Gera cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                params = {**dict(enumerate(args)), **kwargs}
                cache_key = cache._hash_params(params)

            # Tenta buscar do cache
            cached_value = await cache.get(namespace, cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {namespace}:{cache_key}")
                return cached_value

            # Executa função e cacheia resultado
            result = await func(self, *args, **kwargs)

            if result is not None:
                await cache.set(namespace, cache_key, result, ttl)
                logger.debug(f"Cache SET: {namespace}:{cache_key}")

            return result

        return wrapper
    return decorator


# ============================================
# CONNECTION POOL
# ============================================

class ConnectionPool:
    """
    Pool de conexões PostgreSQL async.

    Usa asyncpg para conexões diretas quando disponível,
    com fallback para Supabase SDK.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        min_connections: int = 2,
        max_connections: int = 10,
        connection_timeout: float = 10.0
    ):
        self._database_url = database_url or os.getenv("DATABASE_URL")
        self._min_connections = min_connections
        self._max_connections = max_connections
        self._connection_timeout = connection_timeout
        self._pool = None
        self._initialized = False
        self._use_asyncpg = False

    async def initialize(self) -> bool:
        """Inicializa pool de conexões."""
        if self._initialized:
            return True

        if not self._database_url:
            logger.warning("DATABASE_URL not set, using Supabase SDK only")
            self._initialized = True
            return True

        try:
            import asyncpg

            self._pool = await asyncpg.create_pool(
                dsn=self._database_url,
                min_size=self._min_connections,
                max_size=self._max_connections,
                command_timeout=self._connection_timeout,
                statement_cache_size=100
            )

            self._use_asyncpg = True
            self._initialized = True

            logger.info(
                f"Connection pool initialized: "
                f"min={self._min_connections}, max={self._max_connections}"
            )
            return True

        except ImportError:
            logger.warning("asyncpg not installed, using Supabase SDK only")
            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            self._initialized = True
            return False

    async def close(self) -> None:
        """Fecha pool de conexões."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("Connection pool closed")

    @asynccontextmanager
    async def acquire(self):
        """
        Adquire conexão do pool.

        Usage:
            async with pool.acquire() as conn:
                result = await conn.fetch("SELECT * FROM agents")
        """
        if not self._initialized:
            await self.initialize()

        if not self._use_asyncpg or not self._pool:
            yield None
            return

        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            await self._pool.release(conn)

    async def execute(self, query: str, *args) -> str:
        """Executa query sem retorno."""
        async with self.acquire() as conn:
            if conn:
                return await conn.execute(query, *args)
            raise RuntimeError("No database connection available")

    async def fetch(self, query: str, *args) -> List[Dict]:
        """Executa query e retorna resultados como lista de dicts."""
        async with self.acquire() as conn:
            if conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
            raise RuntimeError("No database connection available")

    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Executa query e retorna primeira linha como dict."""
        async with self.acquire() as conn:
            if conn:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
            raise RuntimeError("No database connection available")

    async def fetchval(self, query: str, *args) -> Any:
        """Executa query e retorna valor único."""
        async with self.acquire() as conn:
            if conn:
                return await conn.fetchval(query, *args)
            raise RuntimeError("No database connection available")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do pool."""
        if not self._pool:
            return {"status": "not_initialized", "using_asyncpg": False}

        return {
            "status": "active",
            "using_asyncpg": self._use_asyncpg,
            "size": self._pool.get_size(),
            "min_size": self._pool.get_min_size(),
            "max_size": self._pool.get_max_size(),
            "free_size": self._pool.get_idle_size()
        }


# ============================================
# SOFT DELETE MIXIN
# ============================================

class SoftDeleteMixin:
    """
    Mixin para operações de soft delete.

    Requer coluna 'deleted_at TIMESTAMPTZ' na tabela.
    """

    @staticmethod
    def soft_delete_filter(include_deleted: bool = False) -> str:
        """Retorna filtro SQL para soft delete."""
        if include_deleted:
            return ""
        return "AND deleted_at IS NULL"

    @staticmethod
    def soft_delete_columns() -> str:
        """Retorna colunas SQL para soft delete."""
        return ", deleted_at, deleted_by"

    async def soft_delete(
        self,
        pool: ConnectionPool,
        table: str,
        record_id: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Marca registro como deletado (soft delete).

        Args:
            pool: Connection pool
            table: Nome da tabela
            record_id: ID do registro
            deleted_by: ID do usuário que deletou (opcional)

        Returns:
            True se deletou, False se não encontrou
        """
        query = f"""
            UPDATE {table}
            SET
                deleted_at = NOW(),
                deleted_by = $2
            WHERE id = $1 AND deleted_at IS NULL
            RETURNING id
        """

        result = await pool.fetchval(query, record_id, deleted_by)
        return result is not None

    async def restore(
        self,
        pool: ConnectionPool,
        table: str,
        record_id: str
    ) -> bool:
        """
        Restaura registro deletado.

        Args:
            pool: Connection pool
            table: Nome da tabela
            record_id: ID do registro

        Returns:
            True se restaurou, False se não encontrou
        """
        query = f"""
            UPDATE {table}
            SET
                deleted_at = NULL,
                deleted_by = NULL
            WHERE id = $1 AND deleted_at IS NOT NULL
            RETURNING id
        """

        result = await pool.fetchval(query, record_id)
        return result is not None

    async def hard_delete(
        self,
        pool: ConnectionPool,
        table: str,
        record_id: str
    ) -> bool:
        """
        Remove registro permanentemente.

        Args:
            pool: Connection pool
            table: Nome da tabela
            record_id: ID do registro

        Returns:
            True se deletou, False se não encontrou
        """
        query = f"""
            DELETE FROM {table}
            WHERE id = $1
            RETURNING id
        """

        result = await pool.fetchval(query, record_id)
        return result is not None


# ============================================
# DATABASE MANAGER
# ============================================

class DatabaseManager(SoftDeleteMixin):
    """
    Gerenciador central de acesso ao banco de dados.

    Features:
    - Connection pooling
    - In-memory caching
    - Soft delete
    - Estatísticas
    - Healthcheck
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        cache_ttl: int = 300,
        cache_max_size: int = 1000,
        pool_min: int = 2,
        pool_max: int = 10
    ):
        self.pool = ConnectionPool(
            database_url=database_url,
            min_connections=pool_min,
            max_connections=pool_max
        )
        self._cache = InMemoryCache(
            default_ttl=cache_ttl,
            max_size=cache_max_size
        )
        self._supabase_client = None
        self._initialized = False

    async def initialize(self) -> None:
        """Inicializa database manager."""
        if self._initialized:
            return

        # Inicializa pool
        await self.pool.initialize()

        # Inicializa Supabase client como fallback
        try:
            from src.supabase_client import SupabaseClient
            self._supabase_client = SupabaseClient()
        except Exception as e:
            logger.warning(f"Supabase client not available: {e}")

        self._initialized = True
        logger.info("DatabaseManager initialized")

    async def close(self) -> None:
        """Fecha conexões."""
        await self.pool.close()
        self._initialized = False

    async def healthcheck(self) -> Dict[str, Any]:
        """Verifica saúde do banco de dados."""
        result = {
            "status": "unknown",
            "pool": self.pool.get_stats(),
            "cache": self._cache.get_stats(),
            "latency_ms": None
        }

        try:
            start = datetime.utcnow()

            if self.pool._use_asyncpg:
                await self.pool.fetchval("SELECT 1")
            elif self._supabase_client:
                self._supabase_client.ping()
            else:
                result["status"] = "no_connection"
                return result

            latency = (datetime.utcnow() - start).total_seconds() * 1000
            result["latency_ms"] = round(latency, 2)
            result["status"] = "healthy"

        except Exception as e:
            result["status"] = "unhealthy"
            result["error"] = str(e)

        return result

    # ============================================
    # QUERY HELPERS
    # ============================================

    @cached(namespace="agents", ttl=60)
    async def get_agent_version(self, agent_id: str) -> Optional[Dict]:
        """Busca agent_version por ID (cacheado)."""
        if self.pool._use_asyncpg:
            return await self.pool.fetchrow(
                """
                SELECT av.*, c.name as client_name, sa.name as sub_account_name
                FROM agent_versions av
                LEFT JOIN clients c ON c.id = av.client_id
                LEFT JOIN sub_accounts sa ON sa.id = av.sub_account_id
                WHERE av.id = $1 AND av.deleted_at IS NULL
                """,
                agent_id
            )
        elif self._supabase_client:
            return self._supabase_client.get_agent_version(agent_id)

        return None

    @cached(namespace="agents_needing_test", ttl=30)
    async def get_agents_needing_testing(self, limit: int = 100) -> List[Dict]:
        """Busca agentes que precisam ser testados (cacheado)."""
        if self.pool._use_asyncpg:
            return await self.pool.fetch(
                """
                SELECT * FROM vw_agents_needing_testing
                ORDER BY priority, created_at DESC
                LIMIT $1
                """,
                limit
            )
        elif self._supabase_client:
            return self._supabase_client.get_agents_needing_testing(limit)

        return []

    async def save_test_result(
        self,
        agent_version_id: str,
        overall_score: float,
        test_details: Dict,
        report_url: str,
        test_duration_ms: int,
        evaluator_model: str = "claude-opus-4"
    ) -> str:
        """Salva resultado de teste (invalida cache)."""
        result_id = None

        if self.pool._use_asyncpg:
            result_id = await self.pool.fetchval(
                """
                INSERT INTO agenttest_test_results
                    (agent_version_id, overall_score, test_details,
                     report_url, test_duration_ms, evaluator_model)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                agent_version_id,
                overall_score,
                json.dumps(test_details),
                report_url,
                test_duration_ms,
                evaluator_model
            )
        elif self._supabase_client:
            result_id = self._supabase_client.save_test_result(
                agent_version_id=agent_version_id,
                overall_score=overall_score,
                test_details=test_details,
                report_url=report_url,
                test_duration_ms=test_duration_ms,
                evaluator_model=evaluator_model
            )

        # Invalida caches relacionados
        await self._cache.invalidate_namespace("agents")
        await self._cache.invalidate_namespace("test_results")
        await self._cache.invalidate_namespace("agents_needing_test")

        return str(result_id) if result_id else ""

    @cached(namespace="test_results", ttl=120)
    async def get_test_results_history(
        self,
        agent_version_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Busca histórico de testes (cacheado)."""
        if self.pool._use_asyncpg:
            return await self.pool.fetch(
                """
                SELECT * FROM agenttest_test_results
                WHERE agent_version_id = $1 AND deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT $2
                """,
                agent_version_id,
                limit
            )
        elif self._supabase_client:
            return self._supabase_client.get_test_results_history(
                agent_version_id, limit
            )

        return []

    @cached(namespace="skills", ttl=300)
    async def get_skill(self, agent_version_id: str) -> Optional[Dict]:
        """Busca skill mais recente (cacheado)."""
        if self.pool._use_asyncpg:
            return await self.pool.fetchrow(
                """
                SELECT * FROM agenttest_skills
                WHERE agent_version_id = $1 AND deleted_at IS NULL
                ORDER BY version DESC
                LIMIT 1
                """,
                agent_version_id
            )
        elif self._supabase_client:
            return self._supabase_client.get_skill(agent_version_id)

        return None

    @cached(namespace="metrics", ttl=60)
    async def get_agent_metrics(
        self,
        agent_version_id: str,
        days: int = 30
    ) -> List[Dict]:
        """Busca métricas do agente (cacheado)."""
        if self.pool._use_asyncpg:
            return await self.pool.fetch(
                """
                SELECT * FROM agent_metrics
                WHERE agent_version_id = $1
                  AND data >= CURRENT_DATE - $2::INTEGER
                  AND deleted_at IS NULL
                ORDER BY data DESC
                """,
                agent_version_id,
                days
            )
        elif self._supabase_client:
            return self._supabase_client.get_agent_metrics(agent_version_id, days)

        return []

    async def update_agent_test_results(
        self,
        agent_id: str,
        score: float,
        report_url: str,
        test_result_id: str
    ) -> None:
        """Atualiza resultados de teste no agent (invalida cache)."""
        if self.pool._use_asyncpg:
            await self.pool.execute(
                """
                UPDATE agent_versions SET
                    last_test_score = $2,
                    last_test_at = NOW(),
                    test_report_url = $3,
                    framework_approved = $4,
                    status = CASE WHEN $2 >= 8.0 THEN 'active' ELSE 'needs_improvement' END,
                    updated_at = NOW()
                WHERE id = $1
                """,
                agent_id,
                score,
                report_url,
                score >= 8.0
            )
        elif self._supabase_client:
            self._supabase_client.update_agent_test_results(
                agent_id, score, report_url, test_result_id
            )

        # Invalida caches
        await self._cache.delete("agents", agent_id)
        await self._cache.invalidate_namespace("agents_needing_test")

    # ============================================
    # CACHE MANAGEMENT
    # ============================================

    async def clear_cache(self, namespace: Optional[str] = None) -> int:
        """Limpa cache (todo ou namespace específico)."""
        if namespace:
            return await self._cache.invalidate_namespace(namespace)

        # Limpa tudo
        total = 0
        for ns in ["agents", "test_results", "skills", "metrics", "agents_needing_test"]:
            total += await self._cache.invalidate_namespace(ns)
        return total

    async def cleanup_expired_cache(self) -> int:
        """Remove entradas expiradas do cache."""
        return await self._cache.cleanup_expired()


# ============================================
# SINGLETON INSTANCE
# ============================================

_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Retorna instância singleton do DatabaseManager."""
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()

    return _db_manager


async def close_database_manager() -> None:
    """Fecha instância singleton."""
    global _db_manager

    if _db_manager:
        await _db_manager.close()
        _db_manager = None
