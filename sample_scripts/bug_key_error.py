#!/usr/bin/env python3
"""Demonstrates a KeyError."""

data = {"a": 1, "b": 2}

if __name__ == "__main__":
    value = data["z"]  # KeyError
    print(value)
