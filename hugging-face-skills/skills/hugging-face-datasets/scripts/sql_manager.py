#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "duckdb>=1.0.0",
#   "huggingface_hub>=0.20.0",
#   "datasets>=2.14.0",
#   "pandas>=2.0.0",
# ]
# ///
"""
Hugging Face Dataset SQL Manager

Query, transform, and push Hugging Face datasets using DuckDB's SQL interface.
Supports the hf:// protocol for direct dataset access, data wrangling, and 
pushing results back to the Hub.

Version: 1.0.0

Usage:
    # Query a dataset
    uv run sql_manager.py query --dataset "cais/mmlu" --sql "SELECT * FROM data LIMIT 10"
    
    # Query and push to new dataset
    uv run sql_manager.py query --dataset "cais/mmlu" --sql "SELECT * FROM data WHERE subject='nutrition'" \
        --push-to "username/nutrition-subset"
    
    # Describe dataset schema
    uv run sql_manager.py describe --dataset "cais/mmlu"
    
    # List available splits/configs
    uv run sql_manager.py info --dataset "cais/mmlu"
    
    # Get random sample
    uv run sql_manager.py sample --dataset "cais/mmlu" --n 5
    
    # Export to parquet
    uv run sql_manager.py export --dataset "cais/mmlu" --output "data.parquet"
"""

import os
import json
import argparse
from typing import Optional, List, Dict, Any, Union

import duckdb
from huggingface_hub import HfApi


# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN")


class HFDatasetSQL:
    """
    Query Hugging Face datasets using DuckDB SQL.

    Examples:
        >>> sql = HFDatasetSQL()
        >>> results = sql.query("cais/mmlu", "SELECT * FROM data LIMIT 5")
        >>> schema = sql.describe("cais/mmlu")
        >>> sql.query_and_push("cais/mmlu", "SELECT * FROM data WHERE subject='nutrition'", "user/nutrition-qa")
    """

    def __init__(self, token: Optional[str] = None):
        """Initialize the SQL manager with optional HF token."""
        self.token = token or HF_TOKEN
        self.conn = duckdb.connect()
        self._setup_connection()

    def _setup_connection(self):
        """Configure DuckDB connection for HF access."""
        # Set HF token if available (for private datasets)
        if self.token:
            self.conn.execute(f"CREATE SECRET hf_token (TYPE HUGGINGFACE, TOKEN '{self.token}');")

    def _build_hf_path(
        self, dataset_id: str, split: str = "*", config: Optional[str] = None, revision: str = "~parquet"
    ) -> str:
        """
        Build the hf:// path for a dataset.

        Args:
            dataset_id: Dataset ID (e.g., "cais/mmlu")
            split: Split name or "*" for all splits
            config: Optional config/subset name
            revision: Revision, defaults to ~parquet for auto-converted parquet

        Returns:
            hf:// path string
        """
        if config:
            return f"hf://datasets/{dataset_id}@{revision}/{config}/{split}/*.parquet"
        else:
            return f"hf://datasets/{dataset_id}@{revision}/default/{split}/*.parquet"

    def _build_hf_path_flexible(
        self,
        dataset_id: str,
        split: Optional[str] = None,
        config: Optional[str] = None,
    ) -> str:
        """
        Build flexible hf:// path with wildcards for discovery.

        Args:
            dataset_id: Dataset ID
            split: Optional specific split
            config: Optional config name

        Returns:
            hf:// path with appropriate wildcards
        """
        base = f"hf://datasets/{dataset_id}@~parquet"

        if config and split:
            return f"{base}/{config}/{split}/*.parquet"
        elif config:
            return f"{base}/{config}/*/*.parquet"
        elif split:
            return f"{base}/*/{split}/*.parquet"
        else:
            return f"{base}/*/*/*.parquet"

    def query(
        self,
        dataset_id: str,
        sql: str,
        split: str = "train",
        config: Optional[str] = None,
        limit: Optional[int] = None,
        output_format: str = "dict",
    ) -> Union[List[Dict], Any]:
        """
        Execute SQL query on a Hugging Face dataset.

        Args:
            dataset_id: Dataset ID (e.g., "cais/mmlu", "ibm/duorc")
            sql: SQL query. Use 'data' as table name (will be replaced with actual path)
            split: Dataset split (train, test, validation, or * for all)
            config: Optional dataset config/subset
            limit: Optional limit override
            output_format: Output format - "dict", "df" (pandas), "arrow", "raw"

        Returns:
            Query results in specified format

        Examples:
            >>> sql.query("cais/mmlu", "SELECT * FROM data WHERE subject='nutrition' LIMIT 10")
            >>> sql.query("cais/mmlu", "SELECT subject, COUNT(*) as cnt FROM data GROUP BY subject")
        """
        # Build the HF path
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        # Replace 'data' placeholder with actual path
        # Handle various SQL patterns
        processed_sql = sql.replace("FROM data", f"FROM '{hf_path}'")
        processed_sql = processed_sql.replace("from data", f"FROM '{hf_path}'")
        processed_sql = processed_sql.replace("JOIN data", f"JOIN '{hf_path}'")
        processed_sql = processed_sql.replace("join data", f"JOIN '{hf_path}'")

        # If user provides raw path, use as-is
        if "hf://" in sql:
            processed_sql = sql

        # Apply limit if specified and not already in query
        if limit and "LIMIT" not in processed_sql.upper():
            processed_sql += f" LIMIT {limit}"

        try:
            result = self.conn.execute(processed_sql)

            if output_format == "df":
                return result.fetchdf()
            elif output_format == "arrow":
                return result.fetch_arrow_table()
            elif output_format == "raw":
                return result.fetchall()
            else:  # dict
                columns = [desc[0] for desc in result.description]
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            print(f"❌ Query error: {e}")
            print(f"   SQL: {processed_sql[:200]}...")
            raise

    def query_raw(self, sql: str, output_format: str = "dict") -> Union[List[Dict], Any]:
        """
        Execute raw SQL query without path substitution.

        Useful for queries that already contain full hf:// paths or for
        multi-dataset queries.

        Args:
            sql: Complete SQL query
            output_format: Output format

        Returns:
            Query results
        """
        result = self.conn.execute(sql)

        if output_format == "df":
            return result.fetchdf()
        elif output_format == "arrow":
            return result.fetch_arrow_table()
        elif output_format == "raw":
            return result.fetchall()
        else:
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def describe(self, dataset_id: str, split: str = "train", config: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get schema/structure of a dataset.

        Args:
            dataset_id: Dataset ID
            split: Dataset split
            config: Optional config

        Returns:
            List of column definitions with name, type, nullable info
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        sql = f"DESCRIBE SELECT * FROM '{hf_path}' LIMIT 1"
        result = self.conn.execute(sql)

        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    def sample(
        self,
        dataset_id: str,
        n: int = 10,
        split: str = "train",
        config: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get a random sample from a dataset.

        Args:
            dataset_id: Dataset ID
            n: Number of samples
            split: Dataset split
            config: Optional config
            seed: Random seed for reproducibility

        Returns:
            List of sampled rows
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        if seed is not None:
            sql = f"SELECT * FROM '{hf_path}' USING SAMPLE {n} (RESERVOIR, {seed})"
        else:
            sql = f"SELECT * FROM '{hf_path}' USING SAMPLE {n}"

        return self.query_raw(sql)

    def count(
        self, dataset_id: str, split: str = "train", config: Optional[str] = None, where: Optional[str] = None
    ) -> int:
        """
        Count rows in a dataset, optionally with filter.

        Args:
            dataset_id: Dataset ID
            split: Dataset split
            config: Optional config
            where: Optional WHERE clause (without WHERE keyword)

        Returns:
            Row count
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        sql = f"SELECT COUNT(*) FROM '{hf_path}'"
        if where:
            sql += f" WHERE {where}"

        result = self.conn.execute(sql).fetchone()
        return result[0] if result else 0

    def unique_values(
        self, dataset_id: str, column: str, split: str = "train", config: Optional[str] = None, limit: int = 100
    ) -> List[Any]:
        """
        Get unique values in a column.

        Args:
            dataset_id: Dataset ID
            column: Column name
            split: Dataset split
            config: Optional config
            limit: Max unique values to return

        Returns:
            List of unique values
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        sql = f"SELECT DISTINCT {column} FROM '{hf_path}' LIMIT {limit}"
        result = self.conn.execute(sql).fetchall()

        return [row[0] for row in result]

    def histogram(
        self, dataset_id: str, column: str, split: str = "train", config: Optional[str] = None, bins: int = 10
    ) -> List[Dict]:
        """
        Get value distribution/histogram for a column.

        Args:
            dataset_id: Dataset ID
            column: Column name
            split: Dataset split
            config: Optional config
            bins: Number of bins for numeric columns

        Returns:
            Distribution data
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        sql = f"""
        SELECT 
            {column},
            COUNT(*) as count
        FROM '{hf_path}'
        GROUP BY {column}
        ORDER BY count DESC
        LIMIT {bins}
        """

        return self.query_raw(sql)

    def filter_and_transform(
        self,
        dataset_id: str,
        select: str = "*",
        where: Optional[str] = None,
        group_by: Optional[str] = None,
        order_by: Optional[str] = None,
        split: str = "train",
        config: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Filter and transform dataset with SQL clauses.

        Args:
            dataset_id: Dataset ID
            select: SELECT clause (columns, expressions, aggregations)
            where: WHERE clause (filter conditions)
            group_by: GROUP BY clause
            order_by: ORDER BY clause
            split: Dataset split
            config: Optional config
            limit: Row limit

        Returns:
            Transformed data

        Examples:
            >>> sql.filter_and_transform(
            ...     "cais/mmlu",
            ...     select="subject, COUNT(*) as cnt",
            ...     group_by="subject",
            ...     order_by="cnt DESC",
            ...     limit=10
            ... )
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        sql_parts = [f"SELECT {select}", f"FROM '{hf_path}'"]

        if where:
            sql_parts.append(f"WHERE {where}")
        if group_by:
            sql_parts.append(f"GROUP BY {group_by}")
        if order_by:
            sql_parts.append(f"ORDER BY {order_by}")
        if limit:
            sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)
        return self.query_raw(sql)

    def join_datasets(
        self,
        left_dataset: str,
        right_dataset: str,
        on: str,
        select: str = "*",
        join_type: str = "INNER",
        left_split: str = "train",
        right_split: str = "train",
        left_config: Optional[str] = None,
        right_config: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Join two datasets.

        Args:
            left_dataset: Left dataset ID
            right_dataset: Right dataset ID
            on: JOIN condition (e.g., "left.id = right.id")
            select: SELECT clause
            join_type: Type of join (INNER, LEFT, RIGHT, FULL)
            left_split: Split for left dataset
            right_split: Split for right dataset
            left_config: Config for left dataset
            right_config: Config for right dataset
            limit: Row limit

        Returns:
            Joined data
        """
        left_path = self._build_hf_path(left_dataset, split=left_split, config=left_config)
        right_path = self._build_hf_path(right_dataset, split=right_split, config=right_config)

        sql = f"""
        SELECT {select}
        FROM '{left_path}' AS left_table
        {join_type} JOIN '{right_path}' AS right_table
        ON {on}
        """

        if limit:
            sql += f" LIMIT {limit}"

        return self.query_raw(sql)

    def export_to_parquet(
        self,
        dataset_id: str,
        output_path: str,
        sql: Optional[str] = None,
        split: str = "train",
        config: Optional[str] = None,
    ) -> str:
        """
        Export query results to a local Parquet file.

        Args:
            dataset_id: Source dataset ID
            output_path: Local path for output Parquet file
            sql: Optional SQL query (uses SELECT * if not provided)
            split: Dataset split
            config: Optional config

        Returns:
            Path to created file
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)

        if sql:
            # Process the query
            processed_sql = sql.replace("FROM data", f"FROM '{hf_path}'")
            processed_sql = processed_sql.replace("from data", f"FROM '{hf_path}'")
        else:
            processed_sql = f"SELECT * FROM '{hf_path}'"

        export_sql = f"COPY ({processed_sql}) TO '{output_path}' (FORMAT PARQUET)"
        self.conn.execute(export_sql)

        print(f"✅ Exported to {output_path}")
        return output_path

    def export_to_jsonl(
        self,
        dataset_id: str,
        output_path: str,
        sql: Optional[str] = None,
        split: str = "train",
        config: Optional[str] = None,
    ) -> str:
        """
        Export query results to JSONL format.

        Args:
            dataset_id: Source dataset ID
            output_path: Local path for output JSONL file
            sql: Optional SQL query
            split: Dataset split
            config: Optional config

        Returns:
            Path to created file
        """
        results = self.query(dataset_id, sql or "SELECT * FROM data", split=split, config=config)

        with open(output_path, "w") as f:
            for row in results:
                f.write(json.dumps(row) + "\n")

        print(f"✅ Exported {len(results)} rows to {output_path}")
        return output_path

    def push_to_hub(
        self,
        dataset_id: str,
        target_repo: str,
        sql: Optional[str] = None,
        split: str = "train",
        config: Optional[str] = None,
        target_split: str = "train",
        private: bool = True,
        commit_message: Optional[str] = None,
    ) -> str:
        """
        Query a dataset and push results to a new Hub repository.

        Args:
            dataset_id: Source dataset ID
            target_repo: Target repository ID (e.g., "username/new-dataset")
            sql: SQL query to transform data (optional, defaults to SELECT *)
            split: Source split
            config: Source config
            target_split: Target split name
            private: Whether to create private repo
            commit_message: Commit message

        Returns:
            URL of created dataset
        """
        try:
            from datasets import Dataset
        except ImportError:
            raise ImportError("datasets library required for push_to_hub. Install with: pip install datasets")

        # Execute query
        results = self.query(dataset_id, sql or "SELECT * FROM data", split=split, config=config)

        if not results:
            print("❌ No results to push")
            return ""

        # Convert to HF Dataset
        ds = Dataset.from_list(results)

        # Push to Hub
        ds.push_to_hub(
            target_repo,
            split=target_split,
            private=private,
            commit_message=commit_message or f"Created from {dataset_id} via SQL query",
            token=self.token,
        )

        url = f"https://huggingface.co/datasets/{target_repo}"
        print(f"✅ Pushed {len(results)} rows to {url}")
        return url

    def create_view(self, name: str, dataset_id: str, split: str = "train", config: Optional[str] = None):
        """
        Create a DuckDB view for easier querying.

        Args:
            name: View name
            dataset_id: Dataset ID
            split: Dataset split
            config: Optional config
        """
        hf_path = self._build_hf_path(dataset_id, split=split, config=config)
        self.conn.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM '{hf_path}'")
        print(f"✅ Created view '{name}' for {dataset_id}")

    def info(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get information about a dataset including available configs and splits.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset information
        """
        api = HfApi(token=self.token)

        try:
            info = api.dataset_info(dataset_id)

            result = {
                "id": info.id,
                "author": info.author,
                "private": info.private,
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "created_at": str(info.created_at) if info.created_at else None,
                "last_modified": str(info.last_modified) if info.last_modified else None,
            }

            # Try to get config/split info from card data
            if info.card_data:
                result["configs"] = getattr(info.card_data, "configs", None)

            return result

        except Exception as e:
            print(f"❌ Failed to get info: {e}")
            return {}

    def close(self):
        """Close the database connection."""
        self.conn.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Query Hugging Face datasets with SQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query dataset with SQL
  python sql_manager.py query --dataset "cais/mmlu" --sql "SELECT * FROM data WHERE subject='nutrition' LIMIT 10"
  
  # Get random sample
  python sql_manager.py sample --dataset "cais/mmlu" --n 5
  
  # Describe schema
  python sql_manager.py describe --dataset "cais/mmlu"
  
  # Get value counts
  python sql_manager.py histogram --dataset "cais/mmlu" --column "subject"
  
  # Filter and transform
  python sql_manager.py transform --dataset "cais/mmlu" \\
    --select "subject, COUNT(*) as cnt" \\
    --group-by "subject" \\
    --order-by "cnt DESC"
  
  # Query and push to Hub
  python sql_manager.py query --dataset "cais/mmlu" \\
    --sql "SELECT * FROM data WHERE subject='nutrition'" \\
    --push-to "username/nutrition-subset"
  
  # Export to Parquet
  python sql_manager.py export --dataset "cais/mmlu" \\
    --sql "SELECT * FROM data WHERE subject='nutrition'" \\
    --output "nutrition.parquet"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("--dataset", "-d", required=True, help="Dataset ID (e.g., cais/mmlu)")
        p.add_argument("--split", "-s", default="train", help="Dataset split (default: train)")
        p.add_argument("--config", "-c", help="Dataset config/subset")

    # Query command
    query_parser = subparsers.add_parser("query", help="Execute SQL query on dataset")
    add_common_args(query_parser)
    query_parser.add_argument("--sql", required=True, help="SQL query (use 'data' as table name)")
    query_parser.add_argument("--limit", "-l", type=int, help="Limit results")
    query_parser.add_argument("--format", choices=["json", "table", "csv"], default="json", help="Output format")
    query_parser.add_argument("--push-to", help="Push results to this Hub repo")
    query_parser.add_argument("--private", action="store_true", help="Make pushed repo private")

    # Sample command
    sample_parser = subparsers.add_parser("sample", help="Get random sample from dataset")
    add_common_args(sample_parser)
    sample_parser.add_argument("--n", type=int, default=10, help="Number of samples")
    sample_parser.add_argument("--seed", type=int, help="Random seed")

    # Describe command
    describe_parser = subparsers.add_parser("describe", help="Get dataset schema")
    add_common_args(describe_parser)

    # Count command
    count_parser = subparsers.add_parser("count", help="Count rows in dataset")
    add_common_args(count_parser)
    count_parser.add_argument("--where", "-w", help="WHERE clause for filtering")

    # Histogram command
    histogram_parser = subparsers.add_parser("histogram", help="Get value distribution")
    add_common_args(histogram_parser)
    histogram_parser.add_argument("--column", required=True, help="Column name")
    histogram_parser.add_argument("--bins", type=int, default=20, help="Number of bins")

    # Unique command
    unique_parser = subparsers.add_parser("unique", help="Get unique values in column")
    add_common_args(unique_parser)
    unique_parser.add_argument("--column", required=True, help="Column name")
    unique_parser.add_argument("--limit", "-l", type=int, default=100, help="Max values")

    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Filter and transform dataset")
    add_common_args(transform_parser)
    transform_parser.add_argument("--select", default="*", help="SELECT clause")
    transform_parser.add_argument("--where", "-w", help="WHERE clause")
    transform_parser.add_argument("--group-by", help="GROUP BY clause")
    transform_parser.add_argument("--order-by", help="ORDER BY clause")
    transform_parser.add_argument("--limit", "-l", type=int, help="LIMIT")
    transform_parser.add_argument("--push-to", help="Push results to Hub repo")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export query results to file")
    add_common_args(export_parser)
    export_parser.add_argument("--sql", help="SQL query (defaults to SELECT *)")
    export_parser.add_argument("--output", "-o", required=True, help="Output file path")
    export_parser.add_argument("--format", choices=["parquet", "jsonl"], default="parquet", help="Output format")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get dataset information")
    info_parser.add_argument("--dataset", "-d", required=True, help="Dataset ID")

    # Raw SQL command
    raw_parser = subparsers.add_parser("raw", help="Execute raw SQL with full hf:// paths")
    raw_parser.add_argument("--sql", required=True, help="Complete SQL query")
    raw_parser.add_argument("--format", choices=["json", "table", "csv"], default="json", help="Output format")

    args = parser.parse_args()

    # Initialize SQL manager
    sql = HFDatasetSQL()

    try:
        if args.command == "query":
            results = sql.query(args.dataset, args.sql, split=args.split, config=args.config, limit=args.limit)

            if getattr(args, "push_to", None):
                sql.push_to_hub(
                    args.dataset, args.push_to, sql=args.sql, split=args.split, config=args.config, private=args.private
                )
            else:
                _print_results(results, args.format)

        elif args.command == "sample":
            results = sql.sample(args.dataset, n=args.n, split=args.split, config=args.config, seed=args.seed)
            _print_results(results, "json")

        elif args.command == "describe":
            schema = sql.describe(args.dataset, split=args.split, config=args.config)
            _print_results(schema, "table")

        elif args.command == "count":
            count = sql.count(args.dataset, split=args.split, config=args.config, where=args.where)
            print(f"Count: {count:,}")

        elif args.command == "histogram":
            results = sql.histogram(args.dataset, args.column, split=args.split, config=args.config, bins=args.bins)
            _print_results(results, "table")

        elif args.command == "unique":
            values = sql.unique_values(
                args.dataset, args.column, split=args.split, config=args.config, limit=args.limit
            )
            for v in values:
                print(v)

        elif args.command == "transform":
            results = sql.filter_and_transform(
                args.dataset,
                select=args.select,
                where=args.where,
                group_by=args.group_by,
                order_by=args.order_by,
                split=args.split,
                config=args.config,
                limit=args.limit,
            )

            if getattr(args, "push_to", None):
                # Build SQL for push
                query_sql = f"SELECT {args.select} FROM data"
                if args.where:
                    query_sql += f" WHERE {args.where}"
                if args.group_by:
                    query_sql += f" GROUP BY {args.group_by}"
                if args.order_by:
                    query_sql += f" ORDER BY {args.order_by}"
                if args.limit:
                    query_sql += f" LIMIT {args.limit}"

                sql.push_to_hub(args.dataset, args.push_to, sql=query_sql, split=args.split, config=args.config)
            else:
                _print_results(results, "json")

        elif args.command == "export":
            if args.format == "parquet":
                sql.export_to_parquet(args.dataset, args.output, sql=args.sql, split=args.split, config=args.config)
            else:
                sql.export_to_jsonl(args.dataset, args.output, sql=args.sql, split=args.split, config=args.config)

        elif args.command == "info":
            info = sql.info(args.dataset)
            _print_results([info], "json")

        elif args.command == "raw":
            results = sql.query_raw(args.sql)
            _print_results(results, args.format)

    finally:
        sql.close()


def _print_results(results: List[Dict], format: str):
    """Print results in specified format."""
    if not results:
        print("No results")
        return

    if format == "json":
        print(json.dumps(results, indent=2, default=str))

    elif format == "csv":
        if results:
            keys = results[0].keys()
            print(",".join(str(k) for k in keys))
            for row in results:
                print(",".join(str(row.get(k, "")) for k in keys))

    elif format == "table":
        if results:
            keys = list(results[0].keys())
            # Calculate column widths
            widths = {k: max(len(str(k)), max(len(str(r.get(k, ""))) for r in results)) for k in keys}

            # Header
            header = " | ".join(str(k).ljust(widths[k]) for k in keys)
            print(header)
            print("-" * len(header))

            # Rows
            for row in results:
                print(" | ".join(str(row.get(k, "")).ljust(widths[k]) for k in keys))


if __name__ == "__main__":
    main()
