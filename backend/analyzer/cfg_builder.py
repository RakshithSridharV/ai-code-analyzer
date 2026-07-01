"""
cfg_builder.py
──────────────
Builds a Control Flow Graph (CFG) from a Python function using
ONLY Python's built-in ast module.

A CFG is a directed graph where:
  - Each NODE is a basic block (sequence of statements with no branches)
  - Each EDGE represents a possible execution path

Node types:
  "entry"     → function entry point
  "exit"      → function exit point
  "block"     → straight-line sequence of statements
  "condition" → if/elif/else branch point
  "loop"      → for/while loop
  "exception" → try/except block

Edge types:
  "sequential"  → normal flow
  "true"        → condition was True
  "false"       → condition was False / else branch
  "loop_back"   → loop iteration back edge
  "exception"   → exception raised
  "return"      → return statement exits

Algorithm:
  1. Create ENTRY node
  2. Walk function body statement by statement
  3. For each If: create condition node, true-branch subgraph,
     false-branch subgraph, merge node after
  4. For each For/While: create loop node, body subgraph,
     back edge to loop node, exit edge out
  5. For each Return/Raise: create edge to EXIT node
  6. For each Try/Except: create try-block, exception edges
     to each handler block, merge after
  7. Create EXIT node

Return format:
{
    "nodes": [
        {
            "id": str,          unique e.g. "node_0", "entry", "exit"
            "type": str,        "entry"|"exit"|"block"|"condition"|"loop"|"exception"
            "label": str,       human readable e.g. "if x > 0" or "for i in arr"
            "line": int|None,   source line number
            "statements": int   number of statements in this block
        }
    ],
    "edges": [
        {
            "from": str,        node id
            "to": str,          node id
            "type": str,        edge type
            "label": str        "True"/"False"/"loop back"/"exception"/""
        }
    ],
    "entry": "entry",
    "exit": "exit",
    "function_name": str,
    "num_paths": int,     estimated number of distinct execution paths
                          (product of branches, capped at 1000)
}

Only analyze the FIRST function found in the tree.
If no function is found, return an empty graph with just entry→exit.

num_paths calculation:
  Start at 1
  For each If node: multiply by 2 (true/false)
  For each loop node: multiply by 2 (entered/skipped)
  For each ExceptHandler: multiply by 2
  Cap at 1000
"""

import ast
from typing import Any


class CFGBuilder:
    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code
        self._node_counter = 0
        self.nodes: list[dict] = []
        self.edges: list[dict] = []

    def build(self) -> dict[str, Any]:
        """Build and return the CFG dict."""
        # Create entry and exit nodes
        entry_id = "entry"
        exit_id = "exit"

        self.nodes.append({
            "id": entry_id,
            "type": "entry",
            "label": "Entry",
            "line": None,
            "statements": 0,
        })
        self.nodes.append({
            "id": exit_id,
            "type": "exit",
            "label": "Exit",
            "line": None,
            "statements": 0,
        })

        # Find the first function definition
        func_node = None
        func_name = "<module>"
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_node = node
                func_name = node.name
                break

        if func_node is None:
            # No function found – entry directly to exit
            self._add_edge(entry_id, exit_id, "sequential", "")
        else:
            # Process the function body
            last = self._process_body(func_node.body, entry_id, exit_id)
            # If last node is not exit, connect to exit
            if last != exit_id:
                self._add_edge(last, exit_id, "sequential", "")

        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "entry": entry_id,
            "exit": exit_id,
            "function_name": func_name,
            "num_paths": self._count_paths(),
        }

    def _new_node(
        self,
        node_type: str,
        label: str,
        line: int | None = None,
        statements: int = 0,
    ) -> str:
        """Create a new node, add to self.nodes, return its id."""
        node_id = f"node_{self._node_counter}"
        self._node_counter += 1
        self.nodes.append({
            "id": node_id,
            "type": node_type,
            "label": label,
            "line": line,
            "statements": statements,
        })
        return node_id

    def _add_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: str = "sequential",
        label: str = "",
    ) -> None:
        """Add an edge to self.edges."""
        self.edges.append({
            "from": from_id,
            "to": to_id,
            "type": edge_type,
            "label": label,
        })

    def _get_line(self, node: ast.AST) -> int | None:
        """Safely get line number from an AST node."""
        return getattr(node, "lineno", None)

    def _stmt_label(self, stmt: ast.stmt) -> str:
        """Generate a short human-readable label for a statement."""
        try:
            return ast.unparse(stmt)[:48]
        except Exception:
            return type(stmt).__name__

    def _process_body(
        self,
        stmts: list,
        current: str,
        exit_id: str,
    ) -> str:
        """
        Process a list of statements starting from current node.
        Return the id of the last node produced.
        Handles: If, For, While, Try, Return, Raise, and plain statements.
        Groups consecutive plain statements into a single block node.
        """
        plain_buffer: list[ast.stmt] = []

        def flush_plain(cur: str) -> str:
            nonlocal plain_buffer
            if not plain_buffer:
                return cur
            label_parts = [self._stmt_label(s) for s in plain_buffer[:3]]
            if len(plain_buffer) > 3:
                label_parts.append("…")
            label = "; ".join(label_parts)
            block_id = self._new_node(
                "block",
                label,
                line=self._get_line(plain_buffer[0]),
                statements=len(plain_buffer),
            )
            self._add_edge(cur, block_id, "sequential", "")
            plain_buffer = []
            return block_id

        for stmt in stmts:
            if isinstance(stmt, ast.If):
                current = flush_plain(current)
                current = self._process_if(stmt, current, exit_id)

            elif isinstance(stmt, (ast.For, ast.While)):
                current = flush_plain(current)
                current = self._process_loop(stmt, current, exit_id)

            elif isinstance(stmt, ast.Try):
                current = flush_plain(current)
                current = self._process_try(stmt, current, exit_id)

            elif isinstance(stmt, (ast.Return, ast.Raise)):
                current = flush_plain(current)
                label = self._stmt_label(stmt)
                ret_node = self._new_node(
                    "block",
                    label,
                    line=self._get_line(stmt),
                    statements=1,
                )
                self._add_edge(current, ret_node, "sequential", "")
                edge_type = "return" if isinstance(stmt, ast.Return) else "exception"
                self._add_edge(ret_node, exit_id, edge_type, "return" if isinstance(stmt, ast.Return) else "raise")
                # After return/raise, flow is dead; return exit so callers know
                return exit_id

            else:
                plain_buffer.append(stmt)

        current = flush_plain(current)
        return current

    def _process_if(
        self,
        node: ast.If,
        current: str,
        exit_id: str,
    ) -> str:
        """
        Create condition node.
        Process true branch and false branch (orelse) separately.
        Merge into a new block node after.
        Return merge node id.
        """
        try:
            condition_label = f"if {ast.unparse(node.test)}"[:48]
        except Exception:
            condition_label = "if <condition>"

        cond_id = self._new_node(
            "condition",
            condition_label,
            line=self._get_line(node),
            statements=1,
        )
        self._add_edge(current, cond_id, "sequential", "")

        merge_id = self._new_node("block", "merge", line=None, statements=0)

        # True branch
        true_end = self._process_body(node.body, cond_id, exit_id)
        if true_end != exit_id:
            self._add_edge(true_end, merge_id, "sequential", "")
        else:
            # True branch always returns; still need to patch first edge label
            pass

        # Fix the first edge from cond_id to true branch to be "true"
        for edge in self.edges:
            if edge["from"] == cond_id and edge["type"] == "sequential":
                edge["type"] = "true"
                edge["label"] = "True"
                break

        # False branch (else / elif)
        if node.orelse:
            false_end = self._process_body(node.orelse, cond_id, exit_id)
            if false_end != exit_id:
                self._add_edge(false_end, merge_id, "sequential", "")
            # Fix the second sequential edge from cond_id to be "false"
            patched = False
            for edge in self.edges:
                if edge["from"] == cond_id and edge["type"] == "sequential" and not patched:
                    edge["type"] = "false"
                    edge["label"] = "False"
                    patched = True
        else:
            # No else: direct false edge to merge
            self._add_edge(cond_id, merge_id, "false", "False")

        return merge_id

    def _process_loop(
        self,
        node: ast.For | ast.While,
        current: str,
        exit_id: str,
    ) -> str:
        """
        Create loop node.
        Process loop body.
        Add back edge from body end to loop node.
        Add exit edge from loop node to after-loop node.
        Return after-loop node id.
        """
        if isinstance(node, ast.For):
            try:
                target = ast.unparse(node.target)
                iter_ = ast.unparse(node.iter)
                loop_label = f"for {target} in {iter_}"[:48]
            except Exception:
                loop_label = "for loop"
        else:
            try:
                loop_label = f"while {ast.unparse(node.test)}"[:48]
            except Exception:
                loop_label = "while loop"

        loop_id = self._new_node(
            "loop",
            loop_label,
            line=self._get_line(node),
            statements=1,
        )
        self._add_edge(current, loop_id, "sequential", "")

        after_id = self._new_node("block", "after loop", line=None, statements=0)

        # Loop body
        body_end = self._process_body(node.body, loop_id, exit_id)
        if body_end != exit_id:
            self._add_edge(body_end, loop_id, "loop_back", "loop back")

        # Exit edge from loop
        self._add_edge(loop_id, after_id, "false", "exit loop")

        # Fix the first sequential edge from loop_id to body as "true"
        for edge in self.edges:
            if edge["from"] == loop_id and edge["type"] == "sequential":
                edge["type"] = "true"
                edge["label"] = "True"
                break

        return after_id

    def _process_try(
        self,
        node: ast.Try,
        current: str,
        exit_id: str,
    ) -> str:
        """
        Create try block.
        Process handlers.
        Merge after.
        """
        try_id = self._new_node(
            "exception",
            "try block",
            line=self._get_line(node),
            statements=len(node.body),
        )
        self._add_edge(current, try_id, "sequential", "")

        merge_id = self._new_node("block", "after try", line=None, statements=0)

        # Process try body
        try_end = self._process_body(node.body, try_id, exit_id)
        if try_end != exit_id:
            self._add_edge(try_end, merge_id, "sequential", "")

        # Process each handler
        for handler in node.handlers:
            exc_name = ""
            if handler.type:
                try:
                    exc_name = ast.unparse(handler.type)
                except Exception:
                    exc_name = "Exception"
            handler_label = f"except {exc_name}" if exc_name else "except"
            handler_id = self._new_node(
                "exception",
                handler_label,
                line=self._get_line(handler),
                statements=len(handler.body),
            )
            self._add_edge(try_id, handler_id, "exception", "exception")
            handler_end = self._process_body(handler.body, handler_id, exit_id)
            if handler_end != exit_id:
                self._add_edge(handler_end, merge_id, "sequential", "")

        # Process else clause (no exception raised)
        if node.orelse:
            else_end = self._process_body(node.orelse, try_id, exit_id)
            if else_end != exit_id:
                self._add_edge(else_end, merge_id, "sequential", "")

        # Process finally clause
        if node.finalbody:
            finally_end = self._process_body(node.finalbody, merge_id, exit_id)
            if finally_end != exit_id:
                return finally_end

        return merge_id

    def _count_paths(self) -> int:
        """Count estimated paths, cap at 1000."""
        paths = 1
        for node in self.nodes:
            if node["type"] == "condition":
                paths *= 2
            elif node["type"] == "loop":
                paths *= 2
            elif node["id"].startswith("node_") and node["label"].startswith("except"):
                paths *= 2
        return min(paths, 1000)
