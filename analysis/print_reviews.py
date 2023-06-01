from db.movie_crud import get_reviews

reviews = get_reviews()

for i, review in enumerate(reviews):
    print("=" * 50)
    print(f"{i+1}.")
    print(f"title: {review[0]}")
    print(f"review: {review[1]}")
    print(f"score: {review[2]}")
print("=" * 50)
print(f"= {len(reviews)}건 리뷰 조회 완료")
print("=" * 50)
