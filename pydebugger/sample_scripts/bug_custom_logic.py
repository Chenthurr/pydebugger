#!/usr/bin/env python3
"""Demonstrates a custom logic error (AssertionError)."""

def process_data(data):
    assert len(data) > 0, "Data must not be empty"
    return sum(data) / len(data)

if __name__ == "__main__":
    result = process_data([])  # AssertionError
    print(result)
