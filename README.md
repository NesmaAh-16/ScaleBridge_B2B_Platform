# ScaleBridge | B2B Digital Ecosystem

**Empowering small producers through collective purchasing and enterprise matchmaking.**

ScaleBridge is a community-driven B2B platform designed to transform isolated micro-businesses into collaborative economic networks. By bridging the gap between fragmented demand and wholesale markets, ScaleBridge enables small businesses to scale sustainably and allows large enterprises to find reliable, verified local suppliers.

---

## The Problem
- **High Costs:** Small businesses pay premium prices for raw materials due to fragmented, low-volume demand.
- **Sourcing Difficulty:** Large enterprises struggle to verify and connect with reliable local manufacturers and artisans.

## The ScaleBridge Solution
- **Buying Circles:** Aggregates demand from multiple small businesses to unlock bulk wholesale pricing.
- **Intelligent Matchmaking:** A marketplace with advanced filtering (location, category, business type) to connect buyers and sellers.
- **Trust & Scoring:** A performance-driven rating system tied strictly to completed transaction data.

---

## The Team

**Nesma Ah-16**, **Mahmoud**, **Shaimaa** — Fullstack Developers

---

## Key Features
- **Group-Buying System:** Automatic circle closure and bulk order generation when target quantities are reached.
- **B2B Marketplace:** Multi-parameter search for raw materials and finished products.
- **Order Lifecycle Management:** State-machine tracking from `Pending` → `Accepted` → `In Progress` → `Completed`.
- **Trust System:** 1–5 star ratings based on historical order performance and admin-moderated reviews.
- **Secure Authentication:** Session-based auth with Role-Based Access Control (RBAC) for Small Businesses, Enterprise Buyers, and Admins.

---

## Tech Stack
- **Frontend:** Tailwind CSS (CDN), Django Templates (MTV)
- **Backend:** Django 6 / Python 3
- **Database:** SQLite (development) via Django ORM
- **Security:** Django password hashing (PBKDF2), CSRF protection, session-based authentication

---

## Database Architecture (ERD Highlights)
The system is built on a normalized relational schema ensuring data integrity:
- **Unified Product Catalog:** Handles both "Materials" and "Products" in a single entity.
- **Price Snapshotting:** Orders store the `price_at_purchase` to ensure financial accuracy.
- **Verification Logic:** Businesses must be approved by an Admin to earn the "Verified" status.

---

## Implemented — Feature: Auth Setup

### URL Routes

| Method | URL | Description |
|--------|-----|-------------|
| GET/POST | `/accounts/register/` | Register a new Business or Enterprise account |
| GET/POST | `/accounts/login/` | Login with email and password |
| GET | `/accounts/logout/` | Logout and clear session |
| GET | `/accounts/me/` | Authenticated user profile (protected) |

### User Roles

| Role | Access Level |
|------|-------------|
| `Admin` | Full system access — user management, moderation, verification |
| `SmallBusiness` | Buying circles, product listings, order tracking |
| `EnterpriseBuyer` | Marketplace browsing, bulk orders, supply contracts |

### RBAC Decorator
Protected views use the reusable `role_required` decorator:
```python
from accounts.decorators import role_required

@role_required('Admin')
def admin_only_view(request):
    ...
```

### Design System (Tailwind CSS)
| Token | Color |
|-------|-------|
| Primary Deep Navy | `rgb(10, 54, 88)` |
| Vibrant Brand Green | `rgb(144, 191, 73)` |
| Mid-Tone Teal | `rgb(38, 102, 117)` |
| Dashboard Neutral | `rgb(248, 250, 252)` |

---

## Getting Started

### Prerequisites
- Python 3.9+
- pip + virtualenv

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NesmaAh-16/ScaleBridge_Project.git
   cd ScaleBridge_B2B_Platform
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate      # Linux/Mac
   env\Scripts\activate         # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Seed the admin user:**
   ```bash
   python manage.py seed_admin
   ```
   Default credentials:
   - Email: `admin@scalebridge.com`
   - Password: `Admin@1234`

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. Open `http://127.0.0.1:8000/` — you will be redirected to the login page.

---

## Running Tests

```bash
python manage.py test accounts -v 2
```

35 test cases covering registration, login, logout, profile access, RBAC, and user model integrity.

---

*ScaleBridge — Scaling local impact through global connections.*
