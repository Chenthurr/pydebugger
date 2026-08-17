#!/usr/bin/env python3
"""Demonstrates a RecursionError."""

def infinite_recursion(n):
    return infinite_recursion(n + 1)

if __name__ == "__main__":
    infinite_recursion(0)
