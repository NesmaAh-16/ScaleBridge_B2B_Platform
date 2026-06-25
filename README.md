# ScaleBridge 🚀 | B2B Digital Ecosystem

**Empowering small producers through collective purchasing and enterprise matchmaking.**

ScaleBridge is a community-driven B2B platform designed to transform isolated micro-businesses into collaborative economic networks. By bridging the gap between fragmented demand and wholesale markets, ScaleBridge enables small businesses to scale sustainably and allows large enterprises to find reliable, verified local suppliers.

---

## 📖 Project Overview

### The Problem
*   **High Costs:** Small businesses pay premium prices for raw materials due to fragmented, low-volume demand.
*   **Sourcing Difficulty:** Large enterprises struggle to verify and connect with reliable local manufacturers and artisans.

### The ScaleBridge Solution
*   **Buying Circles:** Aggregates demand from multiple small businesses to unlock bulk wholesale pricing.
*   **Intelligent Matchmaking:** A marketplace with advanced filtering (location, category, business type) to connect buyers and sellers.
*   **Trust & Scoring:** A performance-driven rating system tied strictly to completed transaction data.

---

## 👥 The Team

*   **Nesma Ah-16**, **Mahmood**, **Shaimaa:** are all Fullstack Developers

---

## ✨ Key Features
- **Group-Buying System:** Automatic circle closure and bulk order generation when target quantities are reached.
- **B2B Marketplace:** Multi-parameter search for raw materials and finished products.
- **Order Lifecycle Management:** State-machine tracking from `Pending` → `Accepted` → `In Progress` → `Completed`.
- **Trust System:** 1–5 star ratings based on historical order performance and admin-moderated reviews.
- **Secure Authentication:** Role-Based Access Control (RBAC) for Small Businesses, Enterprise Buyers, and Admins.

---

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3 (Bootstrap/Tailwind), JavaScript
- **Backend:** [Django]
- **Database:** MySQL (Relational Schema), ORM
- **Security:** Bcrypt Password Hashing, JWT/Session Auth, CSRF Protection.

---

## 📊 Database Architecture (ERD Highlights)
The system is built on a highly normalized MySQL schema ensuring data integrity:
- **Unified Product Catalog:** Handles both "Materials" and "Products" in a single entity.
- **Price Snapshotting:** Orders store the `price_at_purchase` to ensure financial accuracy.
- **Verification Logic:** Businesses must be approved by an Admin to earn the "Verified" status.

---

## 🚀 Getting Started

### Prerequisites
- [Django 6+/ Python 3.9+]
- MySQL Server

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/NesmaAh-16/ScaleBridge_Project.git

2.  Setup Database:
      - Import the database_schema.sql file into your MySQL Workbench.
3.  Configure Environment:
      - adding your database credentials.
4.  Install Dependencies:
    ```bash
     pip install -r requirements.txt
5.  Run the Application:
    ```bash
     python manage.py runserver

ScaleBridge: Scaling local impact through global connections.

