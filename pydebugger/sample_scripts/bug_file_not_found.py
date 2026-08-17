#!/usr/bin/env python3
"""Demonstrates a FileNotFoundError."""

if __name__ == "__main__":
    with open("/tmp/definitely_does_not_exist_12345.txt", "r") as f:
        content = f.read()
    print(content)
