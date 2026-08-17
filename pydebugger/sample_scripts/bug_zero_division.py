#!/usr/bin/env python3
"""Demonstrates a ZeroDivisionError."""

def calculate(x, y):
    return x / y

if __name__ == "__main__":
    result = calculate(10, 0)  # ZeroDivisionError
    print(result)
