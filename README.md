# 🎬 CineStar Booking — Movie Ticket Booking System

A complete FastAPI backend for a cinema ticket booking system built as part of the **Innomatics FastAPI Internship Final Project**.

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload

# 3. Open Swagger UI
# http://127.0.0.1:8000/docs
```

---

## 📌 Features Implemented

| Day | Concept | Details |
|-----|---------|---------|
| Day 1 | GET APIs | Home route, list movies, get by ID, summary, bookings |
| Day 2 | POST + Pydantic | `BookingRequest` with field validation (seats 1–10, phone min 10 chars) |
| Day 3 | Helper Functions | `find_movie()`, `calculate_ticket_cost()`, `filter_movies_logic()` |
| Day 4 | CRUD Operations | POST/PUT/DELETE for movies with 201/404 handling |
| Day 5 | Multi-Step Workflow | Seat Hold → Confirm → Booking (or Release) |
| Day 6 | Advanced APIs | Search, Sort, Pagination, Browse (combined) |

---

## 📋 All 20 Endpoints

### 🟢 Beginner — Basic GETs
| # | Method | Route | Description |
|---|--------|-------|-------------|
| Q1 | GET | `/` | Welcome message |
| Q2 | GET | `/movies` | All movies + total seats |
| Q3 | GET | `/movies/{movie_id}` | Get movie by ID |
| Q4 | GET | `/bookings` | All bookings + total revenue |
| Q5 | GET | `/movies/summary` | Stats: expensive/cheap ticket, genre counts |

### 🔵 Easy — Pydantic + Helpers
| # | Method | Route | Description |
|---|--------|-------|-------------|
| Q6 | POST | `/bookings` | BookingRequest model with validation |
| Q7 | — | helpers | `find_movie()`, `calculate_ticket_cost()` |
| Q8 | POST | `/bookings` | Book tickets with seat cost calculation |
| Q9 | POST | `/bookings` | Promo codes: SAVE10 (10% off), SAVE20 (20% off) |
| Q10 | GET | `/movies/filter` | Filter by genre, language, max_price, min_seats |

### 🟡 Medium — CRUD + Workflow
| # | Method | Route | Description |
|---|--------|-------|-------------|
| Q11 | POST | `/movies` | Add new movie (201, duplicate check) |
| Q12 | PUT | `/movies/{movie_id}` | Update ticket price / seats |
| Q13 | DELETE | `/movies/{movie_id}` | Delete movie (blocked if bookings exist) |
| Q14 | POST/GET | `/seat-hold` | Hold seats temporarily |
| Q15 | POST/DELETE | `/seat-confirm/{id}`, `/seat-release/{id}` | Confirm or release a hold |

### 🔴 Hard — Search, Sort, Pagination
| # | Method | Route | Description |
|---|--------|-------|-------------|
| Q16 | GET | `/movies/search?keyword=` | Case-insensitive search on title/genre/language |
| Q17 | GET | `/movies/sort?sort_by=&order=` | Sort by price/title/duration/seats |
| Q18 | GET | `/movies/page?page=&limit=` | Paginate movies with total_pages |
| Q19 | GET | `/bookings/search`, `/bookings/sort`, `/bookings/page` | Search/sort/paginate bookings |
| Q20 | GET | `/movies/browse` | Combined: keyword + genre + language + sort + paginate |

---

## 🎫 Seat Types & Pricing

| Seat Type | Multiplier |
|-----------|-----------|
| Standard  | 1× base price |
| Premium   | 1.5× base price |
| Recliner  | 2× base price |

## 🏷️ Promo Codes

| Code | Discount |
|------|----------|
| `SAVE10` | 10% off total |
| `SAVE20` | 20% off total |

---

## 🛠️ Tech Stack

- **FastAPI** — Web framework
- **Pydantic** — Data validation
- **Uvicorn** — ASGI server

---

## 📁 Project Structure

```
fastapi-movie-ticket-booking/
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
    ├── Q1_home_route.png
    ├── Q2_get_all_movies.png
    ├── ...
    └── Q20_combined_browse.png
```

---

*Built as part of Innomatics Research Labs FastAPI Internship — Final Project*
