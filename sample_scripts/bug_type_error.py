#!/usr/bin/env python3
"""Demonstrates a TypeError."""

def add(a, b):
    return a + b

if __name__ == "__main__":
    result = add("hello", 42)  # str + int -> TypeError
    print(result)
