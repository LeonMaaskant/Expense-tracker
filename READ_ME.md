# Expense Tracker

A Flask web application that processes and analyzes bank statements to provide actionable financial insights. Built as a portfolio project to demonstrate full-stack development skills and real-world data processing.

## Project Overview

This application solves a real problem: understanding personal spending patterns. Users upload their bank statements and receive instant analysis including spending categorization, transaction trends, and financial summaries.

## Key Features

- Secure File Upload System - Validates file types, handles encoding issues (ISO-8859-1), and prevents malicious uploads
- Financial Analytics
  - Income vs. expense tracking with net balance calculation
  - Transaction count and average spending metrics
  - Daily spending rate across statement period
  - Top 5 expense identification
- Smart Categorization - Automatically categorizes transactions into:
  - Groceries (Kiwi, Meny, Rema 1000, etc.)
  - Salary deposits
  - Transport (Skyss, taxi, buses)
  - Investments (Skilling, Nordnet)
  - Other expenses
- Data Visualization - Clean HTML tables displaying categorized expenses

## Technical Stack

- Backend: Flask (Python)
- Data Processing: Pandas, NumPy
- Security: Werkzeug for secure filename handling
- Format Support: CSV/TXT files with semicolon delimiters

## Technical Highlights

- Handles real-world data challenges (NaN values, encoding issues, irregular formats)
- Server-side validation for security (doesn't rely on client-side checks)
- Clean separation of concerns with dedicated categorization logic
- File size limits and extension validation to prevent abuse

## Installation & Setup

# Clone repository

git clone [your-repo-url]

# Create virtual environment

python -m venv expense_env

# Activate environment

expense_env\Scripts\activate # Windows
source expense_env/bin/activate # Mac/Linux

# Install dependencies

pip install -r requirements.txt

# Run application

python app.py

Visit http://localhost:5000 to use the application.

## Supported Formats

Currently optimized for DNB (Den Norske Bank) CSV exports with semicolon delimiters. The categorization logic can be easily extended for other Norwegian banks.

## Future Enhancements

React Frontend - Modern UI with interactive charts and visualizations
Multi-bank Support - Handle different CSV formats (Nordea, Sparebank1, etc.)
AI-Powered Categorization - OpenAI API integration for smarter expense classification
Data Persistence - Database integration for historical tracking
Export Features - PDF reports and CSV exports of analyzed data

## What I Learned so far

Building production-ready file upload systems with proper security
Working with messy real-world data (encoding issues, inconsistent formats)
Creating practical business logic for financial categorization
Structuring Flask applications for maintainability

## Developer

Leon Maaskant - AI Bachelor Student at University of Bergen (Graduation: Summer 2026)
