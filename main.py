from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(title="CineStar Booking", description="Movie Ticket Booking System", version="1.0.0")

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

movies = [
    {"id": 1, "title": "Inception", "genre": "Action", "language": "English", "duration_mins": 148, "ticket_price": 250, "seats_available": 50},
    {"id": 2, "title": "The Dark Knight", "genre": "Action", "language": "English", "duration_mins": 152, "ticket_price": 300, "seats_available": 40},
    {"id": 3, "title": "Dilwale Dulhania Le Jayenge", "genre": "Drama", "language": "Hindi", "duration_mins": 189, "ticket_price": 150, "seats_available": 60},
    {"id": 4, "title": "3 Idiots", "genre": "Comedy", "language": "Hindi", "duration_mins": 170, "ticket_price": 180, "seats_available": 70},
    {"id": 5, "title": "The Conjuring", "genre": "Horror", "language": "English", "duration_mins": 112, "ticket_price": 200, "seats_available": 30},
    {"id": 6, "title": "Parasite", "genre": "Drama", "language": "Korean", "duration_mins": 132, "ticket_price": 220, "seats_available": 45},
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

movie_counter = 7  # next id for new movies


# ─────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────

class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = Field(default="standard")
    promo_code: str = Field(default="")


class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)


class SeatHoldRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def find_movie(movie_id: int):
    for m in movies:
        if m["id"] == movie_id:
            return m
    return None


def calculate_ticket_cost(base_price: int, seats: int, seat_type: str, promo_code: str = ""):
    multipliers = {"standard": 1.0, "premium": 1.5, "recliner": 2.0}
    multiplier = multipliers.get(seat_type.lower(), 1.0)
    original_cost = base_price * seats * multiplier

    discounted_cost = original_cost
    discount_applied = "none"

    if promo_code == "SAVE10":
        discounted_cost = original_cost * 0.90
        discount_applied = "10% off (SAVE10)"
    elif promo_code == "SAVE20":
        discounted_cost = original_cost * 0.80
        discount_applied = "20% off (SAVE20)"

    return {
        "original_cost": round(original_cost, 2),
        "discounted_cost": round(discounted_cost, 2),
        "discount_applied": discount_applied
    }


def filter_movies_logic(genre=None, language=None, max_price=None, min_seats=None):
    result = movies[:]
    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]
    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]
    return result


# ─────────────────────────────────────────────
# Q1 — HOME ROUTE
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}


# ─────────────────────────────────────────────
# Q2 — GET ALL MOVIES
# ─────────────────────────────────────────────

@app.get("/movies")
def get_all_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {
        "total": len(movies),
        "total_seats_available": total_seats,
        "movies": movies
    }


# ─────────────────────────────────────────────
# FIXED ROUTES MUST COME BEFORE /{movie_id}
# ─────────────────────────────────────────────

# Q5 — MOVIES SUMMARY
@app.get("/movies/summary")
def movies_summary():
    if not movies:
        return {"message": "No movies available"}
    most_expensive = max(movies, key=lambda m: m["ticket_price"])
    cheapest = min(movies, key=lambda m: m["ticket_price"])
    total_seats = sum(m["seats_available"] for m in movies)
    genre_count = {}
    for m in movies:
        genre_count[m["genre"]] = genre_count.get(m["genre"], 0) + 1
    return {
        "total_movies": len(movies),
        "most_expensive_ticket": most_expensive["title"],
        "most_expensive_price": most_expensive["ticket_price"],
        "cheapest_ticket": cheapest["title"],
        "cheapest_price": cheapest["ticket_price"],
        "total_seats_across_all_movies": total_seats,
        "movies_by_genre": genre_count
    }


# Q10 — FILTER MOVIES
@app.get("/movies/filter")
def filter_movies(
    genre: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default=None),
    max_price: Optional[int] = Query(default=None),
    min_seats: Optional[int] = Query(default=None)
):
    result = filter_movies_logic(genre, language, max_price, min_seats)
    return {"total": len(result), "movies": result}


# Q16 — SEARCH MOVIES
@app.get("/movies/search")
def search_movies(keyword: str = Query(...)):
    kw = keyword.lower()
    result = [
        m for m in movies
        if kw in m["title"].lower() or kw in m["genre"].lower() or kw in m["language"].lower()
    ]
    if not result:
        return {"message": f"No movies found for keyword '{keyword}'", "total_found": 0}
    return {"total_found": len(result), "movies": result}


# Q17 — SORT MOVIES
@app.get("/movies/sort")
def sort_movies(
    sort_by: str = Query(default="ticket_price"),
    order: str = Query(default="asc")
):
    valid_sort_fields = ["ticket_price", "title", "duration_mins", "seats_available"]
    valid_orders = ["asc", "desc"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sort_fields}")
    if order not in valid_orders:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    sorted_movies = sorted(movies, key=lambda m: m[sort_by], reverse=(order == "desc"))
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_movies),
        "movies": sorted_movies
    }


# Q18 — PAGINATE MOVIES
@app.get("/movies/page")
def paginate_movies(page: int = Query(default=1), limit: int = Query(default=3)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page and limit must be >= 1")
    total = len(movies)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "movies": movies[start:end]
    }


# Q20 — BROWSE MOVIES (combined)
@app.get("/movies/browse")
def browse_movies(
    keyword: Optional[str] = Query(default=None),
    genre: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default=None),
    sort_by: str = Query(default="ticket_price"),
    order: str = Query(default="asc"),
    page: int = Query(default=1),
    limit: int = Query(default=3)
):
    valid_sort_fields = ["ticket_price", "title", "duration_mins", "seats_available"]
    valid_orders = ["asc", "desc"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sort_fields}")
    if order not in valid_orders:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    result = movies[:]

    # Step 1: keyword filter
    if keyword is not None:
        kw = keyword.lower()
        result = [m for m in result if kw in m["title"].lower() or kw in m["genre"].lower() or kw in m["language"].lower()]

    # Step 2: genre / language filter
    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]

    # Step 3: sort
    result = sorted(result, key=lambda m: m[sort_by], reverse=(order == "desc"))

    # Step 4: paginate
    total = len(result)
    total_pages = math.ceil(total / limit) if limit else 1
    start = (page - 1) * limit
    end = start + limit

    return {
        "keyword": keyword,
        "genre": genre,
        "language": language,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "movies": result[start:end]
    }


# Q3 — GET MOVIE BY ID  (variable route — must be BELOW all fixed /movies/xxx routes)
@app.get("/movies/{movie_id}")
def get_movie_by_id(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    return movie


# ─────────────────────────────────────────────
# Q4 — GET ALL BOOKINGS  (fixed routes first)
# ─────────────────────────────────────────────

@app.get("/bookings")
def get_all_bookings():
    total_revenue = sum(b["total_cost"] for b in bookings)
    return {
        "total": len(bookings),
        "total_revenue": round(total_revenue, 2),
        "bookings": bookings
    }


# Q19 — BOOKINGS SEARCH / SORT / PAGE  (fixed routes above variable)
@app.get("/bookings/search")
def search_bookings(customer_name: str = Query(...)):
    result = [b for b in bookings if customer_name.lower() in b["customer_name"].lower()]
    if not result:
        return {"message": f"No bookings found for '{customer_name}'", "total_found": 0}
    return {"total_found": len(result), "bookings": result}


@app.get("/bookings/sort")
def sort_bookings(
    sort_by: str = Query(default="total_cost"),
    order: str = Query(default="asc")
):
    valid_fields = ["total_cost", "seats"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    sorted_bookings = sorted(bookings, key=lambda b: b[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "total": len(sorted_bookings), "bookings": sorted_bookings}


@app.get("/bookings/page")
def paginate_bookings(page: int = Query(default=1), limit: int = Query(default=3)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page and limit must be >= 1")
    total = len(bookings)
    total_pages = math.ceil(total / limit) if total else 1
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page, "limit": limit,
        "total": total, "total_pages": total_pages,
        "bookings": bookings[start:end]
    }


# ─────────────────────────────────────────────
# Q8 — POST BOOKING
# ─────────────────────────────────────────────

@app.post("/bookings", status_code=201)
def create_booking(request: BookingRequest):
    global booking_counter
    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {request.movie_id} not found")
    if movie["seats_available"] < request.seats:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough seats. Available: {movie['seats_available']}, Requested: {request.seats}"
        )
    valid_seat_types = ["standard", "premium", "recliner"]
    if request.seat_type.lower() not in valid_seat_types:
        raise HTTPException(status_code=400, detail=f"seat_type must be one of {valid_seat_types}")

    cost_info = calculate_ticket_cost(movie["ticket_price"], request.seats, request.seat_type, request.promo_code)
    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "phone": request.phone,
        "movie_id": movie["id"],
        "movie_title": movie["title"],
        "seats": request.seats,
        "seat_type": request.seat_type,
        "promo_code": request.promo_code,
        "original_cost": cost_info["original_cost"],
        "total_cost": cost_info["discounted_cost"],
        "discount_applied": cost_info["discount_applied"],
        "status": "confirmed"
    }
    bookings.append(booking)
    booking_counter += 1
    return {"message": "Booking confirmed!", "booking": booking}


# ─────────────────────────────────────────────
# Q11 — POST NEW MOVIE
# ─────────────────────────────────────────────

@app.post("/movies", status_code=201)
def add_movie(new_movie: NewMovie):
    global movie_counter
    for m in movies:
        if m["title"].lower() == new_movie.title.lower():
            raise HTTPException(status_code=400, detail=f"Movie '{new_movie.title}' already exists")
    movie = {
        "id": movie_counter,
        "title": new_movie.title,
        "genre": new_movie.genre,
        "language": new_movie.language,
        "duration_mins": new_movie.duration_mins,
        "ticket_price": new_movie.ticket_price,
        "seats_available": new_movie.seats_available
    }
    movies.append(movie)
    movie_counter += 1
    return {"message": "Movie added successfully", "movie": movie}


# Q12 — UPDATE MOVIE
@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    ticket_price: Optional[int] = Query(default=None),
    seats_available: Optional[int] = Query(default=None)
):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    if ticket_price is not None:
        movie["ticket_price"] = ticket_price
    if seats_available is not None:
        movie["seats_available"] = seats_available
    return {"message": "Movie updated", "movie": movie}


# Q13 — DELETE MOVIE
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    movie_bookings = [b for b in bookings if b["movie_id"] == movie_id]
    if movie_bookings:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete '{movie['title']}' — it has {len(movie_bookings)} existing booking(s)"
        )
    movies.remove(movie)
    return {"message": f"Movie '{movie['title']}' deleted successfully"}


# ─────────────────────────────────────────────
# Q14 — SEAT HOLD SYSTEM
# ─────────────────────────────────────────────

@app.get("/seat-hold")
def get_all_holds():
    return {"total": len(holds), "holds": holds}


@app.post("/seat-hold", status_code=201)
def create_seat_hold(request: SeatHoldRequest):
    global hold_counter
    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {request.movie_id} not found")
    if movie["seats_available"] < request.seats:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough seats to hold. Available: {movie['seats_available']}"
        )
    movie["seats_available"] -= request.seats
    hold = {
        "hold_id": hold_counter,
        "customer_name": request.customer_name,
        "movie_id": movie["id"],
        "movie_title": movie["title"],
        "seats": request.seats,
        "status": "on_hold"
    }
    holds.append(hold)
    hold_counter += 1
    return {"message": "Seats held successfully", "hold": hold}


# ─────────────────────────────────────────────
# Q15 — CONFIRM HOLD / RELEASE HOLD
# ─────────────────────────────────────────────

@app.post("/seat-confirm/{hold_id}", status_code=201)
def confirm_seat_hold(hold_id: int):
    global booking_counter
    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        raise HTTPException(status_code=404, detail=f"Hold with id {hold_id} not found")

    movie = find_movie(hold["movie_id"])
    # Calculate cost at standard price (no promo on hold-confirm)
    cost_info = calculate_ticket_cost(movie["ticket_price"], hold["seats"], "standard")

    booking = {
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "movie_id": hold["movie_id"],
        "movie_title": hold["movie_title"],
        "seats": hold["seats"],
        "seat_type": "standard",
        "promo_code": "",
        "original_cost": cost_info["original_cost"],
        "total_cost": cost_info["discounted_cost"],
        "discount_applied": cost_info["discount_applied"],
        "status": "confirmed",
        "converted_from_hold": hold_id
    }
    bookings.append(booking)
    booking_counter += 1
    holds.remove(hold)
    return {"message": "Hold confirmed and converted to booking!", "booking": booking}


@app.delete("/seat-release/{hold_id}")
def release_seat_hold(hold_id: int):
    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        raise HTTPException(status_code=404, detail=f"Hold with id {hold_id} not found")
    movie = find_movie(hold["movie_id"])
    if movie:
        movie["seats_available"] += hold["seats"]
    holds.remove(hold)
    return {"message": f"Hold {hold_id} released. {hold['seats']} seat(s) returned to '{hold['movie_title']}'"}
