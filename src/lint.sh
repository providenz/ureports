#!/bin/bash

# Run Python linting and formatting
isort .
ruff check .
ruff format .


