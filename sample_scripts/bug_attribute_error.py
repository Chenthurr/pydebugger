#!/usr/bin/env python3
"""Demonstrates an AttributeError."""

class User:
    def __init__(self, name):
        self.name = name

if __name__ == "__main__":
    user = User("Alice")
    print(user.email)  # AttributeError
